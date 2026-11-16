// c_src/diskops/posix/mkdir.c

#include "../shared/native_errors.h"
#include <errno.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

static Result make_single_dir_posix(const char *path, bool ignore_existing) {
    if (mkdir(path, 0777) == 0) {
        return SUCCESS;
    }
    if (errno == EEXIST && ignore_existing) {
        struct stat st;
        if (stat(path, &st) == 0 && S_ISDIR(st.st_mode)) {
            return SUCCESS;
        }
        return ERR_NOT_DIR;
    }
    return map_posix_errno(errno);
}

Result make_dir(const char *path, bool parents) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    if (!parents) {
        return make_single_dir_posix(path, false);
    }

    char *copy = strdup(path);
    if (!copy) {
        return ERR_IO;
    }

    size_t len = strlen(copy);
    while (len > 1 && copy[len - 1] == '/') {
        copy[--len] = '\0';
    }

    for (size_t i = 1; i < len; ++i) {
        if (copy[i] == '/') {
            copy[i] = '\0';
            Result res = make_single_dir_posix(copy, true);
            if (res != SUCCESS) {
                free(copy);
                return res;
            }
            copy[i] = '/';
        }
    }

    Result final_res = make_single_dir_posix(copy, true);
    free(copy);
    return final_res;
}
