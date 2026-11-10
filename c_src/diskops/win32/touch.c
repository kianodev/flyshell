// c_src/diskops/win32/touch.c

#include <windows.h>
#include <stdlib.h>
#include "../shared/native_errors.h"

Result touch(const char* path) {
    if (!path || path[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    int wlen = MultiByteToWideChar(CP_UTF8, 0, path, -1, NULL, 0);
    if (wlen <= 0) {
        return ERR_INVALID_PATH;
    }

    wchar_t* wpath = (wchar_t*)malloc(wlen * sizeof(wchar_t));
    if (!wpath) {
        return ERR_IO;
    }
    MultiByteToWideChar(CP_UTF8, 0, path, -1, wpath, wlen);

    DWORD attrs = GetFileAttributesW(wpath);
    if (attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_DIRECTORY)) {
        free(wpath);
        return ERR_IS_DIR;
    }

    HANDLE hFile = CreateFileW(
        wpath,
        FILE_WRITE_ATTRIBUTES,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        DWORD err = GetLastError();
        free(wpath);
        return map_win32_error(err);
    }
    free(wpath);

    FILETIME ft;
    SYSTEMTIME st;
    GetSystemTime(&st);
    SystemTimeToFileTime(&st, &ft);
    SetFileTime(hFile, NULL, &ft, &ft);

    CloseHandle(hFile);
    return SUCCESS;
}
