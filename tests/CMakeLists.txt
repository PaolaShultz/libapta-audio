# SPDX-License-Identifier: Apache-2.0

find_package(Threads REQUIRED)

add_library(apta_headers_c OBJECT compile/headers_c.c)
target_link_libraries(apta_headers_c PRIVATE apta::headers)
set_target_properties(apta_headers_c PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)

add_library(apta_headers_cpp OBJECT compile/headers_cpp.cpp)
target_link_libraries(apta_headers_cpp PRIVATE apta::headers)
set_target_properties(apta_headers_cpp PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)

add_library(apta_abi_layout OBJECT compile/abi_layout.c)
target_link_libraries(apta_abi_layout PRIVATE apta::headers)
set_target_properties(apta_abi_layout PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)

function(apta_add_c_test target test_name source)
    add_executable(${target} ${source})
    target_link_libraries(${target} PRIVATE apta::core)
    set_target_properties(${target} PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)
    add_test(NAME ${test_name} COMMAND ${target})
endfunction()

function(apta_add_cpp_test target test_name source)
    add_executable(${target} ${source})
    target_link_libraries(${target} PRIVATE apta::core Threads::Threads)
    set_target_properties(${target} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
    add_test(NAME ${test_name} COMMAND ${target})
endfunction()

function(apta_add_desktop_test target test_name source)
    add_executable(${target} ${source})
    target_link_libraries(
        ${target}
        PRIVATE
            apta::core
            apta::decoder_wav
            apta::port_native)
    if(UNIX)
        target_compile_definitions(${target} PRIVATE _POSIX_C_SOURCE=200809L)
    endif()
    set_target_properties(${target} PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)
    add_test(NAME ${test_name} COMMAND ${target})
endfunction()

apta_add_c_test(apta_core_smoke apta.core.smoke unit/core_smoke.c)
apta_add_c_test(apta_allocation_failure apta.core.allocation_failure unit/allocation_failure.c)
apta_add_c_test(apta_cancellation apta.core.cancellation unit/cancellation.c)
apta_add_c_test(apta_initializers apta.api.initializers unit/initializers.c)
apta_add_c_test(
    apta_result_builder_roundtrip
    apta.api.result_builder_roundtrip
    unit/result_builder_roundtrip.c)
apta_add_c_test(
    apta_result_builder_validation
    apta.api.result_builder_validation
    unit/result_builder_validation.c)
apta_add_c_test(
    apta_result_builder_allocation_failure
    apta.api.result_builder_allocation_failure
    unit/result_builder_allocation_failure.c)
apta_add_c_test(
    apta_result_builder_review_regressions
    apta.api.result_builder_review_regressions
    unit/result_builder_review_regressions.c)
target_link_libraries(
    apta_result_builder_review_regressions PRIVATE apta_c11_atomics)
apta_add_c_test(
    apta_result_model_1_1
    apta.api.result_model_1_1
    unit/result_model_1_1.c)
target_link_libraries(apta_result_model_1_1 PRIVATE apta_c11_atomics)
target_include_directories(
    apta_result_model_1_1
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(
    apta_result_model_1_1_ranges
    apta.api.result_model_1_1_ranges
    unit/result_model_1_1_ranges.c)
target_link_libraries(apta_result_model_1_1_ranges PRIVATE apta_c11_atomics)
target_include_directories(
    apta_result_model_1_1_ranges
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(
    apta_result_model_1_1_quality
    apta.api.result_model_1_1_quality
    unit/result_model_1_1_quality.c)
target_link_libraries(apta_result_model_1_1_quality PRIVATE apta_c11_atomics)
target_include_directories(
    apta_result_model_1_1_quality
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(
    apta_result_model_1_1_storage
    apta.api.result_model_1_1_storage
    unit/result_model_1_1_storage.c)
target_link_libraries(apta_result_model_1_1_storage PRIVATE apta_c11_atomics)
target_include_directories(
    apta_result_model_1_1_storage
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_version_validation apta.api.version_validation unit/version_validation.c)
apta_add_c_test(apta_metadata_lifecycle apta.metadata.lifecycle unit/metadata_lifecycle.c)
apta_add_c_test(apta_pcm_pull apta.source.pcm_pull unit/pcm_pull.c)
apta_add_c_test(apta_pcm_pull_bounded apta.source.pcm_pull_bounded unit/pcm_pull_bounded.c)

apta_add_c_test(apta_waveform_overview apta.waveform.overview unit/waveform_overview.c)
apta_add_c_test(apta_waveform_determinism apta.waveform.determinism unit/waveform_determinism.c)
if(APTA_ENABLE_EXPERIMENTAL_MULTIBAND_ONSET)
    apta_add_c_test(
        apta_multiband_onset
        apta.experimental.multiband_onset
        unit/multiband_onset.c)
    target_include_directories(apta_multiband_onset PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
    if(UNIX)
        target_link_libraries(apta_multiband_onset PRIVATE m)
    endif()
endif()
if(APTA_ENABLE_EXPERIMENTAL_TRANSIENT_LATTICE_I8)
    apta_add_c_test(
        apta_transient_peak
        apta.experimental.transient_peak
        unit/transient_peak.c)
    target_link_libraries(apta_transient_peak PRIVATE apta_c11_atomics)
    target_include_directories(
        apta_transient_peak
        PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
    if(UNIX)
        target_link_libraries(apta_transient_peak PRIVATE m)
    endif()
endif()
if(APTA_ENABLE_EXPERIMENTAL_SPECTRAL_FLUX_I9)
    apta_add_c_test(
        apta_spectral_flux_i9
        apta.experimental.spectral_flux_i9
        unit/spectral_flux_i9.c)
    target_link_libraries(apta_spectral_flux_i9 PRIVATE apta_c11_atomics)
    target_include_directories(
        apta_spectral_flux_i9
        PRIVATE
            ${CMAKE_SOURCE_DIR}/src/core
            ${CMAKE_SOURCE_DIR}/src/tempo)
    if(UNIX)
        target_link_libraries(apta_spectral_flux_i9 PRIVATE m)
    endif()
endif()
if(APTA_ENABLE_EXPERIMENTAL_COMPLEX_DEVIATION_I10)
    apta_add_c_test(
        apta_complex_deviation_i10
        apta.experimental.complex_deviation_i10
        unit/complex_deviation_i10.c)
    target_link_libraries(apta_complex_deviation_i10 PRIVATE apta_c11_atomics)
    target_include_directories(
        apta_complex_deviation_i10
        PRIVATE
            ${CMAKE_SOURCE_DIR}/src/core
            ${CMAKE_SOURCE_DIR}/src/tempo)
    if(UNIX)
        target_link_libraries(apta_complex_deviation_i10 PRIVATE m)
    endif()
endif()
if(APTA_ENABLE_EXPERIMENTAL_METER_TRACE AND
   APTA_ENABLE_EXPERIMENTAL_MULTIBAND_ONSET)
    apta_add_c_test(
        apta_s4_trace_energy
        apta.experimental.s4_trace_energy
        unit/s4_trace_energy.c)
    target_link_libraries(apta_s4_trace_energy PRIVATE apta_c11_atomics)
    target_include_directories(
        apta_s4_trace_energy
        PRIVATE
            ${CMAKE_SOURCE_DIR}/src/core
            ${CMAKE_SOURCE_DIR}/src/tempo)
    if(UNIX)
        target_link_libraries(apta_s4_trace_energy PRIVATE m)
    endif()
endif()
apta_add_c_test(apta_waveform_priority apta.waveform.priority unit/waveform_priority.c)
apta_add_c_test(apta_scheduler_deadline apta.scheduler.deadline unit/scheduler_deadline.c)
apta_add_c_test(apta_scheduler_process_deadline apta.scheduler.process_deadline unit/scheduler_process_deadline.c)
apta_add_c_test(apta_scheduler_aging apta.scheduler.aging unit/scheduler_aging.c)
apta_add_c_test(apta_waveform_contracts apta.waveform.contracts unit/waveform_contracts.c)
apta_add_c_test(apta_waveform_detail apta.waveform.detail unit/waveform_detail.c)
apta_add_c_test(apta_waveform_detail_contracts apta.waveform.detail_contracts unit/waveform_detail_contracts.c)
apta_add_c_test(apta_waveform_detail_replay apta.waveform.detail_replay unit/waveform_detail_replay.c)

apta_add_c_test(apta_s4_tempo_grid apta.s4.tempo_grid unit/s4_tempo_grid.c)
apta_add_c_test(apta_s4_silence apta.s4.silence unit/s4_silence.c)
apta_add_c_test(apta_s4_bounded apta.s4.bounded unit/s4_bounded.c)
apta_add_c_test(apta_s4_pull apta.s4.pull unit/s4_pull.c)
apta_add_c_test(apta_s4_tempo_vectors apta.s4.tempo_vectors unit/s4_tempo_vectors.c)
apta_add_c_test(apta_s4_tempo_subbin apta.s4.tempo_subbin unit/s4_tempo_subbin.c)
apta_add_c_test(apta_s4_endorsement apta.s4.endorsement unit/s4_endorsement.c)
apta_add_c_test(apta_s4_focus apta.s4.focus unit/s4_focus.c)
apta_add_c_test(apta_s4_refresh_gate apta.s4.refresh_gate unit/s4_refresh_gate.c)
apta_add_c_test(apta_s4_evidence_cache apta.s4.evidence_cache unit/s4_evidence_cache.c)
target_link_libraries(apta_s4_evidence_cache PRIVATE apta_c11_atomics)
target_include_directories(apta_s4_evidence_cache PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_confidence_without_tempo apta.waveform.confidence_without_tempo unit/confidence_without_tempo.c)
apta_add_c_test(apta_workspace_requirements apta.memory.workspace_requirements unit/workspace_requirements.c)
apta_add_c_test(apta_waveform_3band apta.waveform.three_band unit/waveform_3band.c)
apta_add_c_test(apta_waveform_resolution apta.waveform.resolution unit/waveform_resolution.c)
apta_add_c_test(apta_session_seeding apta.session.seeding unit/session_seeding.c)
apta_add_c_test(apta_s4_relations apta.s4.relations unit/s4_relations.c)
target_link_libraries(apta_s4_relations PRIVATE apta_c11_atomics)
target_include_directories(apta_s4_relations PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_s4_serialization apta.serialization.s4 unit/s4_serialization.c)
target_link_libraries(apta_s4_serialization PRIVATE apta_c11_atomics)
target_include_directories(apta_s4_serialization PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_s4_allocation_failure apta.serialization.s4_allocation_failure unit/s4_allocation_failure.c)

apta_add_c_test(apta_s6_global_grid apta.s6.global_grid unit/s6_global_grid.c)
apta_add_c_test(
    apta_s6_dominant_tempo
    apta.s6.dominant_tempo
    unit/s6_dominant_tempo.c)
target_include_directories(
    apta_s6_dominant_tempo PRIVATE ${CMAKE_SOURCE_DIR}/src/beatgrid)
apta_add_c_test(apta_s6_revision apta.s6.revision unit/s6_revision.c)
apta_add_c_test(apta_s6_bounded apta.s6.bounded unit/s6_bounded.c)
target_include_directories(
    apta_s6_bounded PRIVATE ${CMAKE_SOURCE_DIR}/src/beatgrid)
apta_add_c_test(
    apta_cooperative_refresh
    apta.scheduler.cooperative_refresh
    unit/cooperative_refresh.c)
target_link_libraries(apta_cooperative_refresh PRIVATE apta_c11_atomics)
target_include_directories(
    apta_cooperative_refresh
    PRIVATE
        ${CMAKE_SOURCE_DIR}/src/core
        ${CMAKE_SOURCE_DIR}/src/beatgrid)
apta_add_c_test(apta_s6_serialization apta.serialization.s6 unit/s6_serialization.c)
target_link_libraries(apta_s6_serialization PRIVATE apta_c11_atomics)
target_include_directories(apta_s6_serialization PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_s6_allocation_failure apta.serialization.s6_allocation_failure unit/s6_allocation_failure.c)
apta_add_c_test(
    apta_meter_downbeat
    apta.dj.meter_downbeat
    unit/meter_downbeat.c)
target_link_libraries(apta_meter_downbeat PRIVATE apta_c11_atomics)
target_include_directories(
    apta_meter_downbeat
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core ${CMAKE_SOURCE_DIR}/src/beatgrid)
apta_add_c_test(
    apta_quality_model
    apta.dj.quality_model
    unit/quality_model.c)
target_include_directories(
    apta_quality_model
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core ${CMAKE_SOURCE_DIR}/src/confidence)
apta_add_c_test(
    apta_quality_publication_failure
    apta.dj.quality_publication_failure
    unit/quality_publication_failure.c)
target_link_libraries(apta_quality_publication_failure PRIVATE apta_c11_atomics)
target_include_directories(
    apta_quality_publication_failure
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core ${CMAKE_SOURCE_DIR}/src/confidence)
apta_add_c_test(
    apta_musical_key
    apta.dj.musical_key
    unit/musical_key.c)
target_link_libraries(apta_musical_key PRIVATE apta_c11_atomics)
target_include_directories(
    apta_musical_key
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core ${CMAKE_SOURCE_DIR}/src/key)

# Development measurement instrument, deliberately excluded from the ordinary
# test/build/install graph. WP4 experiments build it explicitly to compare the
# private per-sample key front end without decoder or filesystem noise.
add_executable(
    apta_key_feed_benchmark
    EXCLUDE_FROM_ALL
    bench/key_feed_benchmark.c)
target_link_libraries(
    apta_key_feed_benchmark
    PRIVATE apta::core apta_c11_atomics)
target_include_directories(
    apta_key_feed_benchmark
    PRIVATE ${CMAKE_SOURCE_DIR}/src/core ${CMAKE_SOURCE_DIR}/src/key)
set_target_properties(
    apta_key_feed_benchmark
    PROPERTIES
        C_STANDARD 11
        C_STANDARD_REQUIRED YES
        C_EXTENSIONS NO)
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(
        apta_key_feed_benchmark
        PRIVATE -Wall -Wextra -Wpedantic)
    target_link_libraries(apta_key_feed_benchmark PRIVATE m)
    if(APTA_WARNINGS_AS_ERRORS)
        target_compile_options(apta_key_feed_benchmark PRIVATE -Werror)
    endif()
elseif(MSVC)
    target_compile_options(apta_key_feed_benchmark PRIVATE /W4)
    if(APTA_WARNINGS_AS_ERRORS)
        target_compile_options(apta_key_feed_benchmark PRIVATE /WX)
    endif()
endif()
# Explicit-build, synthetic-only key diagnostic; never installed or run on a corpus.
foreach(key_diagnostic IN ITEMS apta_key_mode_diagnostic apta_key_extraction_reference apta_key_contrast_diagnostic apta_key_gain_diagnostic)
add_executable(${key_diagnostic} EXCLUDE_FROM_ALL bench/key_mode_diagnostic.c)
target_link_libraries(${key_diagnostic} PRIVATE apta::core apta_c11_atomics)
target_include_directories(${key_diagnostic} PRIVATE ${CMAKE_SOURCE_DIR}/src/core ${CMAKE_SOURCE_DIR}/src/key)
set_target_properties(${key_diagnostic} PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(${key_diagnostic} PRIVATE -Wall -Wextra -Wpedantic)
    target_link_libraries(${key_diagnostic} PRIVATE m)
    if(APTA_WARNINGS_AS_ERRORS)
        target_compile_options(${key_diagnostic} PRIVATE -Werror)
    endif()
elseif(MSVC)
    target_compile_options(${key_diagnostic} PRIVATE /W4)
    if(APTA_WARNINGS_AS_ERRORS)
        target_compile_options(${key_diagnostic} PRIVATE /WX)
    endif()
endif()
endforeach()
target_compile_definitions(apta_key_extraction_reference PRIVATE APTA_KEY_EXTRACTION_REFERENCE=1)
# Only this executable's key translation unit receives the observer macro.
# Its definitions satisfy the static core's key references without loading the
# uninstrumented key object from the archive. The production core is unchanged.
foreach(observer_diagnostic IN ITEMS apta_key_contrast_diagnostic apta_key_gain_diagnostic)
target_sources(${observer_diagnostic} PRIVATE ${CMAKE_SOURCE_DIR}/src/key/apta_key.c)
target_compile_definitions(${observer_diagnostic} PRIVATE APTA_INTERNAL_KEY_CONTRAST_DIAGNOSTIC=1)
endforeach()
target_compile_definitions(apta_key_gain_diagnostic PRIVATE APTA_KEY_GAIN_DIAGNOSTIC=1)
if(APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY)
    apta_add_c_test(apta_key_mean_normalization apta.dj.key_mean_normalization unit/key_mean_normalization.c)
    target_link_libraries(apta_key_mean_normalization PRIVATE apta_c11_atomics)
    if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(apta_key_mean_normalization PRIVATE -Wall -Wextra -Wpedantic)
        target_link_libraries(apta_key_mean_normalization PRIVATE m)
        if(APTA_WARNINGS_AS_ERRORS)
            target_compile_options(apta_key_mean_normalization PRIVATE -Werror)
        endif()
    endif()
endif()
apta_add_c_test(
    apta_dj_sections_roundtrip
    apta.serialization.dj_sections_roundtrip
    unit/dj_sections_roundtrip.c)
target_compile_definitions(
    apta_dj_sections_roundtrip
    PRIVATE
        APTA_DJ_GOLDEN_HEX_PATH="${CMAKE_SOURCE_DIR}/tests/fixtures/dj-sections-v1-combined.apta.hex")
apta_add_c_test(
    apta_dj_sections_malformed
    apta.serialization.dj_sections_malformed
    unit/dj_sections_malformed.c)
target_compile_definitions(
    apta_dj_sections_malformed
    PRIVATE
        APTA_DJ_GOLDEN_HEX_PATH="${CMAKE_SOURCE_DIR}/tests/fixtures/dj-sections-v1-combined.apta.hex")
apta_add_c_test(
    apta_dj_sections_state_scale
    apta.serialization.dj_sections_state_scale
    unit/dj_sections_state_scale.c)
target_link_libraries(apta_dj_sections_state_scale PRIVATE apta_c11_atomics)
set_tests_properties(
    apta.serialization.dj_sections_state_scale
    PROPERTIES TIMEOUT 15)
add_test(
    NAME apta.serialization.dj_sections_id_scale
    COMMAND apta_dj_sections_state_scale id-scale)
set_tests_properties(
    apta.serialization.dj_sections_id_scale
    PROPERTIES TIMEOUT 15)
add_test(
    NAME apta.serialization.dj_sections_grid_scale
    COMMAND apta_dj_sections_state_scale grid-scale)
set_tests_properties(
    apta.serialization.dj_sections_grid_scale
    PROPERTIES TIMEOUT 3)
apta_add_c_test(
    apta_dj_sections_allocation_failure
    apta.serialization.dj_sections_allocation_failure
    unit/dj_sections_allocation_failure.c)
target_compile_definitions(
    apta_dj_sections_allocation_failure
    PRIVATE
        APTA_DJ_GOLDEN_HEX_PATH="${CMAKE_SOURCE_DIR}/tests/fixtures/dj-sections-v1-combined.apta.hex")
apta_add_c_test(
    apta_streaming_container_io
    apta.serialization.streaming_container_io
    unit/streaming_container_io.c)
target_compile_definitions(
    apta_streaming_container_io
    PRIVATE
        APTA_DJ_GOLDEN_HEX_PATH="${CMAKE_SOURCE_DIR}/tests/fixtures/dj-sections-v1-combined.apta.hex")
add_executable(
    apta_compat_1_0_container_skip
    compat/1.0.0/frozen_container_consumer.c)
target_compile_definitions(
    apta_compat_1_0_container_skip
    PRIVATE
        APTA_DJ_GOLDEN_HEX_PATH="${CMAKE_SOURCE_DIR}/tests/fixtures/dj-sections-v1-combined.apta.hex")
set_target_properties(
    apta_compat_1_0_container_skip
    PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)
add_test(
    NAME apta.compat.1_0_container_skip
    COMMAND apta_compat_1_0_container_skip)

add_executable(
    apta_espidf_port
    unit/espidf_port.c
    ${CMAKE_SOURCE_DIR}/ports/espidf/apta_espidf.c)
target_link_libraries(apta_espidf_port PRIVATE apta::core)
target_include_directories(
    apta_espidf_port
    PRIVATE
        ${CMAKE_SOURCE_DIR}/ports/espidf/include
        ${CMAKE_CURRENT_SOURCE_DIR}/stubs/espidf)
target_compile_definitions(apta_espidf_port PRIVATE CONFIG_APTA_ESP_DSP_BACKEND=0)
set_target_properties(apta_espidf_port PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)
add_test(NAME apta.port.espidf COMMAND apta_espidf_port)

# The producer for this committed fixture is the standalone Python script in
# tests/fixtures, so consuming it here verifies the container contract without
# sharing writer code. In Stage S8 this same test executes on Windows as the
# cross-platform interchange gate.
add_executable(apta_external_fixture unit/external_fixture.c)
target_link_libraries(apta_external_fixture PRIVATE apta::core)
target_compile_definitions(
    apta_external_fixture
    PRIVATE
        APTA_EXTERNAL_FIXTURE_HEX_PATH="${CMAKE_SOURCE_DIR}/tests/fixtures/reference-wovr-meta.apta.hex")
set_target_properties(
    apta_external_fixture
    PROPERTIES
        C_STANDARD 11
        C_STANDARD_REQUIRED YES)
add_test(NAME apta.interchange.external_fixture COMMAND apta_external_fixture)

find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
    add_test(
        NAME apta.compat.1_0_container_negative
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/compat/1.0.0/legacy_container_negative.py
            $<TARGET_FILE:apta_compat_1_0_container_skip>
            ${CMAKE_SOURCE_DIR}/tests/fixtures/dj-sections-v1-combined.apta.hex)
    add_test(
        NAME apta.serialization.dj_fuzz_seed_manifest
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/unit/dj_fuzz_seed_manifest.py
            ${CMAKE_CURRENT_SOURCE_DIR}/fuzz/corpus-v1.json)
    add_test(
        NAME apta.tools.rekordbox_tempo_corpus
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/unit/rekordbox_tempo_corpus.py)
    add_test(
        NAME apta.tools.dj_candidate_comparison
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/unit/apta_1_1_compare_dj_candidates.py)
    if(APTA_ENABLE_EXPERIMENTAL_SPECTRAL_FLUX_I9)
        add_test(
            NAME apta.experimental.spectral_flux_i9_oracle
            COMMAND
                ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/unit/apta_1_1_onset_trace_i9.py)
    endif()
    if(APTA_ENABLE_EXPERIMENTAL_COMPLEX_DEVIATION_I10)
        add_test(
            NAME apta.experimental.complex_deviation_i10_oracle
            COMMAND
                ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/unit/apta_1_1_onset_trace_i10.py)
    endif()
endif()

if(TARGET apta_decoder_wav)
    apta_add_desktop_test(apta_desktop_native_file apta.desktop.native_file unit/desktop_native_file.c)
    if(TARGET apta_port_posix)
        apta_add_desktop_test(apta_desktop_posix_file apta.desktop.posix_file unit/desktop_posix_file.c)
    endif()
    apta_add_desktop_test(apta_desktop_wav_decoder apta.desktop.wav_decoder unit/desktop_wav_decoder.c)
    apta_add_desktop_test(apta_desktop_wav_malformed apta.desktop.wav_malformed unit/desktop_wav_malformed.c)
    apta_add_desktop_test(apta_desktop_wav_pull apta.desktop.wav_pull unit/desktop_wav_pull_integration.c)
endif()

if(TARGET apta_version)
    add_test(NAME apta.api.version_report COMMAND apta_version)
    set_tests_properties(
        apta.api.version_report
        PROPERTIES
            PASS_REGULAR_EXPRESSION
                "package=1.0.1.*api=1.0.0.*spec=1.0.*container=1")
endif()

if(TARGET apta_tool_common)
    add_executable(apta_tool_features_all unit/tool_features_all.c)
    target_link_libraries(apta_tool_features_all PRIVATE apta_tool_common)
    set_target_properties(
        apta_tool_features_all
        PROPERTIES
            C_STANDARD 11
            C_STANDARD_REQUIRED YES)
    add_test(NAME apta.tools.features_all COMMAND apta_tool_features_all)

    add_executable(apta_tool_sections_all unit/tool_sections_all.c)
    target_link_libraries(apta_tool_sections_all PRIVATE apta_tool_common)
    set_target_properties(
        apta_tool_sections_all
        PROPERTIES
            C_STANDARD 11
            C_STANDARD_REQUIRED YES)
    add_test(NAME apta.tools.sections_all COMMAND apta_tool_sections_all)

    add_executable(apta_tool_dj_sections unit/tool_dj_sections.c)
    target_link_libraries(apta_tool_dj_sections PRIVATE apta_tool_common)
    set_target_properties(
        apta_tool_dj_sections
        PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES)
    add_test(NAME apta.tools.dj_sections COMMAND apta_tool_dj_sections)
endif()

if(TARGET apta_analyze AND TARGET apta_inspect AND TARGET apta_validate)
    set(APTA_CLI_WAV "${CMAKE_CURRENT_BINARY_DIR}/apta-cli-click.wav")
    set(APTA_CLI_CONTAINER "${CMAKE_CURRENT_BINARY_DIR}/apta-cli-result.apta")
    set(APTA_CLI_CORRUPT "${CMAKE_CURRENT_BINARY_DIR}/apta-cli-corrupt.apta")

    add_executable(apta_desktop_cli_fixture unit/desktop_cli_fixture.c)
    if(UNIX)
        target_compile_definitions(apta_desktop_cli_fixture PRIVATE _POSIX_C_SOURCE=200809L)
    endif()
    set_target_properties(
        apta_desktop_cli_fixture
        PROPERTIES
            C_STANDARD 11
            C_STANDARD_REQUIRED YES)

    add_test(
        NAME apta.tools.fixture_wav
        COMMAND apta_desktop_cli_fixture wav ${APTA_CLI_WAV})
    set_tests_properties(
        apta.tools.fixture_wav
        PROPERTIES
            FIXTURES_SETUP apta_cli_wav)

    add_test(
        NAME apta.tools.analyze
        COMMAND apta_analyze ${APTA_CLI_WAV}
                --output ${APTA_CLI_CONTAINER}
                --profile performance)
    set_tests_properties(
        apta.tools.analyze
        PROPERTIES
            FIXTURES_REQUIRED apta_cli_wav
            FIXTURES_SETUP apta_cli_container
            PASS_REGULAR_EXPRESSION "analyzed")

    add_test(
        NAME apta.tools.analyze_reproducibility
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/unit/apta_analyze_reproducibility.py
            $<TARGET_FILE:apta_analyze>
            $<TARGET_FILE:apta_inspect>
            ${APTA_CLI_WAV})
    set_tests_properties(
        apta.tools.analyze_reproducibility
        PROPERTIES FIXTURES_REQUIRED apta_cli_wav)

    add_test(
        NAME apta.tools.validate_strict
        COMMAND apta_validate ${APTA_CLI_CONTAINER} --strict)
    set_tests_properties(
        apta.tools.validate_strict
        PROPERTIES
            FIXTURES_REQUIRED apta_cli_container
            PASS_REGULAR_EXPRESSION "valid:")

    add_test(
        NAME apta.tools.inspect_json
        COMMAND apta_inspect ${APTA_CLI_CONTAINER} --json --section TEMP)
    set_tests_properties(
        apta.tools.inspect_json
        PROPERTIES
            FIXTURES_REQUIRED apta_cli_container
            PASS_REGULAR_EXPRESSION "tempo_millibpm.*candidates")

    add_test(
        NAME apta.tools.fixture_corrupt
        COMMAND apta_desktop_cli_fixture truncate
                ${APTA_CLI_CONTAINER} ${APTA_CLI_CORRUPT})
    set_tests_properties(
        apta.tools.fixture_corrupt
        PROPERTIES
            FIXTURES_REQUIRED apta_cli_container
            FIXTURES_SETUP apta_cli_corrupt)

    add_test(
        NAME apta.tools.reject_corrupt
        COMMAND apta_validate ${APTA_CLI_CORRUPT} --strict --quiet)
    set_tests_properties(
        apta.tools.reject_corrupt
        PROPERTIES
            FIXTURES_REQUIRED apta_cli_corrupt
            WILL_FAIL TRUE)
endif()

apta_add_c_test(apta_memory_requirements apta.memory.requirements unit/memory_requirements.c)
apta_add_c_test(apta_static_workspace apta.memory.static_workspace unit/static_workspace.c)
apta_add_c_test(apta_static_workspace_metadata apta.memory.static_workspace_metadata unit/static_workspace_metadata.c)
apta_add_c_test(apta_result_pool_layout apta.memory.result_pool_layout unit/result_pool_layout.c)
apta_add_c_test(apta_result_pool_storage apta.memory.result_pool_storage unit/result_pool_storage.c)
target_link_libraries(apta_result_pool_storage PRIVATE apta_c11_atomics)
target_include_directories(apta_result_pool_storage PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_result_pool_empty_result apta.result.pool_empty_result unit/result_pool_empty_result.c)
target_link_libraries(apta_result_pool_empty_result PRIVATE apta_c11_atomics)
target_include_directories(apta_result_pool_empty_result PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_bounded_session_initial_result apta.session.bounded_initial_result unit/bounded_session_initial_result.c)
apta_add_c_test(apta_bounded_waveform_publication apta.result.bounded_waveform_publication unit/bounded_waveform_publication.c)
apta_add_c_test(apta_bounded_pool_capacity apta.memory.bounded_pool_capacity unit/bounded_pool_capacity.c)
apta_add_cpp_test(apta_bounded_result_concurrency apta.result.bounded_concurrency unit/bounded_result_concurrency.cpp)
apta_add_c_test(apta_publication_retry apta.result.publication_retry unit/publication_retry.c)

apta_add_c_test(apta_wovr_writer apta.serialization.wovr_writer unit/wovr_writer.c)
apta_add_c_test(apta_wovr_writer_partial apta.serialization.wovr_writer_partial unit/wovr_writer_partial.c)
apta_add_c_test(apta_wovr_roundtrip apta.serialization.wovr_roundtrip unit/wovr_roundtrip.c)
target_link_libraries(apta_wovr_roundtrip PRIVATE apta_c11_atomics)
target_include_directories(apta_wovr_roundtrip PRIVATE ${CMAKE_SOURCE_DIR}/src/core)
apta_add_c_test(apta_wovr_reader_malformed apta.serialization.wovr_reader_malformed unit/wovr_reader_malformed.c)
apta_add_c_test(apta_wovr_reader_hardening apta.serialization.wovr_reader_hardening unit/wovr_reader_hardening.c)
apta_add_c_test(apta_wovr_reader_allocation_failure apta.serialization.wovr_reader_allocation_failure unit/wovr_reader_allocation_failure.c)
apta_add_c_test(apta_wdtl_roundtrip apta.serialization.wdtl_roundtrip unit/wdtl_roundtrip.c)
apta_add_c_test(apta_wdtl_reader_malformed apta.serialization.wdtl_reader_malformed unit/wdtl_reader_malformed.c)
apta_add_c_test(apta_wdtl_reader_allocation_failure apta.serialization.wdtl_reader_allocation_failure unit/wdtl_reader_allocation_failure.c)
apta_add_c_test(apta_meta_roundtrip apta.serialization.meta_roundtrip unit/meta_roundtrip.c)
apta_add_c_test(apta_meta_wdtl_roundtrip apta.serialization.meta_wdtl_roundtrip unit/meta_wdtl_roundtrip.c)
apta_add_c_test(apta_meta_reader_malformed apta.serialization.meta_reader_malformed unit/meta_reader_malformed.c)
apta_add_c_test(apta_meta_allocation_failure apta.serialization.meta_allocation_failure unit/meta_allocation_failure.c)
apta_add_c_test(apta_container_truncation apta.serialization.container_truncation unit/container_truncation.c)

apta_add_cpp_test(apta_result_concurrency apta.result.concurrency unit/result_concurrency.cpp)
apta_add_cpp_test(apta_cancellation_thread apta.core.cancellation_thread unit/cancellation_thread.cpp)

if(APTA_BUILD_FUZZING)
    if(NOT CMAKE_C_COMPILER_ID MATCHES "Clang")
        message(FATAL_ERROR "APTA_BUILD_FUZZING requires Clang and libFuzzer")
    endif()

    add_executable(apta_wovr_seed_generator fuzz/wovr_seed_generator.c)
    target_link_libraries(apta_wovr_seed_generator PRIVATE apta::core)
    set_target_properties(
        apta_wovr_seed_generator
        PROPERTIES
            C_STANDARD 11
            C_STANDARD_REQUIRED YES)

    add_executable(apta_s6_seed_generator fuzz/s6_seed_generator.c)
    target_link_libraries(apta_s6_seed_generator PRIVATE apta::core)
    set_target_properties(
        apta_s6_seed_generator
        PROPERTIES
            C_STANDARD 11
            C_STANDARD_REQUIRED YES)

    add_executable(apta_wovr_reader_fuzz fuzz/wovr_reader_fuzz.c)
    target_link_libraries(apta_wovr_reader_fuzz PRIVATE apta::core)
    target_compile_options(apta_wovr_reader_fuzz PRIVATE -fsanitize=fuzzer)
    target_link_options(apta_wovr_reader_fuzz PRIVATE -fsanitize=fuzzer)
    set_target_properties(
        apta_wovr_reader_fuzz
        PROPERTIES
            C_STANDARD 11
            C_STANDARD_REQUIRED YES)
endif()

# C3: tests pinned to the default overview geometry.
#
# These assert exact serialized container sizes, exact fixture byte counts, or
# allocator call counts at the documented default geometry. They are
# interchange and layout conformance evidence, and rewriting them to derive
# their expectations from the configured geometry would make them assert that
# the writer wrote what the writer computed -- circular, and much weaker than
# what they check today.
#
# A build with a non-default capacity override therefore excludes them:
#
#   cmake -S . -B build-ov256 -DCMAKE_BUILD_TYPE=Release \
#         -DCMAKE_C_FLAGS=-DAPTA_INTERNAL_OVERVIEW_FRAMES_PER_COLUMN=256u \
#         -DCMAKE_CXX_FLAGS=-DAPTA_INTERNAL_OVERVIEW_FRAMES_PER_COLUMN=256u
#   cmake --build build-ov256 --parallel
#   ctest --test-dir build-ov256 -LE default_geometry --output-on-failure
#
# Everything outside this label must pass at any supported override.
set_tests_properties(
    apta.serialization.wovr_writer
    apta.serialization.wovr_writer_partial
    apta.serialization.wovr_roundtrip
    apta.serialization.wovr_reader_malformed
    apta.serialization.wdtl_roundtrip
    apta.serialization.wdtl_reader_malformed
    apta.serialization.wdtl_reader_allocation_failure
    apta.serialization.s4_allocation_failure
    apta.memory.static_workspace
    apta.memory.result_pool_storage
    apta.result.bounded_waveform_publication
    apta.result.publication_retry
    PROPERTIES LABELS default_geometry)

# Stage S9 P2 public API/ABI freeze gates.
find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_executable(apta_abi_layout_manifest abi/layout_manifest.c)
target_link_libraries(apta_abi_layout_manifest PRIVATE apta::headers)
set_target_properties(
    apta_abi_layout_manifest
    PROPERTIES
        C_STANDARD 11
        C_STANDARD_REQUIRED YES
        C_EXTENSIONS NO)

if(CMAKE_SIZEOF_VOID_P EQUAL 4)
    include(CheckCSourceCompiles)
    if(DEFINED CMAKE_TRY_COMPILE_TARGET_TYPE)
        set(_APTA_HAD_TRY_COMPILE_TARGET_TYPE TRUE)
        set(_APTA_SAVED_TRY_COMPILE_TARGET_TYPE
            "${CMAKE_TRY_COMPILE_TARGET_TYPE}")
    endif()
    set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
    check_c_source_compiles(
        "#include <stdint.h>
         _Static_assert(_Alignof(uint64_t) == 8, \"not p32a64\");
         int apta_probe(void) { return 0; }"
        APTA_ABI_POINTER32_ALIGN64)
    if(_APTA_HAD_TRY_COMPILE_TARGET_TYPE)
        set(CMAKE_TRY_COMPILE_TARGET_TYPE
            "${_APTA_SAVED_TRY_COMPILE_TARGET_TYPE}")
    else()
        unset(CMAKE_TRY_COMPILE_TARGET_TYPE)
    endif()
    unset(_APTA_HAD_TRY_COMPILE_TARGET_TYPE)
    unset(_APTA_SAVED_TRY_COMPILE_TARGET_TYPE)
    if(APTA_ABI_POINTER32_ALIGN64)
        set(APTA_ABI_LAYOUT_MODEL p32a64)
    else()
        set(APTA_ABI_LAYOUT_MODEL ilp32)
    endif()
elseif(WIN32)
    set(APTA_ABI_LAYOUT_MODEL llp64)
else()
    set(APTA_ABI_LAYOUT_MODEL lp64)
endif()

add_test(
    NAME apta.abi.public_layout
    COMMAND
        ${Python3_EXECUTABLE}
        ${CMAKE_CURRENT_SOURCE_DIR}/abi/check_layout_manifest.py
        --probe $<TARGET_FILE:apta_abi_layout_manifest>
        --manifest
        ${CMAKE_SOURCE_DIR}/abi/public-layout-${APTA_ABI_LAYOUT_MODEL}.txt)

add_test(
    NAME apta.abi.header_snapshot
    COMMAND
        ${Python3_EXECUTABLE}
        ${CMAKE_CURRENT_SOURCE_DIR}/abi/check_header_snapshot.py
        --live ${CMAKE_SOURCE_DIR}/include/apta
        --snapshot ${CMAKE_CURRENT_SOURCE_DIR}/compat/1.0.0/include/apta
        --delta-manifest
        ${CMAKE_SOURCE_DIR}/abi/public-header-deltas-1.1.sha256)

add_executable(apta_compat_1_0_client compat/1.0.0/client.c)
target_include_directories(
    apta_compat_1_0_client
    BEFORE
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/compat/1.0.0/include)
target_link_libraries(apta_compat_1_0_client PRIVATE apta::core)
set_target_properties(
    apta_compat_1_0_client
    PROPERTIES
        C_STANDARD 11
        C_STANDARD_REQUIRED YES
        C_EXTENSIONS NO)
add_test(NAME apta.abi.old_header_new_library COMMAND apta_compat_1_0_client)

if(BUILD_SHARED_LIBS)
    add_test(
        NAME apta.abi.public_symbols
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/abi/check_symbols.py
            --library $<TARGET_FILE:apta_core>
            --manifest ${CMAKE_SOURCE_DIR}/abi/public-symbols-1.1.txt)
endif()
