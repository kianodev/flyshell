// c_src/diskops/shared/native_errors.h

#ifndef NATIVE_ERRORS_H
#define NATIVE_ERRORS_H

#include <errno.h>

#ifdef _WIN32
#include <windows.h>
#endif

typedef enum {
    SUCCESS = 0,
    ERR_NOT_FOUND = -1,
    ERR_PERMISSION = -2,
    ERR_IS_DIR = -3,
    ERR_NOT_DIR = -4,
    ERR_EXISTS = -5,
    ERR_NOT_EMPTY = -6,
    ERR_SAME_FILE = -7,
    ERR_EMPTY = -8,
    ERR_INVALID_PATH = -9,
    ERR_XDEV = -10,
    ERR_BUSY = -11,
    ERR_NO_SPACE = -12,
    ERR_IO = -13,
    ERR_DECODE = -14,
    ERR_LAUNCH_FAIL = -15,
    ERR_UNKNOWN = -99
} Result;

static inline Result map_posix_errno(int err) {
    switch (err) {
        case 0: return SUCCESS;
        case ENOENT: return ERR_NOT_FOUND;
        case EACCES:
        case EPERM: return ERR_PERMISSION;
        case EISDIR: return ERR_IS_DIR;
        case ENOTDIR: return ERR_NOT_DIR;
        case EEXIST: return ERR_EXISTS;
        case ENOTEMPTY: return ERR_NOT_EMPTY;
        case EXDEV: return ERR_XDEV;
        case EBUSY: return ERR_BUSY;
        case ENOSPC:
#ifdef EDQUOT
        case EDQUOT:
#endif
            return ERR_NO_SPACE;
        case EINVAL:
        case ENAMETOOLONG: return ERR_INVALID_PATH;
        case EIO: return ERR_IO;
        default: return ERR_UNKNOWN;
    }
}

#ifdef _WIN32
static inline Result map_win32_error(DWORD err) {
    switch (err) {
        case ERROR_SUCCESS: return SUCCESS;
        case ERROR_FILE_NOT_FOUND:
        case ERROR_PATH_NOT_FOUND: return ERR_NOT_FOUND;
        case ERROR_ACCESS_DENIED: return ERR_PERMISSION;
        case ERROR_DIRECTORY: return ERR_NOT_DIR;
        case ERROR_ALREADY_EXISTS:
        case ERROR_FILE_EXISTS: return ERR_EXISTS;
        case ERROR_DIR_NOT_EMPTY: return ERR_NOT_EMPTY;
        case ERROR_NOT_SAME_DEVICE: return ERR_XDEV;
        case ERROR_SHARING_VIOLATION:
        case ERROR_LOCK_VIOLATION:
        case ERROR_BUSY: return ERR_BUSY;
        case ERROR_DISK_FULL:
        case ERROR_HANDLE_DISK_FULL: return ERR_NO_SPACE;
        case ERROR_INVALID_NAME:
        case ERROR_FILENAME_EXCED_RANGE:
        case ERROR_BAD_PATHNAME: return ERR_INVALID_PATH;
        case ERROR_READ_FAULT:
        case ERROR_WRITE_FAULT:
        case ERROR_IO_DEVICE: return ERR_IO;
        default: return ERR_UNKNOWN;
    }
}
#endif

#endif /* NATIVE_ERRORS_H */