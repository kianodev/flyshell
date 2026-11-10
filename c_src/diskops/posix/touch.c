// c_src/diskops/posix/touch.c

#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include "../shared/native_errors.h"

Result touch(const char* path) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    struct stat st;
    if (stat(path, &st) == 0) {
        if (S_ISDIR(st.st_mode)) {
            return ERR_IS_DIR;
        }
        if (utimensat(AT_FDCWD, path, NULL, 0) != 0) {
            return map_posix_errno(errno);
        }
        return SUCCESS;
    }

    int fd = open(path, O_WRONLY | O_CREAT | O_NONBLOCK | O_NOCTTY, 0666);
    if (fd < 0) {
        return map_posix_errno(errno);
    }

    close(fd);
    return SUCCESS;
}
