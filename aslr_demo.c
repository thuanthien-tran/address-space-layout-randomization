/*
 * aslr_demo.c - Demo Address Space Layout Randomization (ASLR)
 * Môn: An toàn Hệ điều hành
 * Bản đồng bộ với demo_aslr/aslr_demo.c — dùng khi build từ Makefile ở root.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void);

__attribute__((used)) void rop_pop_rdi_ret(void) {
    __asm__("pop %rdi; ret");
}

void vuln(void *heap_ptr) {
    char buffer[64];

    printf("Address of main:   %p (executable)\n", (void *)main);
    {
        void *libc = dlopen("libc.so.6", RTLD_NOW);
        void *libc_printf = libc ? dlsym(libc, "printf") : (void *)printf;
        printf("Address of printf: %p (library)\n", libc_printf);
    }
    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", heap_ptr);
    fflush(stdout);

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstringop-overflow="
    (void)read(STDIN_FILENO, buffer, 400);
#pragma GCC diagnostic pop
}

int main(void) {
    void *heap_ptr = malloc(1);

    setvbuf(stdout, NULL, _IONBF, 0);
    vuln(heap_ptr);
    free(heap_ptr);
    return 0;
}
