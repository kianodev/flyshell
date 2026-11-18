// c_src/diskops/win32/mv.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdbool.h>
#include <stdlib.h>
#include <windows.h>

Result copy_item(const char *src, const char *dst, bool force);
Result remove_item(const char *path, bool recursive);

Result move_item(const char *src, const char *dst, bool force) {
    if (!src || src[0] == '\0' || !dst || dst[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    wchar_t *wsrc = utf8_to_wide(src);
    if (!wsrc) {
        return ERR_INVALID_PATH;
    }

    wchar_t *wdst = utf8_to_wide(dst);
    if (!wdst) {
        free(wsrc);
        return ERR_INVALID_PATH;
    }

    DWORD src_attrs = GetFileAttributesW(wsrc);
    if (src_attrs == INVALID_FILE_ATTRIBUTES) {
        DWORD err = GetLastError();
        free(wsrc);
        free(wdst);
        return map_win32_error(err);
    }

    DWORD dst_attrs = GetFileAttributesW(wdst);
    if (dst_attrs != INVALID_FILE_ATTRIBUTES) {
        if (!force) {
            free(wsrc);
            free(wdst);
            return ERR_EXISTS;
        }
        if ((dst_attrs & FILE_ATTRIBUTE_DIRECTORY) != 0) {
            Result rm_res = remove_item(dst, true);
            if (rm_res != SUCCESS) {
                free(wsrc);
                free(wdst);
                return rm_res;
            }
        }
    }

    DWORD flags = force ? MOVEFILE_REPLACE_EXISTING : 0;
    if (MoveFileExW(wsrc, wdst, flags) != 0) {
        free(wsrc);
        free(wdst);
        return SUCCESS;
    }

    DWORD err = GetLastError();
    free(wsrc);
    free(wdst);

    if (err != ERROR_NOT_SAME_DEVICE) {
        return map_win32_error(err);
    }

    Result cp_res = copy_item(src, dst, true);
    if (cp_res != SUCCESS) {
        return cp_res;
    }

    return remove_item(src, true);
}
