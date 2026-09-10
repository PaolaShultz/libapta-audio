// SPDX-License-Identifier: Apache-2.0
#include <math.h>
#include "apta_key_internal.h"

/* Kept separate from sample feeding to avoid charging cold-window temporary
 * registers/stack to every input sample. Compression arithmetic is unchanged. */
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

void apta_internal_key_mean_accumulate_in_place(apta_internal_key_analysis_t *analysis)
{
    uint32_t bin;
    /* Each resonator is independent. Once its energy is computed, q1 is dead
     * until the caller resets both resonator arrays before the next sample. */
    float *energies = analysis->q1[0];
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin) {
        const float q1 = analysis->q1[0][bin];
        const float q2 = analysis->q2[0][bin];
        energies[bin] = q1 * q1 + q2 * q2 - analysis->coefficients[0][bin] * q1 * q2;
    }
    apta_internal_key_mean_compress(energies);
    for (bin = 0u; bin < APTA_INTERNAL_KEY_BIN_COUNT; ++bin)
        analysis->chroma[0][bin % APTA_INTERNAL_KEY_PITCH_CLASSES] += energies[bin];
}
