// c_src/diskops/posix/cat.c

#include "../shared/native_errors.h"
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

#define CAT_CHUNK_SIZE 32768

Result cat(const char *path, char **out_buf, size_t *out_size) {
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

    size_t capacity = (st.st_size > 0) ? ((size_t)st.st_size + 1) : CAT_CHUNK_SIZE;
    char *buf = (char *)malloc(capacity);
    if (!buf) {
        close(fd);
        return ERR_IO;
    }

    size_t total_read = 0;
    for (;;) {
        if (total_read + CAT_CHUNK_SIZE + 1 > capacity) {
            size_t new_cap = capacity * 2;
            if (new_cap < total_read + CAT_CHUNK_SIZE + 1) {
                new_cap = total_read + CAT_CHUNK_SIZE + 1;
            }
            char *resized = (char *)realloc(buf, new_cap);
            if (!resized) {
                close(fd);
                free(buf);
                return ERR_IO;
            }
            buf = resized;
            capacity = new_cap;
        }

        ssize_t n = read(fd, buf + total_read, CAT_CHUNK_SIZE);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            int read_err = errno;
            close(fd);
            free(buf);
            return map_posix_errno(read_err);
        }
        if (n == 0) {
            break;
        }
        total_read += (size_t)n;
    }
    close(fd);

    if (total_read == 0) {
        free(buf);
        return ERR_EMPTY;
    }

    buf[total_read] = '\0';
    *out_buf = buf;
    *out_size = total_read;
    return SUCCESS;
}
