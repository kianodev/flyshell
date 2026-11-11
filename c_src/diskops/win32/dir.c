// c_src/diskops/win32/dir.c

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../shared/native_errors.h"
#include "../shared/dir_types.h"

Result list_dir(const char* path, DirList* out_list) {
    if (!path || path[0] == '\0' || !out_list) {
        return ERR_INVALID_PATH;
    }

    out_list->entries = NULL;
    out_list->count = 0;

    char search_pattern[MAX_PATH];
    snprintf(search_pattern, sizeof(search_pattern), "%s\\*", path);

    WIN32_FIND_DATAA find_data;
    HANDLE h_find = FindFirstFileA(search_pattern, &find_data);
    if (h_find == INVALID_HANDLE_VALUE) {
        return map_win32_error(GetLastError());
    }

    size_t capacity = 16;
    out_list->entries = (DirEntry*)malloc(capacity * sizeof(DirEntry));
    if (!out_list->entries) {
        FindClose(h_find);
        return ERR_IO;
    }

    do {
        if (strcmp(find_data.cFileName, ".") == 0 || strcmp(find_data.cFileName, "..") == 0) {
            continue;
        }

        if (out_list->count >= capacity) {
            capacity *= 2;
            DirEntry* resized = (DirEntry*)realloc(out_list->entries, capacity * sizeof(DirEntry));
            if (!resized) {
                FindClose(h_find);
                free_dir_list(out_list);
                return ERR_IO;
            }
            out_list->entries = resized;
        }

        bool is_dir = (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
        out_list->entries[out_list->count].name = _strdup(find_data.cFileName);
        out_list->entries[out_list->count].is_dir = is_dir;
        out_list->count++;
    } while (FindNextFileA(h_find, &find_data) != 0);

    DWORD err = GetLastError();
    FindClose(h_find);

    if (err != ERROR_NO_MORE_FILES && err != ERROR_SUCCESS) {
        free_dir_list(out_list);
        return map_win32_error(err);
    }

    return SUCCESS;
}