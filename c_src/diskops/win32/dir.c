// c_src/diskops/win32/dir.c

#include "../shared/dir_types.h"
#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdlib.h>
#include <string.h>
#include <windows.h>

Result list_dir(const char *path, DirList *out_list) {
    if (!path || path[0] == '\0' || !out_list) {
        return ERR_INVALID_PATH;
    }

    out_list->entries = NULL;
    out_list->count = 0;

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

    size_t wlen = wcslen(wpath);
    bool has_sep = (wlen > 0 && (wpath[wlen - 1] == L'\\' || wpath[wlen - 1] == L'/')) != 0;
    size_t pat_len = wlen + (has_sep ? 1 : 2) + 1;

    wchar_t *wpattern = (wchar_t *)malloc(pat_len * sizeof(wchar_t));
    if (!wpattern) {
        free(wpath);
        return ERR_IO;
    }

    memcpy(wpattern, wpath, wlen * sizeof(wchar_t));
    size_t pos = wlen;
    if (!has_sep) {
        wpattern[pos++] = L'\\';
    }
    wpattern[pos++] = L'*';
    wpattern[pos] = L'\0';
    free(wpath);

    WIN32_FIND_DATAW find_data;
    HANDLE h_find = FindFirstFileW(wpattern, &find_data);
    DWORD find_err = GetLastError();
    free(wpattern);

    if (h_find == INVALID_HANDLE_VALUE) {
        return map_win32_error(find_err);
    }

    size_t capacity = 16;
    out_list->entries = (DirEntry *)malloc(capacity * sizeof(DirEntry));
    if (!out_list->entries) {
        FindClose(h_find);
        return ERR_IO;
    }

    do {
        if (wcscmp(find_data.cFileName, L".") == 0 || wcscmp(find_data.cFileName, L"..") == 0) {
            continue;
        }

        if (out_list->count >= capacity) {
            capacity *= 2;
            DirEntry *resized = (DirEntry *)realloc(out_list->entries, capacity * sizeof(DirEntry));
            if (!resized) {
                FindClose(h_find);
                free_dir_list(out_list);
                return ERR_IO;
            }
            out_list->entries = resized;
        }

        char *utf8_name = wide_to_utf8(find_data.cFileName);
        if (!utf8_name) {
            FindClose(h_find);
            free_dir_list(out_list);
            return ERR_DECODE;
        }

        bool is_dir = (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
        out_list->entries[out_list->count].name = utf8_name;
        out_list->entries[out_list->count].is_dir = is_dir;
        out_list->count++;
    } while (FindNextFileW(h_find, &find_data) != 0);

    DWORD err = GetLastError();
    FindClose(h_find);

    if (err != ERROR_NO_MORE_FILES && err != ERROR_SUCCESS) {
        free_dir_list(out_list);
        return map_win32_error(err);
    }

    return SUCCESS;
}
