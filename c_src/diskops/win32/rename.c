// c_src/diskops/win32/rename.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdlib.h>
#include <windows.h>

Result rename_item(const char *src, const char *dst) {
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

    if (_wcsicmp(wsrc, wdst) == 0 && wcscmp(wsrc, wdst) == 0) {
        free(wsrc);
        free(wdst);
        return ERR_SAME_FILE;
    }

    DWORD dst_attrs = GetFileAttributesW(wdst);
    if (dst_attrs != INVALID_FILE_ATTRIBUTES) {
        free(wsrc);
        free(wdst);
        return ERR_EXISTS;
    }

    if (MoveFileW(wsrc, wdst) == 0) {
        DWORD err = GetLastError();
        free(wsrc);
        free(wdst);
        return map_win32_error(err);
    }

    free(wsrc);
    free(wdst);
    return SUCCESS;
}
