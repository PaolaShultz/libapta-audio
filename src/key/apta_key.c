// SPDX-License-Identifier: Apache-2.0
#include "apta_key_internal.h"

#include <math.h>
#include <stdalign.h>
#include <string.h>

static const float apta_key_frequencies[APTA_INTERNAL_KEY_BIN_COUNT] = {
    130.8128f, 138.5913f, 146.8324f, 155.5635f, 164.8138f, 174.6141f,
    184.9972f, 195.9977f, 207.6523f, 220.0000f, 233.0819f, 246.9417f,
    261.6256f, 277.1826f, 293.6648f, 311.1270f, 329.6276f, 349.2282f,
    369.9944f, 391.9954f, 415.3047f, 440.0000f, 466.1638f, 493.8833f,
    523.2511f, 554.3653f, 587.3295f, 622.2540f, 659.2551f, 698.4565f,
    739.9888f, 783.9909f, 830.6094f, 880.0000f, 932.3275f, 987.7666f
};

/* Temperley/Kostka-Payne pitch-class profiles. Chosen over Krumhansl-Kessler
 * because the official corpus error taxonomy showed classic KK failure modes:
 * dominant-for-tonic (fifth) confusions and parallel-mode swaps on minor
 * material. KP weights de-emphasize the dominant relative to the tonic and
 * model the harmonic-minor leading tone explicitly. */
static const float apta_major_profile[APTA_INTERNAL_KEY_PITCH_CLASSES] = {
    0.748f, 0.060f, 0.488f, 0.082f, 0.674f, 0.460f,
    0.096f, 0.715f, 0.104f, 0.366f, 0.057f, 0.400f
};

static const float apta_minor_profile[APTA_INTERNAL_KEY_PITCH_CLASSES] = {
    0.712f, 0.084f, 0.455f, 0.270f, 0.360f, 0.320f,
    0.082f, 0.600f, 0.059f, 0.291f, 0.092f, 0.260f
};

#ifdef APTA_INTERNAL_KEY_TEMPORAL_CHORD
#define APTA_KEY_CHORD_FIFTH_WEIGHT 0.70f
#define APTA_KEY_CHORD_TEMPLATE_NORM_SQUARED 2.49f

static float apta_key_chord_score(
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES],
    float chroma_norm,
    uint32_t tonic,
    apta_key_mode_t mode)
{
    const uint32_t third =
        (tonic + (mode == APTA_KEY_MODE_MAJOR ? 4u : 3u)) %
        APTA_INTERNAL_KEY_PITCH_CLASSES;
    const uint32_t fifth = (tonic + 7u) % APTA_INTERNAL_KEY_PITCH_CLASSES;
    const float dot = chroma[tonic] + chroma[third] +
                      APTA_KEY_CHORD_FIFTH_WEIGHT * chroma[fifth];

    if (chroma_norm <= 1e-20f) {
        return 0.0f;
    }
    return dot / sqrtf(chroma_norm * APTA_KEY_CHORD_TEMPLATE_NORM_SQUARED);
}

static float apta_key_chord_compatibility(
    uint32_t key_tonic,
    apta_key_mode_t key_mode,
    uint32_t chord_tonic,
    apta_key_mode_t chord_mode)
{
    const uint32_t degree =
        (chord_tonic + APTA_INTERNAL_KEY_PITCH_CLASSES - key_tonic) %
        APTA_INTERNAL_KEY_PITCH_CLASSES;

    if (key_mode == APTA_KEY_MODE_MAJOR) {
        if (chord_mode == APTA_KEY_MODE_MAJOR) {
            if (degree == 0u) {
                return 1.00f;
            }
            if (degree == 7u) {
                return 0.85f;
            }
            if (degree == 5u) {
                return 0.70f;
            }
        } else {
            if (degree == 9u) {
                return 0.60f;
            }
            if (degree == 2u) {
                return 0.45f;
            }
            if (degree == 4u) {
                return 0.30f;
            }
        }
    } else if (chord_mode == APTA_KEY_MODE_MINOR) {
        if (degree == 0u) {
            return 1.00f;
        }
        if (degree == 5u) {
            return 0.70f;
        }
    } else {
        if (degree == 7u) {
            return 0.85f;
        }
        if (degree == 3u) {
            return 0.60f;
        }
        if (degree == 8u) {
            return 0.45f;
        }
        if (degree == 10u) {
            return 0.30f;
        }
    }
    return 0.0f;
}

void apta_internal_key_temporal_vote_chroma(
    apta_internal_key_analysis_t *analysis,
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES])
{
    float chroma_norm = 0.0f;
    float best_score = -1.0f;
    float second_score = -1.0f;
    uint32_t best_tonic = 0u;
    apta_key_mode_t best_mode = APTA_KEY_MODE_MAJOR;
    uint32_t tonic;
    uint32_t pitch;

    if (analysis == NULL || chroma == NULL) {
        return;
    }
    for (pitch = 0u; pitch < APTA_INTERNAL_KEY_PITCH_CLASSES; ++pitch) {
        if (!isfinite(chroma[pitch]) || chroma[pitch] < 0.0f) {
            return;
        }
        chroma_norm += chroma[pitch] * chroma[pitch];
    }
    if (chroma_norm <= 1e-20f) {
        return;
    }
    for (tonic = 0u; tonic < APTA_INTERNAL_KEY_PITCH_CLASSES; ++tonic) {
        const apta_key_mode_t modes[2] = {
            APTA_KEY_MODE_MAJOR, APTA_KEY_MODE_MINOR};
        uint32_t mode_index;

        for (mode_index = 0u; mode_index < 2u; ++mode_index) {
            const float score = apta_key_chord_score(
                chroma, chroma_norm, tonic, modes[mode_index]);
            if (score > best_score) {
                second_score = best_score;
                best_score = score;
                best_tonic = tonic;
                best_mode = modes[mode_index];
            } else if (score > second_score) {
                second_score = score;
            }
        }
    }
    if (best_score > second_score) {
        const float margin = best_score - second_score;
        uint32_t key_tonic;

        for (key_tonic = 0u;
             key_tonic < APTA_INTERNAL_KEY_PITCH_CLASSES;
             ++key_tonic) {
            const float major_weight = apta_key_chord_compatibility(
                key_tonic,
                APTA_KEY_MODE_MAJOR,
                best_tonic,
                best_mode);
            const float minor_weight = apta_key_chord_compatibility(
                key_tonic,
                APTA_KEY_MODE_MINOR,
                best_tonic,
                best_mode);
            analysis->temporal_key_support[key_tonic] += margin * major_weight;
            analysis->temporal_key_support[
                APTA_INTERNAL_KEY_PITCH_CLASSES + key_tonic] +=
                margin * minor_weight;
        }
        analysis->temporal_margin_sum += margin;
    }
}
#endif

#ifdef APTA_INTERNAL_KEY_HPCP
#define APTA_KEY_HPCP_THIRD_HARMONIC_OFFSET 19u
#define APTA_KEY_HPCP_FIFTH_HARMONIC_OFFSET 28u
#define APTA_KEY_HPCP_THIRD_HARMONIC_WEIGHT 0.10f
#define APTA_KEY_HPCP_FIFTH_HARMONIC_WEIGHT 0.20f

void apta_internal_key_harmonic_chroma(
    const float spectral_profile[APTA_INTERNAL_KEY_BIN_COUNT],
    float chroma_out[APTA_INTERNAL_KEY_PITCH_CLASSES])
{
    uint32_t fundamental;

    if (spectral_profile == NULL || chroma_out == NULL) {
        return;
    }
    memset(
        chroma_out,
        0,
        sizeof(*chroma_out) * APTA_INTERNAL_KEY_PITCH_CLASSES);
    for (fundamental = 0u;
         fundamental < APTA_INTERNAL_KEY_BIN_COUNT;
         ++fundamental) {
        float salience = spectral_profile[fundamental];
        float available_weight = 1.0f;

        if (fundamental + APTA_KEY_HPCP_THIRD_HARMONIC_OFFSET <
            APTA_INTERNAL_KEY_BIN_COUNT) {
            salience += APTA_KEY_HPCP_THIRD_HARMONIC_WEIGHT *
                        spectral_profile[
                            fundamental +
                            APTA_KEY_HPCP_THIRD_HARMONIC_OFFSET];
            available_weight += APTA_KEY_HPCP_THIRD_HARMONIC_WEIGHT;
        }
        if (fundamental + APTA_KEY_HPCP_FIFTH_HARMONIC_OFFSET <
            APTA_INTERNAL_KEY_BIN_COUNT) {
            salience += APTA_KEY_HPCP_FIFTH_HARMONIC_WEIGHT *
                        spectral_profile[
                            fundamental +
                            APTA_KEY_HPCP_FIFTH_HARMONIC_OFFSET];
            available_weight += APTA_KEY_HPCP_FIFTH_HARMONIC_WEIGHT;
        }
        chroma_out[fundamental % APTA_INTERNAL_KEY_PITCH_CLASSES] +=
            salience / available_weight;
    }
}
#endif

#ifdef APTA_INTERNAL_KEY_TRACE
void apta_internal_key_trace_get(
    const apta_session_t *session,
    const float **spectral_profile_out,
    uint32_t *bin_count_out,
    const float **chroma_out,
    uint32_t *completed_windows_out)
{
    if (spectral_profile_out != NULL) {
        *spectral_profile_out =
            session != NULL
                ? session->key_analysis.spectral_profile
                      [APTA_INTERNAL_KEY_BASE_VARIANT]
                : NULL;
    }
    if (bin_count_out != NULL) {
        *bin_count_out = session != NULL ? APTA_INTERNAL_KEY_BIN_COUNT : 0u;
    }
    if (chroma_out != NULL) {
        *chroma_out =
            session != NULL
                ? session->key_analysis.chroma[APTA_INTERNAL_KEY_BASE_VARIANT]
                : NULL;
    }
    if (completed_windows_out != NULL) {
        *completed_windows_out =
            session != NULL ? session->key_analysis.completed_windows : 0u;
    }
}
#endif

static float apta_key_profile_score(
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES],
    uint32_t tonic,
    const float profile[APTA_INTERNAL_KEY_PITCH_CLASSES])
{
    float dot = 0.0f;
    float chroma_norm = 0.0f;
    float profile_norm = 0.0f;
#ifdef APTA_INTERNAL_KEY_CENTERED_CORRELATION
    float chroma_mean = 0.0f;
    float profile_mean = 0.0f;
#endif
    uint32_t pitch;

#ifdef APTA_INTERNAL_KEY_CENTERED_CORRELATION
    for (pitch = 0u; pitch < APTA_INTERNAL_KEY_PITCH_CLASSES; ++pitch) {
        const uint32_t rotated =
            (pitch + APTA_INTERNAL_KEY_PITCH_CLASSES - tonic) %
            APTA_INTERNAL_KEY_PITCH_CLASSES;
        chroma_mean += chroma[pitch];
        profile_mean += profile[rotated];
    }
    chroma_mean /= (float)APTA_INTERNAL_KEY_PITCH_CLASSES;
    profile_mean /= (float)APTA_INTERNAL_KEY_PITCH_CLASSES;
#endif
    for (pitch = 0u; pitch < APTA_INTERNAL_KEY_PITCH_CLASSES; ++pitch) {
        const uint32_t rotated =
            (pitch + APTA_INTERNAL_KEY_PITCH_CLASSES - tonic) %
            APTA_INTERNAL_KEY_PITCH_CLASSES;
#ifdef APTA_INTERNAL_KEY_CENTERED_CORRELATION
        const float centered_chroma = chroma[pitch] - chroma_mean;
        const float centered_profile = profile[rotated] - profile_mean;
        dot += centered_chroma * centered_profile;
        chroma_norm += centered_chroma * centered_chroma;
        profile_norm += centered_profile * centered_profile;
#else
        dot += chroma[pitch] * profile[rotated];
        chroma_norm += chroma[pitch] * chroma[pitch];
        profile_norm += profile[rotated] * profile[rotated];
#endif
    }
    if (chroma_norm <= 1e-20f || profile_norm <= 1e-20f) {
        return 0.0f;
    }
    return dot / sqrtf(chroma_norm * profile_norm);
}

#ifdef APTA_INTERNAL_KEY_TEMPORAL_PROFILE
void apta_internal_key_temporal_profile_add_chroma(
    apta_internal_key_analysis_t *analysis,
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES])
{
    float scores[APTA_INTERNAL_KEY_GLOBAL_STATES];
    float floor = 1.0f;
    float evidence_sum = 0.0f;
    uint32_t tonic;
    uint32_t pitch;
    uint32_t state;

    if (analysis == NULL || chroma == NULL ||
        analysis->temporal_profile_windows == UINT32_MAX) {
        return;
    }
    for (pitch = 0u; pitch < APTA_INTERNAL_KEY_PITCH_CLASSES; ++pitch) {
        if (!isfinite(chroma[pitch]) || chroma[pitch] < 0.0f) {
            return;
        }
    }
    for (tonic = 0u; tonic < APTA_INTERNAL_KEY_PITCH_CLASSES; ++tonic) {
        const float major_score =
            apta_key_profile_score(chroma, tonic, apta_major_profile);
        const float minor_score =
            apta_key_profile_score(chroma, tonic, apta_minor_profile);
        scores[tonic] = major_score;
        scores[APTA_INTERNAL_KEY_PITCH_CLASSES + tonic] = minor_score;
        if (major_score < floor) {
            floor = major_score;
        }
        if (minor_score < floor) {
            floor = minor_score;
        }
    }
    for (state = 0u; state < APTA_INTERNAL_KEY_GLOBAL_STATES; ++state) {
        scores[state] = fmaxf(0.0f, scores[state] - floor);
        evidence_sum += scores[state];
    }
    if (!isfinite(evidence_sum) || evidence_sum <= 1e-20f) {
        return;
    }
    for (state = 0u; state < APTA_INTERNAL_KEY_GLOBAL_STATES; ++state) {
        analysis->temporal_profile_support[state] +=
            scores[state] / evidence_sum;
    }
    analysis->temporal_profile_windows += 1u;
}
#endif

static void apta_key_insert_candidate(
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    float scores[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    uint8_t tonic,
    apta_key_mode_t mode,
    float score)
{
    uint32_t position;
    uint32_t move;

    for (position = 0u; position < APTA_INTERNAL_KEY_CANDIDATE_COUNT; ++position) {
        if (score > scores[position]) {
            break;
        }
    }
    if (position == APTA_INTERNAL_KEY_CANDIDATE_COUNT) {
        return;
    }
    for (move = APTA_INTERNAL_KEY_CANDIDATE_COUNT - 1u;
         move > position;
         --move) {
        scores[move] = scores[move - 1u];
        candidates[move] = candidates[move - 1u];
    }
    memset(&candidates[position], 0, sizeof(candidates[position]));
    candidates[position].tonic = tonic;
    candidates[position].mode = mode;
    candidates[position].tuning_offset_cents = 0;
    candidates[position].score = (uint16_t)fminf(
        65535.0f,
        fmaxf(0.0f, score * 65535.0f + 0.5f));
    scores[position] = score;
}

#ifdef APTA_INTERNAL_KEY_TEMPORAL_CHORD
apta_status_t apta_internal_key_select_temporal(
    const apta_internal_key_analysis_t *analysis,
    uint32_t completed_windows,
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    apta_key_view_t *view_out)
{
    float scores[APTA_INTERNAL_KEY_CANDIDATE_COUNT] = {-1.0f, -1.0f, -1.0f};
    float separation;
    uint32_t tonic;
    uint32_t position;
    uint32_t confidence;

    if (analysis == NULL || candidates == NULL || view_out == NULL) {
        return APTA_ERROR_INVALID_ARGUMENT;
    }
    if (completed_windows == 0u ||
        !isfinite(analysis->temporal_margin_sum) ||
        analysis->temporal_margin_sum <= 1e-20f) {
        return APTA_STATUS_NOT_AVAILABLE;
    }
    memset(
        candidates,
        0,
        sizeof(*candidates) * APTA_INTERNAL_KEY_CANDIDATE_COUNT);
    for (tonic = 0u; tonic < APTA_INTERNAL_KEY_PITCH_CLASSES; ++tonic) {
        const float major_score =
            analysis->temporal_key_support[tonic] /
            analysis->temporal_margin_sum;
        const float minor_score =
            analysis->temporal_key_support[
                APTA_INTERNAL_KEY_PITCH_CLASSES + tonic] /
            analysis->temporal_margin_sum;
        if (!isfinite(major_score) || !isfinite(minor_score) ||
            major_score < 0.0f || minor_score < 0.0f) {
            return APTA_ERROR_INVALID_ARGUMENT;
        }
        apta_key_insert_candidate(
            candidates,
            scores,
            (uint8_t)tonic,
            APTA_KEY_MODE_MAJOR,
            major_score);
        apta_key_insert_candidate(
            candidates,
            scores,
            (uint8_t)tonic,
            APTA_KEY_MODE_MINOR,
            minor_score);
    }
    for (position = 1u;
         position < APTA_INTERNAL_KEY_CANDIDATE_COUNT;
         ++position) {
        if (candidates[position].score >= candidates[position - 1u].score) {
            candidates[position].score =
                candidates[position - 1u].score > 0u
                    ? (uint16_t)(candidates[position - 1u].score - 1u)
                    : 0u;
        }
    }
    separation = scores[0] > scores[1] ? scores[0] - scores[1] : 0.0f;
    confidence = 25u +
                 (completed_windows >= 8u ? 40u : completed_windows * 5u) +
                 (uint32_t)fminf(35.0f, separation * 350.0f + 0.5f);
    if (confidence > APTA_CONFIDENCE_MAX) {
        confidence = APTA_CONFIDENCE_MAX;
    }
    candidates[0].confidence = (apta_confidence_value_t)confidence;
    candidates[1].confidence = confidence > 10u
                                   ? (apta_confidence_value_t)(confidence - 10u)
                                   : 0u;
    candidates[2].confidence = confidence > 20u
                                   ? (apta_confidence_value_t)(confidence - 20u)
                                   : 0u;
    apta_key_view_init(view_out);
    view_out->mode = candidates[0].mode;
    view_out->tonic = candidates[0].tonic;
    view_out->tuning_offset_cents = 0;
    view_out->confidence = candidates[0].confidence;
    view_out->state = completed_windows >= APTA_INTERNAL_KEY_STABLE_WINDOWS
                          ? APTA_FEATURE_STABLE
                          : APTA_FEATURE_PROVISIONAL;
    view_out->candidate_count = APTA_INTERNAL_KEY_CANDIDATE_COUNT;
    view_out->candidates = candidates;
    return APTA_STATUS_OK;
}
#endif

#ifdef APTA_INTERNAL_KEY_TEMPORAL_PROFILE
apta_status_t apta_internal_key_select_temporal_profile(
    const apta_internal_key_analysis_t *analysis,
    uint32_t completed_windows,
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    apta_key_view_t *view_out)
{
    float scores[APTA_INTERNAL_KEY_CANDIDATE_COUNT] = {-1.0f, -1.0f, -1.0f};
    float separation;
    uint32_t tonic;
    uint32_t position;
    uint32_t confidence;

    if (analysis == NULL || candidates == NULL || view_out == NULL) {
        return APTA_ERROR_INVALID_ARGUMENT;
    }
    if (completed_windows == 0u || analysis->temporal_profile_windows == 0u) {
        return APTA_STATUS_NOT_AVAILABLE;
    }
    memset(
        candidates,
        0,
        sizeof(*candidates) * APTA_INTERNAL_KEY_CANDIDATE_COUNT);
    for (tonic = 0u; tonic < APTA_INTERNAL_KEY_PITCH_CLASSES; ++tonic) {
        const float divisor = (float)analysis->temporal_profile_windows;
        const float major_score =
            analysis->temporal_profile_support[tonic] / divisor;
        const float minor_score =
            analysis->temporal_profile_support[
                APTA_INTERNAL_KEY_PITCH_CLASSES + tonic] /
            divisor;
        if (!isfinite(major_score) || !isfinite(minor_score) ||
            major_score < 0.0f || minor_score < 0.0f) {
            return APTA_ERROR_INVALID_ARGUMENT;
        }
        apta_key_insert_candidate(
            candidates,
            scores,
            (uint8_t)tonic,
            APTA_KEY_MODE_MAJOR,
            major_score);
        apta_key_insert_candidate(
            candidates,
            scores,
            (uint8_t)tonic,
            APTA_KEY_MODE_MINOR,
            minor_score);
    }
    for (position = 1u;
         position < APTA_INTERNAL_KEY_CANDIDATE_COUNT;
         ++position) {
        if (candidates[position].score >= candidates[position - 1u].score) {
            candidates[position].score =
                candidates[position - 1u].score > 0u
                    ? (uint16_t)(candidates[position - 1u].score - 1u)
                    : 0u;
        }
    }
    separation = scores[0] > scores[1] ? scores[0] - scores[1] : 0.0f;
    confidence = 25u +
                 (completed_windows >= 8u ? 40u : completed_windows * 5u) +
                 (uint32_t)fminf(35.0f, separation * 350.0f + 0.5f);
    if (confidence > APTA_CONFIDENCE_MAX) {
        confidence = APTA_CONFIDENCE_MAX;
    }
    candidates[0].confidence = (apta_confidence_value_t)confidence;
    candidates[1].confidence = confidence > 10u
                                   ? (apta_confidence_value_t)(confidence - 10u)
                                   : 0u;
    candidates[2].confidence = confidence > 20u
                                   ? (apta_confidence_value_t)(confidence - 20u)
                                   : 0u;
    apta_key_view_init(view_out);
    view_out->mode = candidates[0].mode;
    view_out->tonic = candidates[0].tonic;
    view_out->tuning_offset_cents = 0;
    view_out->confidence = candidates[0].confidence;
    view_out->state = completed_windows >= APTA_INTERNAL_KEY_STABLE_WINDOWS
                          ? APTA_FEATURE_STABLE
                          : APTA_FEATURE_PROVISIONAL;
    view_out->candidate_count = APTA_INTERNAL_KEY_CANDIDATE_COUNT;
    view_out->candidates = candidates;
    return APTA_STATUS_OK;
}
#endif

apta_status_t apta_internal_key_select_chroma(
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES],
    uint32_t completed_windows,
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    apta_key_view_t *view_out)
{
    float scores[APTA_INTERNAL_KEY_CANDIDATE_COUNT] = {-1.0f, -1.0f, -1.0f};
    float energy = 0.0f;
    float separation;
    uint32_t tonic;
    uint32_t pitch;
    uint32_t confidence;

    if (chroma == NULL || candidates == NULL || view_out == NULL) {
        return APTA_ERROR_INVALID_ARGUMENT;
    }
    for (pitch = 0u; pitch < APTA_INTERNAL_KEY_PITCH_CLASSES; ++pitch) {
        if (!isfinite(chroma[pitch]) || chroma[pitch] < 0.0f) {
            return APTA_ERROR_INVALID_ARGUMENT;
        }
        energy += chroma[pitch];
    }
    if (completed_windows == 0u || energy <= 1e-12f) {
        return APTA_STATUS_NOT_AVAILABLE;
    }

    memset(candidates, 0,
           sizeof(*candidates) * APTA_INTERNAL_KEY_CANDIDATE_COUNT);
    for (tonic = 0u; tonic < APTA_INTERNAL_KEY_PITCH_CLASSES; ++tonic) {
        apta_key_insert_candidate(
            candidates,
            scores,
            (uint8_t)tonic,
            APTA_KEY_MODE_MAJOR,
            apta_key_profile_score(chroma, tonic, apta_major_profile));
        apta_key_insert_candidate(
            candidates,
            scores,
            (uint8_t)tonic,
            APTA_KEY_MODE_MINOR,
            apta_key_profile_score(chroma, tonic, apta_minor_profile));
    }

    /* The wire contract orders candidates by the encoded uint16 score, not by
     * the higher-precision float used for ranking. Distinct float scores can
     * round to the same 16-bit value (and flat/broadband material can produce
     * exact ties), which made a native MKEY result impossible to serialize.
     * Preserve the float ranking and resolve only encoded ties by one LSB. */
    for (pitch = 1u; pitch < APTA_INTERNAL_KEY_CANDIDATE_COUNT; ++pitch) {
        if (candidates[pitch].score >= candidates[pitch - 1u].score) {
            candidates[pitch].score =
                candidates[pitch - 1u].score > 0u
                    ? (uint16_t)(candidates[pitch - 1u].score - 1u)
                    : 0u;
        }
    }

    separation = scores[0] > scores[1] ? scores[0] - scores[1] : 0.0f;
    confidence = 25u +
                 (completed_windows >= 8u ? 40u : completed_windows * 5u) +
                 (uint32_t)fminf(35.0f, separation * 350.0f + 0.5f);
    if (confidence > APTA_CONFIDENCE_MAX) {
        confidence = APTA_CONFIDENCE_MAX;
    }
    candidates[0].confidence = (apta_confidence_value_t)confidence;
    candidates[1].confidence = confidence > 10u
                                   ? (apta_confidence_value_t)(confidence - 10u)
                                   : 0u;
    candidates[2].confidence = confidence > 20u
                                   ? (apta_confidence_value_t)(confidence - 20u)
                                   : 0u;

    apta_key_view_init(view_out);
    view_out->mode = candidates[0].mode;
    view_out->tonic = candidates[0].tonic;
    view_out->tuning_offset_cents = 0;
    view_out->confidence = candidates[0].confidence;
    view_out->state = completed_windows >= APTA_INTERNAL_KEY_STABLE_WINDOWS
                          ? APTA_FEATURE_STABLE
                          : APTA_FEATURE_PROVISIONAL;
    view_out->candidate_count = APTA_INTERNAL_KEY_CANDIDATE_COUNT;
    view_out->candidates = candidates;
    return APTA_STATUS_OK;
}

static void apta_key_reset_window(apta_internal_key_analysis_t *analysis)
{
    memset(analysis->q1, 0, sizeof(analysis->q1));
    memset(analysis->q2, 0, sizeof(analysis->q2));
    analysis->decimation_sum = 0.0f;
    analysis->decimation_count = 0u;
    analysis->window_samples = 0u;
}

static void apta_key_initialize(
    apta_internal_key_analysis_t *analysis,
    uint32_t source_sample_rate)
{
    const float decimated_rate =
        (float)source_sample_rate / (float)APTA_INTERNAL_KEY_DECIMATION;
#ifdef APTA_INTERNAL_KEY_SEMITONE_BAND
    /* Fixed -1/3, 0, and +1/3-semitone probes. These are evidence bands,
     * not tuning hypotheses: the selector still receives one folded chroma
     * and publishes a zero tuning offset. */
    static const float probe_ratios[APTA_INTERNAL_KEY_EVIDENCE_VARIANTS] = {
        0.98093009f,
        1.0f,
        1.01944064f
    };
#endif
    uint32_t variant;
    uint32_t bin;

    memset(analysis, 0, sizeof(*analysis));
#ifdef APTA_INTERNAL_KEY_SEMITONE_BAND
    if (decimated_rate <=
        2.0f * apta_key_frequencies[APTA_INTERNAL_KEY_BIN_COUNT - 1u] *
            probe_ratios[APTA_INTERNAL_KEY_EVIDENCE_VARIANTS - 1u]) {
        return;
    }
#else
    if (decimated_rate <= 2.0f * apta_key_frequencies[APTA_INTERNAL_KEY_BIN_COUNT - 1u]) {
        return;
    }
#endif
    for (variant = 0u;
         variant < APTA_INTERNAL_KEY_EVIDENCE_VARIANTS;
         ++variant) {
        for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
#ifdef APTA_INTERNAL_KEY_SEMITONE_BAND
            analysis->coefficients[variant][bin] =
                2.0f * cosf(6.28318530718f * apta_key_frequencies[bin] *
                            probe_ratios[variant] / decimated_rate);
#else
            analysis->coefficients[variant][bin] =
                2.0f * cosf(6.28318530718f * apta_key_frequencies[bin] /
                            decimated_rate);
#endif
        }
    }
    analysis->window_target_samples =
        source_sample_rate / APTA_INTERNAL_KEY_DECIMATION;
    if (analysis->window_target_samples == 0u) {
        return;
    }
    analysis->initialized = 1u;
}

#ifdef APTA_INTERNAL_KEY_MEAN_NORMALIZED
void apta_internal_key_mean_compress(float energies[APTA_INTERNAL_KEY_BIN_COUNT])
{
    float peak = 0.0f;
    float scaled_sum = 0.0f;
    float factor = 0.0f;
    uint32_t bin;
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
        if (!isfinite(energies[bin]) || energies[bin] < 0.0f) energies[bin] = 0.0f;
        if (energies[bin] > peak) peak = energies[bin];
    }
    if (peak > 0.0f) {
        for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin)
            scaled_sum += energies[bin] / peak;
        factor = (float)APTA_INTERNAL_KEY_BIN_COUNT / scaled_sum;
    }
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
        const float raw = energies[bin];
        const float compressed = peak > 0.0f ? logf(1.0f + (raw / peak) * factor) : 0.0f;
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
        apta_key_contrast_observe_energy(0u, bin, raw, compressed);
#endif
        energies[bin] = compressed;
    }
}
#endif

static void apta_key_finish_window(apta_internal_key_analysis_t *analysis)
{
#if defined(APTA_INTERNAL_KEY_TEMPORAL_CHORD) || \
    defined(APTA_INTERNAL_KEY_TEMPORAL_PROFILE)
    float window_chroma[APTA_INTERNAL_KEY_PITCH_CLASSES] = {0.0f};
#endif
#ifndef APTA_INTERNAL_KEY_MEAN_NORMALIZED
    uint32_t variant;
#endif
    uint32_t bin;

#ifdef APTA_INTERNAL_KEY_MEAN_NORMALIZED
    float energies[APTA_INTERNAL_KEY_BIN_COUNT];
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
        const float q1 = analysis->q1[0][bin];
        const float q2 = analysis->q2[0][bin];
        energies[bin] = q1 * q1 + q2 * q2 - analysis->coefficients[0][bin] * q1 * q2;
    }
    apta_internal_key_mean_compress(energies);
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin)
        analysis->chroma[0][bin % APTA_INTERNAL_KEY_PITCH_CLASSES] += energies[bin];
#elif defined(APTA_INTERNAL_KEY_SEMITONE_BAND)
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
        float band_energy = 0.0f;

        for (variant = 0u;
             variant < APTA_INTERNAL_KEY_EVIDENCE_VARIANTS;
             ++variant) {
            const float q1 = analysis->q1[variant][bin];
            const float q2 = analysis->q2[variant][bin];
            float energy = q1 * q1 + q2 * q2 -
                           analysis->coefficients[variant][bin] * q1 * q2;
            if (!isfinite(energy) || energy < 0.0f) {
                energy = 0.0f;
            }
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
            {
                const float compressed = logf(1.0f + energy);
                band_energy += compressed;
                apta_key_contrast_observe_energy(variant, bin, energy, compressed);
            }
#else
            band_energy += logf(1.0f + energy);
#endif
        }
        analysis->chroma[APTA_INTERNAL_KEY_BASE_VARIANT]
                        [bin % APTA_INTERNAL_KEY_PITCH_CLASSES] +=
            band_energy / (float)APTA_INTERNAL_KEY_EVIDENCE_VARIANTS;
    }
#else
    for (variant = 0u;
         variant < APTA_INTERNAL_KEY_EVIDENCE_VARIANTS;
         ++variant) {
        for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
            const float q1 = analysis->q1[variant][bin];
            const float q2 = analysis->q2[variant][bin];
            float energy = q1 * q1 + q2 * q2 -
                           analysis->coefficients[variant][bin] * q1 * q2;
            float compressed;
            if (!isfinite(energy) || energy < 0.0f) {
                energy = 0.0f;
            }
            /* Logarithmic compression: loud frames and resonant partials must
             * not dominate the accumulated chroma. Linear accumulation let
             * bass-heavy dominants outweigh tonic harmony and drove fifth and
             * parallel-mode confusions on the official corpus taxonomy. */
            compressed = logf(1.0f + energy);
#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
            apta_key_contrast_observe_energy(variant, bin, energy, compressed);
#endif
            analysis->chroma[variant]
                            [bin % APTA_INTERNAL_KEY_PITCH_CLASSES] +=
                compressed;
#if defined(APTA_INTERNAL_KEY_TEMPORAL_CHORD) || \
    defined(APTA_INTERNAL_KEY_TEMPORAL_PROFILE)
            if (variant == APTA_INTERNAL_KEY_BASE_VARIANT) {
                window_chroma[bin % APTA_INTERNAL_KEY_PITCH_CLASSES] +=
                    compressed;
            }
#endif
#ifdef APTA_INTERNAL_KEY_SPECTRAL_PROFILE
            analysis->spectral_profile[variant][bin] += compressed;
#endif
        }
    }
#endif
#ifdef APTA_INTERNAL_KEY_TEMPORAL_CHORD
    apta_internal_key_temporal_vote_chroma(analysis, window_chroma);
#endif
#ifdef APTA_INTERNAL_KEY_TEMPORAL_PROFILE
    apta_internal_key_temporal_profile_add_chroma(analysis, window_chroma);
#endif
    analysis->completed_windows += 1u;
    apta_key_reset_window(analysis);
}

void apta_internal_key_feed_sample(
    apta_session_t *session,
    float sample,
    apta_source_frame_t source_frame)
{
    apta_internal_key_analysis_t *analysis;
    float decimated_sample;
    uint32_t variant;
    uint32_t bin;

    if (session == NULL ||
        (session->config.requested_features & APTA_FEATURE_MUSICAL_KEY) == 0u) {
        return;
    }
    analysis = &session->key_analysis;
    if (!analysis->initialized) {
        apta_key_initialize(analysis, session->config.source_sample_rate);
        if (!analysis->initialized) {
            return;
        }
    }

    if (analysis->has_next_source_frame &&
        source_frame != analysis->next_source_frame) {
        apta_key_reset_window(analysis);
    }
    if (analysis->completed_windows == 0u && analysis->window_samples == 0u &&
        analysis->decimation_count == 0u) {
        analysis->evidence_first_frame = source_frame;
    }
    analysis->next_source_frame = source_frame + 1u;
    analysis->has_next_source_frame = 1u;
    analysis->evidence_end_frame = source_frame + 1u;

    analysis->decimation_sum += sample;
    analysis->decimation_count += 1u;
    if (analysis->decimation_count < APTA_INTERNAL_KEY_DECIMATION) {
        return;
    }
    decimated_sample =
        analysis->decimation_sum / (float)APTA_INTERNAL_KEY_DECIMATION;
    analysis->decimation_sum = 0.0f;
    analysis->decimation_count = 0u;

    for (variant = 0u;
         variant < APTA_INTERNAL_KEY_EVIDENCE_VARIANTS;
         ++variant) {
        for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
            const float q0 = decimated_sample +
                             analysis->coefficients[variant][bin] *
                                 analysis->q1[variant][bin] -
                             analysis->q2[variant][bin];
            analysis->q2[variant][bin] = analysis->q1[variant][bin];
            analysis->q1[variant][bin] = q0;
        }
    }
    analysis->window_samples += 1u;
    if (analysis->window_samples >= analysis->window_target_samples) {
        apta_key_finish_window(analysis);
    }
}

int apta_internal_key_refresh_pending(const apta_session_t *session)
{
    const apta_internal_key_analysis_t *analysis;

    if (session == NULL ||
        (session->config.requested_features & APTA_FEATURE_MUSICAL_KEY) == 0u) {
        return 0;
    }
    analysis = &session->key_analysis;
    if (analysis->completed_windows == analysis->selected_windows) {
        return 0;
    }
    return analysis->selected_windows == 0u ||
           analysis->completed_windows >=
               analysis->selected_windows + APTA_INTERNAL_KEY_PUBLISH_INTERVAL ||
           session->end_of_input_signalled;
}

apta_status_t apta_internal_key_refresh(
    apta_session_t *session,
    uint32_t step_limit,
    uint32_t *completed_steps_out)
{
    apta_key_candidate_t next_candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT];
    apta_key_view_t next_view;
    apta_status_t status;
    int changed;

    if (session == NULL || completed_steps_out == NULL) {
        return APTA_ERROR_INVALID_ARGUMENT;
    }
    *completed_steps_out = 0u;
    if (!apta_internal_key_refresh_pending(session)) {
        return APTA_STATUS_OK;
    }
    if (step_limit == 0u) {
        return APTA_STATUS_MORE_WORK;
    }
    *completed_steps_out = 1u;

    {
#if !defined(APTA_INTERNAL_KEY_TEMPORAL_CHORD) && \
    !defined(APTA_INTERNAL_KEY_TEMPORAL_PROFILE)
        const uint32_t selected_variant = APTA_INTERNAL_KEY_BASE_VARIANT;
#endif

#ifdef APTA_INTERNAL_KEY_TEMPORAL_CHORD
        status = apta_internal_key_select_temporal(
            &session->key_analysis,
            session->key_analysis.completed_windows,
            next_candidates,
            &next_view);
#elif defined(APTA_INTERNAL_KEY_TEMPORAL_PROFILE)
        status = apta_internal_key_select_temporal_profile(
            &session->key_analysis,
            session->key_analysis.completed_windows,
            next_candidates,
            &next_view);
#else
        status = apta_internal_key_select_chroma(
            session->key_analysis.chroma[selected_variant],
            session->key_analysis.completed_windows,
            next_candidates,
            &next_view);
#endif
#ifdef APTA_INTERNAL_KEY_HPCP
        if (status == APTA_STATUS_OK) {
            float harmonic_chroma[APTA_INTERNAL_KEY_PITCH_CLASSES];
            apta_key_candidate_t harmonic_candidates
                [APTA_INTERNAL_KEY_CANDIDATE_COUNT];
            apta_key_view_t harmonic_view;
            apta_status_t harmonic_status;

            apta_internal_key_harmonic_chroma(
                session->key_analysis.spectral_profile[selected_variant],
                harmonic_chroma);
            harmonic_status = apta_internal_key_select_chroma(
                harmonic_chroma,
                session->key_analysis.completed_windows,
                harmonic_candidates,
                &harmonic_view);
            /* The harmonic projection changes evidence shape, so its raw
             * cosine score is not calibrated against the folded chroma score.
             * Gate on the selector's separation-derived confidence instead.
             * Same-verdict projections are ignored to keep default score and
             * publication behavior stable inside this opt-in experiment. */
            if (harmonic_status == APTA_STATUS_OK &&
                harmonic_candidates[0].confidence >=
                    next_candidates[0].confidence &&
                (harmonic_view.tonic != next_view.tonic ||
                 harmonic_view.mode != next_view.mode)) {
                memcpy(next_candidates,
                       harmonic_candidates,
                       sizeof(next_candidates));
                next_view = harmonic_view;
                status = harmonic_status;
            }
        }
#endif
        if (status == APTA_STATUS_OK) {
            const int8_t tuning = 0;
            uint32_t candidate;

            next_view.tuning_offset_cents = tuning;
            for (candidate = 0u;
                 candidate < APTA_INTERNAL_KEY_CANDIDATE_COUNT;
                 ++candidate) {
                next_candidates[candidate].tuning_offset_cents = tuning;
            }
        }
    }
    session->key_analysis.selected_windows =
        session->key_analysis.completed_windows;
    if (status == APTA_STATUS_NOT_AVAILABLE) {
        return APTA_STATUS_OK;
    }
    if (status < 0) {
        return status;
    }
    apta_frame_range_init(&next_view.applicability_range);
    next_view.applicability_range.first_frame =
        session->key_analysis.evidence_first_frame;
    next_view.applicability_range.end_frame =
        session->key_analysis.evidence_end_frame;

    changed = !session->has_key ||
              session->key_value.mode != next_view.mode ||
              session->key_value.tonic != next_view.tonic ||
              session->key_value.tuning_offset_cents !=
                  next_view.tuning_offset_cents ||
              session->key_value.state != next_view.state ||
              session->key_value.confidence != next_view.confidence ||
              session->key_candidates[0].score != next_candidates[0].score;
    session->key_value = next_view;
    memcpy(
        session->key_candidates,
        next_candidates,
        sizeof(next_candidates));
    session->key_value.candidates = session->key_candidates;
    session->has_key = 1u;
    if (changed) {
        session->key_mutation_serial += 1u;
    }
    return APTA_STATUS_OK;
}

apta_feature_mask_t apta_internal_key_pending_features(
    const apta_session_t *session)
{
    if (session == NULL || !session->has_key ||
        session->key_mutation_serial == session->key_published_serial) {
        return 0u;
    }
    return APTA_FEATURE_MUSICAL_KEY;
}

void apta_internal_key_mark_published(apta_session_t *session)
{
    if (session != NULL) {
        session->key_published_serial = session->key_mutation_serial;
    }
}

static void apta_key_snapshot_view(
    const apta_session_t *session,
    apta_key_view_t *view,
    apta_key_candidate_t *candidates,
    int completed)
{
    *view = session->key_value;
    memcpy(
        candidates,
        session->key_candidates,
        sizeof(session->key_candidates));
    view->candidates = candidates;
    if (completed) {
        view->state = APTA_FEATURE_FINAL;
    }
}

apta_status_t apta_internal_key_build_snapshot(
    const apta_session_t *session,
    apta_result_t *result)
{
    const int completed =
        atomic_load_explicit(&session->state, memory_order_acquire) ==
        APTA_SESSION_COMPLETED;

    if (session == NULL || result == NULL) {
        return APTA_ERROR_INVALID_ARGUMENT;
    }
    if (!session->has_key ||
        (session->config.requested_features & APTA_FEATURE_MUSICAL_KEY) == 0u) {
        return APTA_STATUS_OK;
    }
    result->key_candidates =
        (apta_key_candidate_t *)apta_internal_context_allocate(
            session->context,
            sizeof(session->key_candidates),
            alignof(apta_key_candidate_t),
            APTA_MEMORY_PERSISTENT);
    if (result->key_candidates == NULL) {
        return APTA_ERROR_OUT_OF_MEMORY;
    }
    apta_key_snapshot_view(
        session,
        &result->key,
        result->key_candidates,
        completed);
    result->info.available_features |= APTA_FEATURE_MUSICAL_KEY;
    return APTA_STATUS_OK;
}

apta_status_t apta_internal_key_pool_build(
    apta_internal_result_pool_control_t *pool,
    const apta_session_t *session,
    apta_result_t *result)
{
    const apta_internal_result_pool_layout_t *layout;
    uint8_t *storage;
    const int completed =
        atomic_load_explicit(&session->state, memory_order_acquire) ==
        APTA_SESSION_COMPLETED;

    if (pool == NULL || session == NULL || result == NULL) {
        return APTA_ERROR_INVALID_ARGUMENT;
    }
    if (!session->has_key ||
        (session->config.requested_features & APTA_FEATURE_MUSICAL_KEY) == 0u) {
        return APTA_STATUS_OK;
    }
    layout = apta_internal_result_pool_get_layout(pool);
    storage = (uint8_t *)apta_internal_result_pool_get_slot_storage(
        pool, result->result_pool_slot_index);
    if (layout == NULL || storage == NULL ||
        layout->key_candidate_capacity < APTA_INTERNAL_KEY_CANDIDATE_COUNT) {
        return APTA_ERROR_LIMIT_EXCEEDED;
    }
    result->key_candidates = (apta_key_candidate_t *)(void *)(
        storage + layout->key_candidates_offset);
    apta_key_snapshot_view(
        session,
        &result->key,
        result->key_candidates,
        completed);
    result->info.available_features |= APTA_FEATURE_MUSICAL_KEY;
    return APTA_STATUS_OK;
}
