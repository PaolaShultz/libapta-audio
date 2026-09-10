// SPDX-License-Identifier: Apache-2.0
#ifndef APTA_KEY_INTERNAL_H
#define APTA_KEY_INTERNAL_H

#include "../core/apta_internal.h"
#include "../core/apta_result_pool.h"

void apta_internal_key_feed_sample(
    apta_session_t *session,
    float sample,
    apta_source_frame_t source_frame);

int apta_internal_key_refresh_pending(const apta_session_t *session);

apta_status_t apta_internal_key_refresh(
    apta_session_t *session,
    uint32_t step_limit,
    uint32_t *completed_steps_out);

apta_feature_mask_t apta_internal_key_pending_features(
    const apta_session_t *session);

void apta_internal_key_mark_published(apta_session_t *session);

apta_status_t apta_internal_key_build_snapshot(
    const apta_session_t *session,
    apta_result_t *result);

apta_status_t apta_internal_key_pool_build(
    apta_internal_result_pool_control_t *pool,
    const apta_session_t *session,
    apta_result_t *result);

apta_status_t apta_internal_key_select_chroma(
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES],
    uint32_t completed_windows,
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    apta_key_view_t *view_out);

#ifdef APTA_INTERNAL_KEY_TEMPORAL_CHORD
void apta_internal_key_temporal_vote_chroma(
    apta_internal_key_analysis_t *analysis,
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES]);

apta_status_t apta_internal_key_select_temporal(
    const apta_internal_key_analysis_t *analysis,
    uint32_t completed_windows,
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    apta_key_view_t *view_out);
#endif

#ifdef APTA_INTERNAL_KEY_TEMPORAL_PROFILE
void apta_internal_key_temporal_profile_add_chroma(
    apta_internal_key_analysis_t *analysis,
    const float chroma[APTA_INTERNAL_KEY_PITCH_CLASSES]);

apta_status_t apta_internal_key_select_temporal_profile(
    const apta_internal_key_analysis_t *analysis,
    uint32_t completed_windows,
    apta_key_candidate_t candidates[APTA_INTERNAL_KEY_CANDIDATE_COUNT],
    apta_key_view_t *view_out);
#endif

#ifdef APTA_INTERNAL_KEY_HPCP
void apta_internal_key_harmonic_chroma(
    const float spectral_profile[APTA_INTERNAL_KEY_BIN_COUNT],
    float chroma_out[APTA_INTERNAL_KEY_PITCH_CLASSES]);
#endif

#ifdef APTA_INTERNAL_KEY_TRACE
void apta_internal_key_trace_get(
    const apta_session_t *session,
    const float **spectral_profile_out,
    uint32_t *bin_count_out,
    const float **chroma_out,
    uint32_t *completed_windows_out);
#endif

#ifdef APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC
/* Implemented only by the explicit-build synthetic diagnostic executable. */
void apta_key_contrast_observe_energy(
    uint32_t variant, uint32_t bin, float energy, float compressed);
#endif

#ifdef APTA_INTERNAL_KEY_MEAN_NORMALIZED
void apta_internal_key_mean_compress(float energies[APTA_INTERNAL_KEY_BIN_COUNT]);
#endif

#endif /* APTA_KEY_INTERNAL_H */
