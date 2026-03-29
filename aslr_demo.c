/*
 * aslr_demo.c - Demo Address Space Layout Randomization (ASLR)
 * Môn: An toàn Hệ điều hành
 * In địa chỉ: executable (main), stack (buffer), thư viện (printf), heap (malloc).
 * Cố tình dùng gets() để demo buffer overflow.
 *
 * Bản gốc ở demo_aslr/aslr_demo.c — file này giữ đồng bộ cho Makefile ở root (nếu dùng).
 */

#include <stdio.h>
#include <stdlib.h>

int main(void);

char *gets(char *s);

__attribute__((used)) void rop_pop_rdi_ret(void) {
    __asm__("pop %rdi; ret");
}

void vuln(void *heap_ptr) {
    char buffer[64];

    printf("Address of main:   %p (executable)\n", (void *)main);
    printf("Address of printf: %p (library)\n", (void *)printf);
    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", heap_ptr);
    fflush(stdout);

    gets(buffer);
}

int main(void) {
    void *heap_ptr = malloc(1);

    setvbuf(stdout, NULL, _IONBF, 0);
    vuln(heap_ptr);
    free(heap_ptr);
    return 0;
}
