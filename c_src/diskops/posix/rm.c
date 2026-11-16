// c_src/diskops/posix/rm.c

#include "../shared/native_errors.h"
#include <errno.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <unistd.h>

Result remove_dir(const char *path, bool force);

Result remove_item(const char *path, bool recursive) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    struct stat st;
    if (lstat(path, &st) != 0) {
        return map_posix_errno(errno);
    }

    if (S_ISDIR(st.st_mode)) {
        if (!recursive) {
            return ERR_IS_DIR;
        }
        return remove_dir(path, true);
    }

    if (unlink(path) != 0) {
        return map_posix_errno(errno);
    }

    return SUCCESS;
}
