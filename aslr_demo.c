/*
 * aslr_demo.c - Demo Address Space Layout Randomization (ASLR)
 * Môn: An toàn Hệ điều hành
 * In địa chỉ: executable (main), stack (buffer), thư viện (printf), heap (malloc).
 * Cố tình dùng gets() để demo buffer overflow.
 */

#include <stdio.h>
#include <stdlib.h>

/* Forward declaration để dùng địa chỉ main trong vuln() */
int main(void);

/* gets() bị loại khỏi C11; khai báo tường minh vì dùng có chủ đích cho demo */
char *gets(char *s);

void vuln(void) {
    char buffer[64];
    void *heap_ptr = malloc(1);   /* heap - 1 byte chỉ để lấy địa chỉ */

    printf("Address of main:   %p (executable)\n", (void *)main);
    printf("Address of printf: %p (library)\n", (void *)printf);
    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", (void *)heap_ptr);

    free(heap_ptr);
    gets(buffer);   /* Cố tình dùng gets để demo buffer overflow */
}

int main(void) {
    vuln();
    return 0;
}
