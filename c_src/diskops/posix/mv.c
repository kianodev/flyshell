// c_src/diskops/posix/mv.c

#include "../shared/native_errors.h"
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <sys/stat.h>

Result copy_item(const char *src, const char *dst, bool force);
Result remove_item(const char *path, bool recursive);

Result move_item(const char *src, const char *dst, bool force) {
    if (!src || src[0] == '\0' || !dst || dst[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    struct stat src_st;
    if (lstat(src, &src_st) != 0) {
        return map_posix_errno(errno);
    }

    struct stat dst_st;
    if (lstat(dst, &dst_st) == 0) {
        if (src_st.st_dev == dst_st.st_dev && src_st.st_ino == dst_st.st_ino) {
            return ERR_SAME_FILE;
        }
        if (!force) {
            return ERR_EXISTS;
        }
        if (S_ISDIR(dst_st.st_mode)) {
            Result rm_res = remove_item(dst, true);
            if (rm_res != SUCCESS) {
                return rm_res;
            }
        }
    }

    if (rename(src, dst) == 0) {
        return SUCCESS;
    }

    if (errno != EXDEV) {
        return map_posix_errno(errno);
    }

    Result cp_res = copy_item(src, dst, true);
    if (cp_res != SUCCESS) {
        return cp_res;
    }

    return remove_item(src, true);
}
