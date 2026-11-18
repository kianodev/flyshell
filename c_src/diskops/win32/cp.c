// c_src/diskops/win32/cp.c

#include "../shared/native_errors.h"
#include "../shared/win32_utf.h"
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

#define CP_CHUNK_SIZE 32768

static bool is_same_file_win32(const wchar_t *wsrc, const wchar_t *wdst) {
    HANDLE h1 = CreateFileW(wsrc, 0, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, NULL,
                            OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
    if (h1 == INVALID_HANDLE_VALUE) {
        return false;
    }

    HANDLE h2 = CreateFileW(wdst, 0, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, NULL,
                            OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
    if (h2 == INVALID_HANDLE_VALUE) {
        CloseHandle(h1);
        return false;
    }

    BY_HANDLE_FILE_INFORMATION info1;
    BY_HANDLE_FILE_INFORMATION info2;
    bool same = false;
    if (GetFileInformationByHandle(h1, &info1) != 0 &&
        GetFileInformationByHandle(h2, &info2) != 0) {
        same = (info1.dwVolumeSerialNumber == info2.dwVolumeSerialNumber &&
                info1.nFileIndexHigh == info2.nFileIndexHigh &&
                info1.nFileIndexLow == info2.nFileIndexLow) != 0;
    }

    CloseHandle(h1);
    CloseHandle(h2);
    return same;
}

static bool is_subpath_win32(const wchar_t *wsrc, const wchar_t *wdst) {
    DWORD src_len = GetFullPathNameW(wsrc, 0, NULL, NULL);
    DWORD dst_len = GetFullPathNameW(wdst, 0, NULL, NULL);
    if (src_len == 0 || dst_len == 0) {
        return false;
    }

    wchar_t *full_src = (wchar_t *)malloc((size_t)src_len * sizeof(wchar_t));
    wchar_t *full_dst = (wchar_t *)malloc((size_t)dst_len * sizeof(wchar_t));
    if (!full_src || !full_dst) {
        free(full_src);
        free(full_dst);
        return false;
    }

    GetFullPathNameW(wsrc, src_len, full_src, NULL);
    GetFullPathNameW(wdst, dst_len, full_dst, NULL);

    size_t slen = wcslen(full_src);
    while (slen > 3 && (full_src[slen - 1] == L'\\' || full_src[slen - 1] == L'/')) {
        full_src[--slen] = L'\0';
    }

    bool sub = false;
    if (_wcsnicmp(full_src, full_dst, slen) == 0 &&
        (full_dst[slen] == L'\0' || full_dst[slen] == L'\\' || full_dst[slen] == L'/')) {
        sub = true;
    }

    free(full_src);
    free(full_dst);
    return sub;
}

static Result copy_file_win32(const wchar_t *wsrc, const wchar_t *wdst, DWORD src_attrs,
                              bool force) {
    DWORD dst_attrs = GetFileAttributesW(wdst);
    if (dst_attrs != INVALID_FILE_ATTRIBUTES) {
        if (is_same_file_win32(wsrc, wdst)) {
            return ERR_SAME_FILE;
        }
        if ((dst_attrs & FILE_ATTRIBUTE_DIRECTORY) != 0) {
            return ERR_IS_DIR;
        }
        if (!force) {
            return ERR_EXISTS;
        }
        if ((dst_attrs & FILE_ATTRIBUTE_READONLY) != 0) {
            SetFileAttributesW(wdst, dst_attrs & ~FILE_ATTRIBUTE_READONLY);
        }
    }

    HANDLE h_src =
        CreateFileW(wsrc, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                    NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h_src == INVALID_HANDLE_VALUE) {
        return map_win32_error(GetLastError());
    }

    HANDLE h_dst = CreateFileW(wdst, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                               src_attrs & ~FILE_ATTRIBUTE_DIRECTORY, NULL);
    if (h_dst == INVALID_HANDLE_VALUE) {
        DWORD err = GetLastError();
        CloseHandle(h_src);
        return map_win32_error(err);
    }

    char *buf = (char *)malloc(CP_CHUNK_SIZE);
    if (!buf) {
        CloseHandle(h_src);
        CloseHandle(h_dst);
        return ERR_IO;
    }

    Result res = SUCCESS;
    for (;;) {
        DWORD bytes_read = 0;
        if (ReadFile(h_src, buf, CP_CHUNK_SIZE, &bytes_read, NULL) == 0) {
            res = map_win32_error(GetLastError());
            break;
        }
        if (bytes_read == 0) {
            break;
        }

        DWORD total_written = 0;
        while (total_written < bytes_read) {
            DWORD bytes_written = 0;
            if (WriteFile(h_dst, buf + total_written, bytes_read - total_written, &bytes_written,
                          NULL) == 0) {
                res = map_win32_error(GetLastError());
                break;
            }
            total_written += bytes_written;
        }
        if (res != SUCCESS) {
            break;
        }
    }

    free(buf);

    if (res == SUCCESS) {
        FILETIME ft_create;
        FILETIME ft_access;
        FILETIME ft_write;
        if (GetFileTime(h_src, &ft_create, &ft_access, &ft_write) != 0) {
            SetFileTime(h_dst, &ft_create, &ft_access, &ft_write);
        }
    }

    CloseHandle(h_src);
    CloseHandle(h_dst);
    return res;
}

static Result copy_dir_recursive_win32(const wchar_t *wsrc, const wchar_t *wdst, bool force) {
    DWORD dst_attrs = GetFileAttributesW(wdst);
    if (dst_attrs != INVALID_FILE_ATTRIBUTES) {
        if (is_same_file_win32(wsrc, wdst)) {
            return ERR_SAME_FILE;
        }
        if ((dst_attrs & FILE_ATTRIBUTE_DIRECTORY) == 0) {
            return ERR_NOT_DIR;
        }
        if (!force) {
            return ERR_EXISTS;
        }
    } else if (CreateDirectoryW(wdst, NULL) == 0) {
        return map_win32_error(GetLastError());
    }

    size_t slen = wcslen(wsrc);
    size_t dlen = wcslen(wdst);
    bool s_sep = (slen > 0 && (wsrc[slen - 1] == L'\\' || wsrc[slen - 1] == L'/')) != 0;
    bool d_sep = (dlen > 0 && (wdst[dlen - 1] == L'\\' || wdst[dlen - 1] == L'/')) != 0;

    size_t pat_len = slen + (s_sep ? 1 : 2) + 1;
    wchar_t *wpattern = (wchar_t *)malloc(pat_len * sizeof(wchar_t));
    if (!wpattern) {
        return ERR_IO;
    }

    memcpy(wpattern, wsrc, slen * sizeof(wchar_t));
    size_t ppos = slen;
    if (!s_sep) {
        wpattern[ppos++] = L'\\';
    }
    wpattern[ppos++] = L'*';
    wpattern[ppos] = L'\0';

    WIN32_FIND_DATAW find_data;
    HANDLE h_find = FindFirstFileW(wpattern, &find_data);
    DWORD find_err = GetLastError();
    free(wpattern);

    if (h_find == INVALID_HANDLE_VALUE) {
        return map_win32_error(find_err);
    }

    do {
        if (wcscmp(find_data.cFileName, L".") == 0 || wcscmp(find_data.cFileName, L"..") == 0) {
            continue;
        }

        size_t nlen = wcslen(find_data.cFileName);
        size_t sc_len = slen + (s_sep ? 0 : 1) + nlen + 1;
        size_t dc_len = dlen + (d_sep ? 0 : 1) + nlen + 1;

        wchar_t *ws_child = (wchar_t *)malloc(sc_len * sizeof(wchar_t));
        wchar_t *wd_child = (wchar_t *)malloc(dc_len * sizeof(wchar_t));
        if (!ws_child || !wd_child) {
            free(ws_child);
            free(wd_child);
            FindClose(h_find);
            return ERR_IO;
        }

        memcpy(ws_child, wsrc, slen * sizeof(wchar_t));
        size_t spos = slen;
        if (!s_sep) {
            ws_child[spos++] = L'\\';
        }
        memcpy(ws_child + spos, find_data.cFileName, (nlen + 1) * sizeof(wchar_t));

        memcpy(wd_child, wdst, dlen * sizeof(wchar_t));
        size_t dpos = dlen;
        if (!d_sep) {
            wd_child[dpos++] = L'\\';
        }
        memcpy(wd_child + dpos, find_data.cFileName, (nlen + 1) * sizeof(wchar_t));

        Result res;
        if ((find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0) {
            res = copy_dir_recursive_win32(ws_child, wd_child, force);
        } else {
            res = copy_file_win32(ws_child, wd_child, find_data.dwFileAttributes, force);
        }

        free(ws_child);
        free(wd_child);

        if (res != SUCCESS) {
            FindClose(h_find);
            return res;
        }
    } while (FindNextFileW(h_find, &find_data) != 0);

    DWORD loop_err = GetLastError();
    FindClose(h_find);

    if (loop_err != ERROR_NO_MORE_FILES && loop_err != ERROR_SUCCESS) {
        return map_win32_error(loop_err);
    }

    return SUCCESS;
}

Result copy_item(const char *src, const char *dst, bool force) {
    if (!src || src[0] == '\0' || !dst || dst[0] == '\0') {
        return ERR_INVALID_PATH;
    }

    wchar_t *wsrc = utf8_to_wide(src);
    if (!wsrc) {
        return ERR_INVALID_PATH;
    }

    wchar_t *wdst = utf8_to_wide(dst);
    if (!wdst) {
        free(wsrc);
        return ERR_INVALID_PATH;
    }

    DWORD src_attrs = GetFileAttributesW(wsrc);
    if (src_attrs == INVALID_FILE_ATTRIBUTES) {
        DWORD err = GetLastError();
        free(wsrc);
        free(wdst);
        return map_win32_error(err);
    }

    Result res;
    if ((src_attrs & FILE_ATTRIBUTE_DIRECTORY) != 0) {
        if (is_subpath_win32(wsrc, wdst)) {
            free(wsrc);
            free(wdst);
            return ERR_INVALID_PATH;
        }
        res = copy_dir_recursive_win32(wsrc, wdst, force);
    } else {
        res = copy_file_win32(wsrc, wdst, src_attrs, force);
    }

    free(wsrc);
    free(wdst);
    return res;
}
