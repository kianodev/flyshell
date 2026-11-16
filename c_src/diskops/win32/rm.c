// c_src/diskops/win32/rm.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdbool.h>
#include <stdlib.h>
#include <windows.h>

Result remove_dir(const char *path, bool force);

Result remove_item(const char *path, bool recursive) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    wchar_t *wpath = utf8_to_wide(path);
    if (!wpath) {
        return ERR_INVALID_PATH;
    }

    DWORD attrs = GetFileAttributesW(wpath);
    if (attrs == INVALID_FILE_ATTRIBUTES) {
        DWORD err = GetLastError();
        free(wpath);
        return map_win32_error(err);
    }

    bool is_dir = (attrs & FILE_ATTRIBUTE_DIRECTORY) != 0;
    bool is_reparse = (attrs & FILE_ATTRIBUTE_REPARSE_POINT) != 0;

    if (is_dir && !is_reparse) {
        free(wpath);
        if (!recursive) {
            return ERR_IS_DIR;
        }
        return remove_dir(path, true);
    }

    if ((attrs & FILE_ATTRIBUTE_READONLY) != 0) {
        SetFileAttributesW(wpath, attrs & ~FILE_ATTRIBUTE_READONLY);
    }

    BOOL ok = is_dir ? RemoveDirectoryW(wpath) : DeleteFileW(wpath);
    DWORD err = GetLastError();
    free(wpath);

    if (ok == 0) {
        return map_win32_error(err);
    }

    return SUCCESS;
}
