// c_src/diskops/posix/rmdir.c

#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#include "../shared/native_errors.h"
#include <dirent.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static Result remove_dir_recursive_posix(const char *path) {
    DIR *dir = opendir(path);
    if (!dir) {
        return map_posix_errno(errno);
    }

    size_t base_len = strlen(path);
    bool has_slash = (base_len > 0 && path[base_len - 1] == '/') != 0;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        size_t name_len = strlen(entry->d_name);
        size_t child_len = base_len + (has_slash ? 0 : 1) + name_len + 1;
        char *child_path = (char *)malloc(child_len);
        if (!child_path) {
            closedir(dir);
            return ERR_IO;
        }

        if (has_slash) {
            snprintf(child_path, child_len, "%s%s", path, entry->d_name);
        } else {
            snprintf(child_path, child_len, "%s/%s", path, entry->d_name);
        }

        struct stat st;
        if (lstat(child_path, &st) != 0) {
            int err = errno;
            free(child_path);
            closedir(dir);
            return map_posix_errno(err);
        }

        Result child_res;
        if (S_ISDIR(st.st_mode)) {
            child_res = remove_dir_recursive_posix(child_path);
        } else {
            child_res = (unlink(child_path) == 0) ? SUCCESS : map_posix_errno(errno);
        }
        free(child_path);

        if (child_res != SUCCESS) {
            closedir(dir);
            return child_res;
        }
    }

    closedir(dir);
    if (rmdir(path) != 0) {
        return map_posix_errno(errno);
    }
    return SUCCESS;
}

Result remove_dir(const char *path, bool force) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    struct stat st;
    if (lstat(path, &st) != 0) {
        return map_posix_errno(errno);
    }
    if (!S_ISDIR(st.st_mode)) {
        return ERR_NOT_DIR;
    }

    if (!force) {
        if (rmdir(path) != 0) {
            if (errno == EEXIST || errno == ENOTEMPTY) {
                return ERR_NOT_EMPTY;
            }
            return map_posix_errno(errno);
        }
        return SUCCESS;
    }

    return remove_dir_recursive_posix(path);
}
