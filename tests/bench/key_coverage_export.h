// SPDX-License-Identifier: Apache-2.0
/* Host-only export of the exact decimation operation, before native feeding. */
#include <float.h>
static FILE *coverage_file;
static float coverage_samples[12000];
static unsigned coverage_count, coverage_records;
static uint64_t coverage_source_samples;

static int coverage_open(const char *path)
{
    const uint32_t one = 1u;
    CHECK(sizeof(float) == 4 && FLT_RADIX == 2 && FLT_MANT_DIG == 24 && FLT_MAX_EXP == 128);
    CHECK(*(const unsigned char *)&one == 1u);
    coverage_file = fopen(path, "wbx");
    CHECK(coverage_file != NULL);
    CHECK(fwrite("APTCOV01", 1, 8, coverage_file) == 8);
    return 0;
}

static int coverage_feed(const apta_session_t *session, float sample)
{
    ++coverage_source_samples;
    if (session->key_analysis.decimation_count == 3u) {
        const float sum = session->key_analysis.decimation_sum + sample;
        CHECK(coverage_count < 12000u);
        coverage_samples[coverage_count++] = sum / 4.0f;
    }
    return 0;
}

static int coverage_write(const apta_session_t *session, unsigned tonic,
                          unsigned mode, unsigned condition, unsigned window)
{
    const uint32_t metadata[4] = {tonic, mode, condition, window};
    CHECK(coverage_count == 12000u);
    CHECK(fwrite(metadata, sizeof(uint32_t), 4, coverage_file) == 4);
    CHECK(fwrite(session->key_analysis.coefficients[0], sizeof(float), 36, coverage_file) == 36);
    CHECK(fwrite(coverage_samples, sizeof(float), 12000, coverage_file) == 12000);
    coverage_count = 0;
    ++coverage_records;
    return 0;
}

static int coverage_close(void)
{
    CHECK(coverage_records == 576u && coverage_source_samples == UINT64_C(27648000));
    CHECK(fclose(coverage_file) == 0);
    return 0;
}
