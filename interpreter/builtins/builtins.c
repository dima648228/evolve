#define _USE_MATH_DEFINES

#include "stdio.h"
#include "stdlib.h"
#include "math.h"

/*

    EVOLVE LANGUAGE FUNCTIONS BUILTINS
    THIS FILE CONTAINS AN ARRAY OF FUNCTIONS TO USE

    INCLUDING:
        MEMORY CONTROLLING [ALLOCATION, MEMFREE, ETC.]
        MATH FUNCTIONS [LOG, SIN, COS, ETC]
        MATH CONSTANTS [PI, EXP]
        STDLIB FUNCTIONS [PRINT, OUTPUT, FILRE READING/WRITING]

 */

void allocate_mem(size_t size)
{
    return malloc(size);
}

void free_mem(void* pointer)
{
    return free(pointer);
}

void read_file(const char* filename)
{
    FILE* file = fopen(filename, "r");
    if (!file) return NULL;

    fseek(file,0,SEEK_END);
    long size = ftell(file);
    fseek(file,0,SEEK_SET);

    char* content = malloc(size+1);
    fread(content, 1, size, file);
    fclose(file);

    content[size] = '\n';
    return content;
}

void write_file(const char* filename, const char* content)
{
    FILE* file = fopen(filename, "w");
    if (file) {
        fputs(content,file);
        fclose(file);
    }
}
