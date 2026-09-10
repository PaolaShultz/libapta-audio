// SPDX-License-Identifier: Apache-2.0
/* Synthetic diagnostic only; no algorithm changes or corpus accuracy claim. */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "apta_key_internal.h"

#if defined(APTA_KEY_EXTRACTION_REFERENCE) && defined(APTA_INTERNAL_KEY_MEAN_NORMALIZED)
#error "The frozen extraction reference does not support mean normalization"
#endif

#if defined(APTA_INTERNAL_KEY_CENTERED_CORRELATION) || defined(APTA_INTERNAL_KEY_HPCP) || \
    defined(APTA_INTERNAL_KEY_TEMPORAL_CHORD) || defined(APTA_INTERNAL_KEY_TEMPORAL_PROFILE)
#error "This frozen diagnostic supports only default and semitone-band builds"
#endif

#define RATE 48000u
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "diagnostic check failed: %s:%d: %s\n", \
    __FILE__, __LINE__, #x); return 1; } } while (0)

/* Independent reference copies pinned to the baseline; not selector weights. */
static const float profiles[2][12] = {
    {0.748f,0.060f,0.488f,0.082f,0.674f,0.460f,0.096f,0.715f,0.104f,0.366f,0.057f,0.400f},
    {0.712f,0.084f,0.455f,0.270f,0.360f,0.320f,0.082f,0.600f,0.059f,0.291f,0.092f,0.260f}
};
static int emit_json;
static unsigned rows;
#ifdef APTA_KEY_COVERAGE_DIAGNOSTIC
#define PCM_CONDITIONS 6u
#include "key_coverage_export.h"
#else
#define PCM_CONDITIONS 3u
#endif

#ifdef APTA_KEY_GAIN_DIAGNOSTIC
static int gain_shift;
static float scaled_sample_peak;
static uint64_t gain_reversal_exact_samples;
#endif

static unsigned mode_index(apta_key_mode_t mode)
{
    return mode == APTA_KEY_MODE_MAJOR ? 0u : 1u;
}

#ifdef APTA_KEY_EXTRACTION_REFERENCE
#include "key_extraction_reference.h"
#endif

#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
#include "key_contrast_trace.h"
#endif

static double cosine(const float *chroma, unsigned tonic, unsigned mode)
{
    double dot = 0.0, cn = 0.0, pn = 0.0;
    unsigned p;
    for (p = 0; p < 12; ++p) {
        double a = chroma[p], b = profiles[mode][(p + 12u - tonic) % 12u];
        dot += a * b; cn += a * a; pn += b * b;
    }
    return cn > 0.0 ? dot / sqrt(cn * pn) : 0.0;
}

static int measure(const char *kind, unsigned condition, unsigned tonic, unsigned mode,
                   unsigned window, const float *chroma, unsigned completed,
                   int require_identity)
{
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT];
    apta_key_view_t view;
    double scores[24], maximum = -1.0;
    unsigned p, i;
    for (p = 0; p < 12; ++p) CHECK(isfinite(chroma[p]) && chroma[p] >= 0.0f);
    CHECK(apta_internal_key_select_chroma(chroma, completed, candidates, &view) == APTA_STATUS_OK);
    CHECK(view.mode == APTA_KEY_MODE_MAJOR || view.mode == APTA_KEY_MODE_MINOR);
    CHECK(view.tonic < 12u && view.candidate_count == 3u);
    for (i = 0; i < 24; ++i) {
        scores[i] = cosine(chroma, i % 12u, i / 12u);
        if (scores[i] > maximum) maximum = scores[i];
    }
    /* Compare all native top-three against independent remaining maxima.
     * Encoded score tie adjustment can subtract up to two uint16 LSBs. */
    for (i = 0; i < 3; ++i) {
        unsigned j, selected;
        double remaining = -1.0;
        CHECK(candidates[i].tonic < 12u);
        CHECK(candidates[i].mode == APTA_KEY_MODE_MAJOR || candidates[i].mode == APTA_KEY_MODE_MINOR);
        selected = mode_index(candidates[i].mode) * 12u + candidates[i].tonic;
        for (j = 0; j < 24; ++j) {
            unsigned k; int used = 0;
            for (k = 0; k < i; ++k)
                if (j == mode_index(candidates[k].mode) * 12u + candidates[k].tonic) used = 1;
            if (!used && scores[j] > remaining) remaining = scores[j];
        }
        for (j = 0; j < i; ++j)
            CHECK(selected != mode_index(candidates[j].mode) * 12u + candidates[j].tonic);
        CHECK(fabs(scores[selected] - remaining) <= 2e-6);
        CHECK(fabs((double)candidates[i].score / 65535.0 - scores[selected]) < 5e-5);
        if (i > 0) CHECK(candidates[i].score < candidates[i-1].score);
    }
    CHECK(fabs(scores[mode_index(view.mode) * 12u + view.tonic] - maximum) <= 2e-6);
    if (require_identity) CHECK(view.tonic == tonic && mode_index(view.mode) == mode);
    if (emit_json) {
        printf("%s{\"kind\":\"%s\",\"condition\":%u,\"stimulus_tonic\":%u,"
               "\"stimulus_mode\":%u,\"window\":%u,\"completed_windows\":%u,"
               "\"selected_tonic\":%u,\"selected_mode\":%u,\"confidence\":%u,\"chroma\":[",
               rows ? ",\n" : "", kind, condition, tonic, mode, window, completed,
               (unsigned)view.tonic, mode_index(view.mode), (unsigned)view.confidence);
        for (p = 0; p < 12; ++p) printf("%s%.9g", p ? "," : "", (double)chroma[p]);
        printf("],\"reference_scores_major_then_minor\":[");
        for (p = 0; p < 24; ++p) printf("%s%.17g", p ? "," : "", scores[p]);
        printf("],\"native_candidates\":[");
        for (p = 0; p < 3; ++p)
            printf("%s{\"tonic\":%u,\"mode\":%u,\"score\":%u}", p ? "," : "",
                   (unsigned)candidates[p].tonic, mode_index(candidates[p].mode),
                   (unsigned)candidates[p].score);
        printf("]");
#ifdef APTA_KEY_EXTRACTION_REFERENCE
        CHECK(reference_print(kind, chroma, completed) == 0);
#endif
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
        if (strcmp(kind, "pcm_cumulative") == 0) contrast_print();
#endif
        printf("}");
    }
    ++rows;
    return 0;
}

static int vectors(void)
{
    static const float floors[3] = {0.0f, 1.0f, 4.0f};
    unsigned mode, tonic, condition, p, kind;
    float chroma[12] = {0};
    apta_key_candidate_t candidates[3];
    apta_key_view_t view;
    CHECK(apta_internal_key_select_chroma(chroma, 8u, candidates, &view) == APTA_STATUS_NOT_AVAILABLE);
    chroma[0] = -1.0f;
    CHECK(apta_internal_key_select_chroma(chroma, 8u, candidates, &view) == APTA_ERROR_INVALID_ARGUMENT);
    chroma[0] = NAN;
    CHECK(apta_internal_key_select_chroma(chroma, 8u, candidates, &view) == APTA_ERROR_INVALID_ARGUMENT);
    chroma[0] = INFINITY;
    CHECK(apta_internal_key_select_chroma(chroma, 8u, candidates, &view) == APTA_ERROR_INVALID_ARGUMENT);
    for (kind = 0; kind < 2; ++kind) for (mode = 0; mode < 2; ++mode)
        for (tonic = 0; tonic < 12; ++tonic) for (condition = 0; condition < 3; ++condition) {
            for (p = 0; p < 12; ++p) chroma[p] = floors[condition] +
                (kind == 0 ? profiles[mode][(p + 12u - tonic) % 12u] : 0.0f);
            if (kind == 1) {
                chroma[tonic] += 1.0f;
                chroma[(tonic + (mode ? 3u : 4u)) % 12u] += 1.0f;
                chroma[(tonic + 7u) % 12u] += 1.0f;
            }
            CHECK(measure(kind ? "triad" : "profile", condition, tonic, mode, 0u,
                          chroma, 8u, kind == 0 && condition == 0) == 0);
        }
    return 0;
}

static int pcm(void)
{
    unsigned mode, tonic, condition, window, p;
    for (mode = 0; mode < 2; ++mode) for (tonic = 0; tonic < 12; ++tonic)
        for (condition = 0; condition < PCM_CONDITIONS; ++condition) {
            apta_session_t session;
            float previous[12] = {0}, delta[12];
            uint32_t random = 0x243f6a88u;
            memset(&session, 0, sizeof(session));
            session.config.source_sample_rate = RATE;
            session.config.requested_features = APTA_FEATURE_MUSICAL_KEY;
#ifdef APTA_KEY_EXTRACTION_REFERENCE
            reference_reset();
#endif
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
            contrast_reset();
#endif
            for (window = 0; window < 4; ++window) {
                static const unsigned degrees[4] = {0u, 5u, 7u, 0u};
                unsigned root = 48u + tonic + degrees[window];
                unsigned third = (window == 2 || mode == 0) ? 4u : 3u;
                unsigned notes[3] = {root, root + third, root + 7u};
                double frequencies[3];
                uint32_t frame;
                for (p = 0; p < 3; ++p)
                    frequencies[p] = 440.0 * pow(2.0, ((double)notes[p] - 69.0 +
                        (condition == 1 ? 1.0 / 3.0 :
#ifdef APTA_KEY_COVERAGE_DIAGNOSTIC
                         condition == 3 ? -1.0 / 3.0 :
#endif
                         0.0)) / 12.0);
                for (frame = 0; frame < RATE; ++frame) {
                    uint64_t absolute = (uint64_t)window * RATE + frame;
                    double sample = 0.0;
                    for (p = 0; p < 3; ++p)
                        sample += 0.15 * sin(6.2831853071795864769 * frequencies[p] * (double)absolute / RATE);
#ifdef APTA_KEY_COVERAGE_DIAGNOSTIC
                    if (condition == 5) sample = 0.0;
                    if (condition >= 4) {
                        unsigned harmonic;
                        for (p = 0; p < 3; ++p) for (harmonic = 2; harmonic <= 4; ++harmonic)
                            sample += (0.15 / harmonic) * sin(6.2831853071795864769 *
                                frequencies[p] * harmonic * (double)absolute / RATE);
                    }
#endif
                    if (condition == 2) {
                        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
                        sample += 0.02 * (2.0 * (double)random / 4294967295.0 - 1.0);
                    }
#ifdef APTA_KEY_GAIN_DIAGNOSTIC
                    {
                        const float original = (float)sample;
                        const float scaled = ldexpf(original, gain_shift);
                        CHECK(isfinite(scaled) && fabsf(scaled) <= 1.0f);
                        CHECK(ldexpf(scaled, -gain_shift) == original);
                        if (fabsf(scaled) > scaled_sample_peak) scaled_sample_peak = fabsf(scaled);
                        ++gain_reversal_exact_samples;
                        apta_internal_key_feed_sample(&session, scaled, absolute);
                    }
#else
#ifdef APTA_KEY_COVERAGE_DIAGNOSTIC
                    CHECK(coverage_feed(&session, (float)sample) == 0);
#endif
                    apta_internal_key_feed_sample(&session, (float)sample, absolute);
#endif
#ifdef APTA_KEY_EXTRACTION_REFERENCE
                    CHECK(reference_feed(&session, (float)sample) == 0);
#endif
                }
                CHECK(session.key_analysis.completed_windows == window + 1u);
#ifdef APTA_KEY_COVERAGE_DIAGNOSTIC
                CHECK(coverage_write(&session, tonic, mode, condition, window + 1u) == 0);
#endif
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
                CHECK(contrast_finish(session.key_analysis.chroma[APTA_INTERNAL_KEY_BASE_VARIANT]) == 0);
#endif
                for (p = 0; p < 12; ++p) {
                    float current = session.key_analysis.chroma[APTA_INTERNAL_KEY_BASE_VARIANT][p];
                    delta[p] = current - previous[p];
                    previous[p] = current;
                }
                CHECK(measure("pcm_window", condition, tonic, mode, window + 1u, delta, 1u, 0) == 0);
                CHECK(measure("pcm_cumulative", condition, tonic, mode, window + 1u,
                              previous, window + 1u, 0) == 0);
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
                contrast_next_window();
#endif
            }
        }
    return 0;
}

int main(int argc, char **argv)
{
#if defined(APTA_KEY_COVERAGE_DIAGNOSTIC)
    if (argc != 4 || strcmp(argv[1], "--json") || strcmp(argv[2], "--samples")) return 2;
    CHECK(coverage_open(argv[3]) == 0);
    emit_json = 1;
#elif defined(APTA_KEY_GAIN_DIAGNOSTIC)
    if (argc != 4 || strcmp(argv[1], "--json") != 0 || strcmp(argv[2], "--gain-shift") != 0 ||
        (strcmp(argv[3], "-4") != 0 && strcmp(argv[3], "-2") != 0 &&
         strcmp(argv[3], "0") != 0 && strcmp(argv[3], "1") != 0)) {
        fputs("usage: apta_key_gain_diagnostic --json --gain-shift {-4|-2|0|1}\n", stderr);
        return 2;
    }
    gain_shift = atoi(argv[3]);
    emit_json = 1;
#else
    if (argc > 2 || (argc == 2 && strcmp(argv[1], "--json") != 0)) {
        fputs("usage: apta_key_mode_diagnostic [--json]\n", stderr); return 2;
    }
    emit_json = argc == 2;
#endif
#if defined(APTA_KEY_COVERAGE_DIAGNOSTIC)
#define DIAGNOSTIC_FORMAT "apta-key-coverage-diagnostic-1"
#elif defined(APTA_KEY_EXTRACTION_REFERENCE)
    CHECK(reference_selftest() == 0);
#define DIAGNOSTIC_FORMAT "apta-key-extraction-reference-1"
#elif defined(APTA_KEY_GAIN_DIAGNOSTIC) && defined(APTA_INTERNAL_KEY_MEAN_NORMALIZED)
#define DIAGNOSTIC_FORMAT "apta-key-mean-normalized-gain-1"
#elif defined(APTA_INTERNAL_KEY_MEAN_NORMALIZED)
#define DIAGNOSTIC_FORMAT "apta-key-mean-normalized-diagnostic-1"
#elif defined(APTA_KEY_GAIN_DIAGNOSTIC)
#define DIAGNOSTIC_FORMAT "apta-key-gain-diagnostic-1"
#elif defined(APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC)
#define DIAGNOSTIC_FORMAT "apta-key-contrast-diagnostic-1"
#else
#define DIAGNOSTIC_FORMAT "apta-key-mode-diagnostic-1"
#endif
    if (emit_json) printf("{\"format\":\"" DIAGNOSTIC_FORMAT "\",\"acceptance_claim\":false,"
        "\"mode_encoding\":\"major=0,minor=1\",\"semitone_band\":%s,\"rows\":[\n",
#ifdef APTA_INTERNAL_KEY_SEMITONE_BAND
        "true"
#else
        "false"
#endif
    );
    CHECK(vectors() == 0);
    CHECK(pcm() == 0);
#ifdef APTA_KEY_COVERAGE_DIAGNOSTIC
    CHECK(rows == 1296u);
    CHECK(coverage_close() == 0);
#else
    CHECK(rows == 720u);
#endif
#ifdef APTA_KEY_GAIN_DIAGNOSTIC
    CHECK(gain_reversal_exact_samples == UINT64_C(13824000));
    if (emit_json) printf("\n],\"row_count\":%u,\"checks_passed\":true,"
                         "\"observer_scratch_bytes\":%lu,\"session_bytes\":%lu,"
                         "\"gain_shift\":%d,\"scaled_sample_peak\":%.9g,"
                         "\"gain_reversal_exact_samples\":%llu}\n",
                         rows, (unsigned long)sizeof(contrast), (unsigned long)sizeof(apta_session_t),
                         gain_shift, (double)scaled_sample_peak,
                         (unsigned long long)gain_reversal_exact_samples);
#elif defined(APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC)
    if (emit_json) printf("\n],\"row_count\":%u,\"checks_passed\":true,"
                         "\"observer_scratch_bytes\":%lu,\"session_bytes\":%lu}\n",
                         rows, (unsigned long)sizeof(contrast), (unsigned long)sizeof(apta_session_t));
#else
    if (emit_json) printf("\n],\"row_count\":%u,\"checks_passed\":true}\n", rows);
#endif
    CHECK(!ferror(stdout));
    return 0;
}
