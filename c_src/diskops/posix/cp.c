// c_src/diskops/posix/cp.c

#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE

#include "../shared/native_errors.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define CP_CHUNK_SIZE 32768

static bool is_subpath_posix(const char *parent, const char *child) {
    char *real_parent = realpath(parent, NULL);
    if (!real_parent) {
        return false;
    }

    char *child_copy = strdup(child);
    if (!child_copy) {
        free(real_parent);
        return false;
    }

    char *slash = strrchr(child_copy, '/');
    char *real_child_parent = NULL;
    if (slash) {
        if (slash == child_copy) {
            real_child_parent = realpath("/", NULL);
        } else {
            *slash = '\0';
            real_child_parent = realpath(child_copy, NULL);
        }
    } else {
        real_child_parent = realpath(".", NULL);
    }
    free(child_copy);

    if (!real_child_parent) {
        free(real_parent);
        return false;
    }

    size_t plen = strlen(real_parent);
    bool sub = false;
    if (strcmp(real_parent, "/") == 0) {
        sub = true;
    } else if (strncmp(real_parent, real_child_parent, plen) == 0 &&
               (real_child_parent[plen] == '\0' || real_child_parent[plen] == '/')) {
        sub = true;
    }

    free(real_parent);
    free(real_child_parent);
    return sub;
}

static Result copy_file_posix(const char *src, const char *dst, const struct stat *src_st,
                              bool force) {
    struct stat dst_st;
    if (lstat(dst, &dst_st) == 0) {
        if (src_st->st_dev == dst_st.st_dev && src_st->st_ino == dst_st.st_ino) {
            return ERR_SAME_FILE;
        }
        if (S_ISDIR(dst_st.st_mode)) {
            return ERR_IS_DIR;
        }
        if (!force) {
            return ERR_EXISTS;
        }
    }

    int src_fd = open(src, O_RDONLY);
    if (src_fd < 0) {
        return map_posix_errno(errno);
    }

    int dst_fd = open(dst, O_WRONLY | O_CREAT | O_TRUNC, src_st->st_mode & 0777);
    if (dst_fd < 0) {
        int err = errno;
        close(src_fd);
        return map_posix_errno(err);
    }

    char *buf = (char *)malloc(CP_CHUNK_SIZE);
    if (!buf) {
        close(src_fd);
        close(dst_fd);
        return ERR_IO;
    }

    Result res = SUCCESS;
    for (;;) {
        ssize_t n_read = read(src_fd, buf, CP_CHUNK_SIZE);
        if (n_read < 0) {
            if (errno == EINTR) {
                continue;
            }
            res = map_posix_errno(errno);
            break;
        }
        if (n_read == 0) {
            break;
        }

        size_t written = 0;
        while (written < (size_t)n_read) {
            ssize_t n_written = write(dst_fd, buf + written, (size_t)n_read - written);
            if (n_written < 0) {
                if (errno == EINTR) {
                    continue;
                }
                res = map_posix_errno(errno);
                break;
            }
            written += (size_t)n_written;
        }
        if (res != SUCCESS) {
            break;
        }
    }

    free(buf);

    if (res == SUCCESS) {
        (void)fchmod(dst_fd, src_st->st_mode & 0777);
        struct timespec times[2];
#ifdef __APPLE__
        times[0] = src_st->st_atimespec;
        times[1] = src_st->st_mtimespec;
#else
        times[0] = src_st->st_atim;
        times[1] = src_st->st_mtim;
#endif
        (void)futimens(dst_fd, times);
    }

    close(src_fd);
    if (close(dst_fd) != 0 && res == SUCCESS) {
        res = map_posix_errno(errno);
    }
    return res;
}

static Result copy_dir_recursive_posix(const char *src, const char *dst, const struct stat *src_st,
                                       bool force) {
    struct stat dst_st;
    if (lstat(dst, &dst_st) == 0) {
        if (src_st->st_dev == dst_st.st_dev && src_st->st_ino == dst_st.st_ino) {
            return ERR_SAME_FILE;
        }
        if (!S_ISDIR(dst_st.st_mode)) {
            return ERR_NOT_DIR;
        }
        if (!force) {
            return ERR_EXISTS;
        }
    } else if (mkdir(dst, src_st->st_mode & 0777) != 0) {
        return map_posix_errno(errno);
    }

    DIR *dir = opendir(src);
    if (!dir) {
        return map_posix_errno(errno);
    }

    size_t src_len = strlen(src);
    size_t dst_len = strlen(dst);
    bool src_slash = (src_len > 0 && src[src_len - 1] == '/') != 0;
    bool dst_slash = (dst_len > 0 && dst[dst_len - 1] == '/') != 0;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        size_t name_len = strlen(entry->d_name);
        size_t s_child_len = src_len + (src_slash ? 0 : 1) + name_len + 1;
        size_t d_child_len = dst_len + (dst_slash ? 0 : 1) + name_len + 1;

        char *s_child = (char *)malloc(s_child_len);
        char *d_child = (char *)malloc(d_child_len);
        if (!s_child || !d_child) {
            free(s_child);
            free(d_child);
            closedir(dir);
            return ERR_IO;
        }

        snprintf(s_child, s_child_len, src_slash ? "%s%s" : "%s/%s", src, entry->d_name);
        snprintf(d_child, d_child_len, dst_slash ? "%s%s" : "%s/%s", dst, entry->d_name);

        struct stat child_st;
        if (stat(s_child, &child_st) != 0) {
            int err = errno;
            free(s_child);
            free(d_child);
            closedir(dir);
            return map_posix_errno(err);
        }

        Result res;
        if (S_ISDIR(child_st.st_mode)) {
            res = copy_dir_recursive_posix(s_child, d_child, &child_st, force);
        } else {
            res = copy_file_posix(s_child, d_child, &child_st, force);
        }

        free(s_child);
        free(d_child);

        if (res != SUCCESS) {
            closedir(dir);
            return res;
        }
    }

    closedir(dir);
    return SUCCESS;
}

Result copy_item(const char *src, const char *dst, bool force) {
    if (!src || src[0] == '\0' || !dst || dst[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    struct stat src_st;
    if (stat(src, &src_st) != 0) {
        return map_posix_errno(errno);
    }

    if (S_ISDIR(src_st.st_mode)) {
        if (is_subpath_posix(src, dst)) {
            return ERR_INVALID_PATH;
        }
        return copy_dir_recursive_posix(src, dst, &src_st, force);
    }

    return copy_file_posix(src, dst, &src_st, force);
}
