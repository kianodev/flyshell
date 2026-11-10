// c_src/diskops/posix/cat.c

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include "../shared/native_errors.h"

Result cat(const char* path, char** out_buf, size_t* out_size) {
    if (!path || !out_buf || !out_size) {
        return ERR_INVALID_PATH;
    }
    *out_buf = NULL;
    *out_size = 0;

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return map_posix_errno(errno);
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        int err = errno;
        close(fd);
        return map_posix_errno(err);
    }

    if (S_ISDIR(st.st_mode)) {
        close(fd);
        return ERR_IS_DIR;
    }

    if (st.st_size == 0) {
        close(fd);
        return ERR_EMPTY;
    }

    char* buf = (char*)malloc(st.st_size + 1);
    if (!buf) {
        close(fd);
        return ERR_IO;
    }

    ssize_t n = read(fd, buf, st.st_size);
    int read_err = errno;
    close(fd);

    if (n < 0) {
        free(buf);
        return map_posix_errno(read_err);
    }

    buf[n] = '\0';
    *out_buf = buf;
    *out_size = (size_t)n;
    return SUCCESS;
}
