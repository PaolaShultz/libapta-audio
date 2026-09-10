// SPDX-License-Identifier: Apache-2.0
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "../../src/key/apta_key_internal.h"
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "CHECK failed %s:%d: %s\n", __FILE__, __LINE__, #x); return 1; } } while (0)

int main(void)
{
    float e[36] = {0}, reference[36], scaled[36];
    unsigned i, level;
    apta_session_t session;
    apta_key_candidate_t candidates[3];
    apta_key_view_t view;
    apta_internal_key_mean_compress(e);
    for (i = 0; i < 36; ++i) CHECK(e[i] == 0.0f);
    e[0] = NAN; e[1] = INFINITY; e[2] = -1.0f; e[3] = -INFINITY;
    apta_internal_key_mean_compress(e);
    for (i = 0; i < 36; ++i) CHECK(e[i] == 0.0f);
    for (level = 0; level < 3; ++level) {
        const float value = level == 0 ? FLT_TRUE_MIN : level == 1 ? 1.0f : FLT_MAX;
        for (i = 0; i < 36; ++i) e[i] = value;
        apta_internal_key_mean_compress(e);
        for (i = 0; i < 36; ++i) CHECK(e[i] == logf(2.0f));
        memset(e, 0, sizeof(e)); e[17] = value;
        apta_internal_key_mean_compress(e);
        for (i = 0; i < 36; ++i) CHECK(e[i] == (i == 17 ? logf(37.0f) : 0.0f));
    }
    for (i = 0; i < 36; ++i) reference[i] = (float)((i + 1) * (i + 1));
    memcpy(e, reference, sizeof(e));
    apta_internal_key_mean_compress(reference);
    for (level = 0; level < 4; ++level) {
        static const int shifts[] = {-8, -4, 0, 2};
        for (i = 0; i < 36; ++i) scaled[i] = ldexpf(e[i], shifts[level]);
        apta_internal_key_mean_compress(scaled);
        CHECK(memcmp(scaled, reference, sizeof(scaled)) == 0);
        for (i = 0; i < 36; ++i) CHECK(isfinite(scaled[i]) && scaled[i] >= 0.0f && scaled[i] <= logf(37.0f));
    }
    /* Actual silent windows complete without creating evidence or erasing it. */
    memset(&session, 0, sizeof(session));
    session.config.source_sample_rate = 48000u;
    session.config.requested_features = APTA_FEATURE_MUSICAL_KEY;
    for (i = 0; i < 48000; ++i) apta_internal_key_feed_sample(&session, 0.0f, i);
    CHECK(session.key_analysis.completed_windows == 1u);
    for (i = 0; i < 12; ++i) CHECK(session.key_analysis.chroma[0][i] == 0.0f);
    CHECK(apta_internal_key_select_chroma(session.key_analysis.chroma[0], 1u, candidates, &view) == APTA_STATUS_NOT_AVAILABLE);
    for (i = 0; i < 12; ++i) session.key_analysis.chroma[0][i] = (float)(i + 1);
    memcpy(reference, session.key_analysis.chroma[0], 12 * sizeof(float));
    for (i = 48000; i < 96000; ++i) apta_internal_key_feed_sample(&session, 0.0f, i);
    CHECK(session.key_analysis.completed_windows == 2u);
    CHECK(memcmp(reference, session.key_analysis.chroma[0], 12 * sizeof(float)) == 0);
    return 0;
}
