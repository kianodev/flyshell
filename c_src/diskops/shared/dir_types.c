// c_src/diskops/shared/dir_types.c

#include <stdlib.h>
#include "dir_types.h"

void free_dir_list(DirList* list) {
    if (!list) return;
    if (list->entries) {
        for (size_t i = 0; i < list ->count; ++i) {
            free(list->entries[i].name);
        }
        free(list->entries);
        list->entries = NULL;
    }
    list->count = 0;
}
