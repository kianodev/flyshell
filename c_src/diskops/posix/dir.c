// c_src/diskops/posix/dir.c

#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#include <dirent.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "../shared/native_errors.h"
#include "../shared/dir_types.h"

Result list_dir(const char* path, DirList* out_list) {
    if (!path || path[0] == '\0' || !out_list) {
        return ERR_INVALID_PATH;
    }

    out_list->entries = NULL;
    out_list->count = 0;

    DIR* dir = opendir(path);
    if (!dir) {
        return map_posix_errno(errno);
    }

    size_t capacity = 16;
    out_list->entries = (DirEntry*)malloc(capacity * sizeof(DirEntry));
    if (!out_list->entries) {
        closedir(dir);
        return ERR_IO;
    }

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        if (out_list->count >= capacity) {
            capacity *= 2;
            DirEntry* resized = (DirEntry*)realloc(out_list->entries, capacity * sizeof(DirEntry));
            if (!resized) {
                closedir(dir);
                free_dir_list(out_list);
                return ERR_IO;
            }
            out_list->entries = resized;
        }

        bool is_dir = false;
#ifdef _DIRENT_HAVE_D_TYPE
        if (entry->d_type != DT_UNKNOWN) {
            is_dir = (entry->d_type == DT_DIR);
        } else
#endif
        {
            struct stat st;
            if (fstatat(dirfd(dir), entry->d_name, &st, 0) == 0) {
                is_dir = S_ISDIR(st.st_mode);
            }
        }

        out_list->entries[out_list->count].name = strdup(entry->d_name);
        out_list->entries[out_list->count].is_dir = is_dir;
        out_list->count++;
    }

    closedir(dir);
    return SUCCESS;
}
