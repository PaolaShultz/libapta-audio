// SPDX-License-Identifier: Apache-2.0
/* Diagnostic stdin: repeated 12 little-endian float32 + uint32 window count.
 * stdout: one JSON result per record. No alternate ranking implementation. */
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "apta_key_internal.h"
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

int main(int argc, char **argv)
{
    const uint32_t one = 1;
    unsigned char record[52];
    size_t n;
    if (argc != 2 || strcmp(argv[1], "--binary") || sizeof(float) != 4 ||
        FLT_RADIX != 2 || FLT_MANT_DIG != 24 || FLT_MAX_EXP != 128 ||
        *(const unsigned char *)&one != 1) return 2;
#ifdef _WIN32
    if (_setmode(_fileno(stdin), _O_BINARY) == -1) return 2;
#endif
    while ((n = fread(record, 1, sizeof(record), stdin)) != 0) {
        float chroma[12];
        uint32_t completed;
        apta_key_candidate_t candidates[3];
        apta_key_view_t view;
        apta_status_t status;
        unsigned p;
        if (n != sizeof(record)) return 2;
        memcpy(chroma, record, sizeof(chroma));
        memcpy(&completed, record + sizeof(chroma), sizeof(completed));
        for (p = 0; p < 12; ++p)
            if (!isfinite(chroma[p]) || chroma[p] < 0.0f) return 2;
        if (completed == 0) return 2;
        status = apta_internal_key_select_chroma(chroma, completed, candidates, &view);
        if (status == APTA_STATUS_NOT_AVAILABLE) { puts("{\"available\":false}"); continue; }
        if (status != APTA_STATUS_OK || view.candidate_count != 3) return 2;
        printf("{\"available\":true,\"tonic\":%u,\"mode\":%u,\"confidence\":%u,\"candidates\":[",
               (unsigned)view.tonic, view.mode == APTA_KEY_MODE_MAJOR ? 0u : 1u,
               (unsigned)view.confidence);
        for (p = 0; p < 3; ++p)
            printf("%s{\"tonic\":%u,\"mode\":%u,\"score\":%u}", p ? "," : "",
                   (unsigned)candidates[p].tonic,
                   candidates[p].mode == APTA_KEY_MODE_MAJOR ? 0u : 1u,
                   (unsigned)candidates[p].score);
        puts("]}");
    }
    return ferror(stdin) || ferror(stdout) ? 2 : 0;
}
