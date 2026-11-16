// c_src/diskops/win32/mkdir.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdbool.h>
#include <stdlib.h>
#include <windows.h>

static Result make_single_dir_win32(const wchar_t *wpath, bool ignore_existing) {
    if (CreateDirectoryW(wpath, NULL) != 0) {
        return SUCCESS;
    }
    DWORD err = GetLastError();
    if (err == ERROR_ALREADY_EXISTS && ignore_existing) {
        DWORD attrs = GetFileAttributesW(wpath);
        if (attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_DIRECTORY) != 0) {
            return SUCCESS;
        }
        return ERR_NOT_DIR;
    }
    return map_win32_error(err);
}

Result make_dir(const char *path, bool parents) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    wchar_t *wpath = utf8_to_wide(path);
    if (!wpath) {
        return ERR_INVALID_PATH;
    }

    if (!parents) {
        Result res = make_single_dir_win32(wpath, false);
        free(wpath);
        return res;
    }

    size_t len = wcslen(wpath);
    while (len > 1 && (wpath[len - 1] == L'\\' || wpath[len - 1] == L'/')) {
        if (len == 3 && wpath[1] == L':') {
            break;
        }
        wpath[--len] = L'\0';
    }

    size_t start = 1;
    if (len >= 3 && wpath[1] == L':' && (wpath[2] == L'\\' || wpath[2] == L'/')) {
        start = 3;
    } else if (len >= 2 && (wpath[0] == L'\\' || wpath[0] == L'/') &&
               (wpath[1] == L'\\' || wpath[1] == L'/')) {
        start = 2;
    }

    for (size_t i = start; i < len; ++i) {
        if (wpath[i] == L'\\' || wpath[i] == L'/') {
            wchar_t orig = wpath[i];
            wpath[i] = L'\0';
            Result res = make_single_dir_win32(wpath, true);
            if (res != SUCCESS) {
                free(wpath);
                return res;
            }
            wpath[i] = orig;
        }
    }

    Result final_res = make_single_dir_win32(wpath, true);
    free(wpath);
    return final_res;
}
