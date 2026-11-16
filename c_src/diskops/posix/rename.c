// c_src/diskops/posix/rename.c

#include "../shared/native_errors.h"
#include <errno.h>
#include <stdio.h>
#include <sys/stat.h>

Result rename_item(const char *src, const char *dst) {
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
        return ERR_EXISTS;
    }

    if (rename(src, dst) != 0) {
        return map_posix_errno(errno);
    }

    return SUCCESS;
}
