// c_src/diskops/win32/cat.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdlib.h>
#include <windows.h>

#define CAT_CHUNK_SIZE 32768

Result cat(const char *path, char **out_buf, size_t *out_size) {
    if (!path || !out_buf || !out_size) {
        return ERR_INVALID_PATH;
    }
    *out_buf = NULL;
    *out_size = 0;

    wchar_t *wpath = utf8_to_wide(path);
    if (!wpath) {
        return ERR_INVALID_PATH;
    }

    HANDLE hFile =
        CreateFileW(wpath, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                    NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

    if (hFile == INVALID_HANDLE_VALUE) {
        DWORD err = GetLastError();
        if (err == ERROR_ACCESS_DENIED) {
            DWORD attrs = GetFileAttributesW(wpath);
            if (attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_DIRECTORY)) {
                free(wpath);
                return ERR_IS_DIR;
            }
        }
        free(wpath);
        return map_win32_error(err);
    }
    free(wpath);

    LARGE_INTEGER size;
    size_t capacity = CAT_CHUNK_SIZE;
    if (GetFileSizeEx(hFile, &size) && size.QuadPart > 0) {
        if ((ULONGLONG)size.QuadPart > (ULONGLONG)(SIZE_MAX - 1)) {
            CloseHandle(hFile);
            return ERR_IO;
        }
        capacity = (size_t)size.QuadPart + 1;
    }

    char *buf = (char *)malloc(capacity);
    if (!buf) {
        CloseHandle(hFile);
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
                CloseHandle(hFile);
                free(buf);
                return ERR_IO;
            }
            buf = resized;
            capacity = new_cap;
        }

        DWORD bytes_read = 0;
        if (!ReadFile(hFile, buf + total_read, CAT_CHUNK_SIZE, &bytes_read, NULL)) {
            DWORD read_err = GetLastError();
            CloseHandle(hFile);
            free(buf);
            return map_win32_error(read_err);
        }
        if (bytes_read == 0) {
            break;
        }
        total_read += (size_t)bytes_read;
    }
    CloseHandle(hFile);

    if (total_read == 0) {
        free(buf);
        return ERR_EMPTY;
    }

    buf[total_read] = '\0';
    *out_buf = buf;
    *out_size = total_read;
    return SUCCESS;
}
