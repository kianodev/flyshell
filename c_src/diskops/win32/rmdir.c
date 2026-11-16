// c_src/diskops/win32/rmdir.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

static Result remove_dir_recursive_win32(const wchar_t *wpath) {
    size_t wlen = wcslen(wpath);
    bool has_sep = (wlen > 0 && (wpath[wlen - 1] == L'\\' || wpath[wlen - 1] == L'/')) != 0;
    size_t pat_len = wlen + (has_sep ? 1 : 2) + 1;

    wchar_t *wpattern = (wchar_t *)malloc(pat_len * sizeof(wchar_t));
    if (!wpattern) {
        return ERR_IO;
    }

    memcpy(wpattern, wpath, wlen * sizeof(wchar_t));
    size_t pos = wlen;
    if (!has_sep) {
        wpattern[pos++] = L'\\';
    }
    wpattern[pos++] = L'*';
    wpattern[pos] = L'\0';

    WIN32_FIND_DATAW find_data;
    HANDLE h_find = FindFirstFileW(wpattern, &find_data);
    DWORD find_err = GetLastError();
    free(wpattern);

    if (h_find == INVALID_HANDLE_VALUE) {
        return map_win32_error(find_err);
    }

    do {
        if (wcscmp(find_data.cFileName, L".") == 0 || wcscmp(find_data.cFileName, L"..") == 0) {
            continue;
        }

        size_t name_len = wcslen(find_data.cFileName);
        size_t child_len = wlen + (has_sep ? 0 : 1) + name_len + 1;
        wchar_t *wchild = (wchar_t *)malloc(child_len * sizeof(wchar_t));
        if (!wchild) {
            FindClose(h_find);
            return ERR_IO;
        }

        memcpy(wchild, wpath, wlen * sizeof(wchar_t));
        size_t cpos = wlen;
        if (!has_sep) {
            wchild[cpos++] = L'\\';
        }
        memcpy(wchild + cpos, find_data.cFileName, (name_len + 1) * sizeof(wchar_t));

        bool is_dir = (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
        bool is_reparse = (find_data.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0;

        if ((find_data.dwFileAttributes & FILE_ATTRIBUTE_READONLY) != 0) {
            SetFileAttributesW(wchild, find_data.dwFileAttributes & ~FILE_ATTRIBUTE_READONLY);
        }

        Result child_res;
        if (is_dir && !is_reparse) {
            child_res = remove_dir_recursive_win32(wchild);
        } else if (is_dir) {
            child_res = (RemoveDirectoryW(wchild) != 0) ? SUCCESS : map_win32_error(GetLastError());
        } else {
            child_res = (DeleteFileW(wchild) != 0) ? SUCCESS : map_win32_error(GetLastError());
        }
        free(wchild);

        if (child_res != SUCCESS) {
            FindClose(h_find);
            return child_res;
        }
    } while (FindNextFileW(h_find, &find_data) != 0);

    DWORD loop_err = GetLastError();
    FindClose(h_find);

    if (loop_err != ERROR_NO_MORE_FILES && loop_err != ERROR_SUCCESS) {
        return map_win32_error(loop_err);
    }

    if (RemoveDirectoryW(wpath) == 0) {
        return map_win32_error(GetLastError());
    }
    return SUCCESS;
}

Result remove_dir(const char *path, bool force) {
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
    if ((attrs & FILE_ATTRIBUTE_DIRECTORY) == 0) {
        free(wpath);
        return ERR_NOT_DIR;
    }

    if (!force) {
        BOOL ok = RemoveDirectoryW(wpath);
        DWORD err = GetLastError();
        free(wpath);
        if (ok == 0) {
            return map_win32_error(err);
        }
        return SUCCESS;
    }

    if ((attrs & FILE_ATTRIBUTE_READONLY) != 0) {
        SetFileAttributesW(wpath, attrs & ~FILE_ATTRIBUTE_READONLY);
    }

    Result res = remove_dir_recursive_win32(wpath);
    free(wpath);
    return res;
}
