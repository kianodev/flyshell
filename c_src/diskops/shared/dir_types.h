// c_src/diskops/shared/dir_types.h

#ifndef DIR_TYPES_H
#define DIR_TYPES_H

#include <stdbool.h>
#include <stddef.h>

typedef struct {
    char* name;
    bool is_dir;
} DirEntry;

typedef struct {
    DirEntry* entries;
    size_t count;
} DirList;

void free_dir_list(DirList* list);

#endif /* DIR_TYPES_H */
