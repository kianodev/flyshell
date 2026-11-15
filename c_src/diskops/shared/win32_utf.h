// c_src/diskops/shared/win32_utf.h

#ifndef WIN32_UTF_H
#define WIN32_UTF_H

#ifdef _WIN32

#include <stdlib.h>
#include <windows.h>

static inline wchar_t *utf8_to_wide(const char *utf8_str) {
    if (!utf8_str) {
        return NULL;
    }
    int wlen = MultiByteToWideChar(CP_UTF8, 0, utf8_str, -1, NULL, 0);
    if (wlen <= 0) {
        return NULL;
    }
    wchar_t *wstr = (wchar_t *)malloc((size_t)wlen * sizeof(wchar_t));
    if (!wstr) {
        return NULL;
    }
    if (MultiByteToWideChar(CP_UTF8, 0, utf8_str, -1, wstr, wlen) <= 0) {
        free(wstr);
        return NULL;
    }
    return wstr;
}

static inline char *wide_to_utf8(const wchar_t *wstr) {
    if (!wstr) {
        return NULL;
    }
    int ulen = WideCharToMultiByte(CP_UTF8, 0, wstr, -1, NULL, 0, NULL, NULL);
    if (ulen <= 0) {
        return NULL;
    }
    char *utf8_str = (char *)malloc((size_t)ulen * sizeof(char));
    if (!utf8_str) {
        return NULL;
    }
    if (WideCharToMultiByte(CP_UTF8, 0, wstr, -1, utf8_str, ulen, NULL, NULL) <= 0) {
        free(utf8_str);
        return NULL;
    }
    return utf8_str;
}

#endif /* _WIN32 */

#endif /* WIN32_UTF_H */
