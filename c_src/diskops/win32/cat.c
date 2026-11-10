// c_src/diskops/win32/cat.c

#include <windows.h>
#include <stdlib.h>
#include "../shared/native_errors.h"

Result cat(const char* path, char** out_buf, size_t* out_size) {
    if (!path || !out_buf || !out_size) {
        return ERR_INVALID_PATH;
    }
    *out_buf = NULL;
    *out_size = 0;

    int wlen = MultiByteToWideChar(CP_UTF8, 0, path, -1, NULL, 0);
    if (wlen <= 0) {
        return ERR_INVALID_PATH;
    }

    wchar_t* wpath = (wchar_t*)malloc(wlen * sizeof(wchar_t));
    if (!wpath) {
        return ERR_IO;
    }
    MultiByteToWideChar(CP_UTF8, 0, path, -1, wpath, wlen);

    HANDLE hFile = CreateFileW(
        wpath,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

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
    if (!GetFileSizeEx(hFile, &size)) {
        DWORD err = GetLastError();
        CloseHandle(hFile);
        return map_win32_error(err);
    }

    if (size.QuadPart == 0) {
        CloseHandle(hFile);
        return ERR_EMPTY;
    }

    char* buf = (char*)malloc(size.QuadPart + 1);
    if (!buf) {
        CloseHandle(hFile);
        return ERR_IO;
    }

    DWORD bytes_read = 0;
    BOOL ok = ReadFile(hFile, buf, (DWORD)size.QuadPart, &bytes_read, NULL);
    DWORD read_err = GetLastError();
    CloseHandle(hFile);

    if (!ok) {
        free(buf);
        return map_win32_error(read_err);
    }

    buf[bytes_read] = '\0';
    *out_buf = buf;
    *out_size = (size_t)bytes_read;
    return SUCCESS;
}
