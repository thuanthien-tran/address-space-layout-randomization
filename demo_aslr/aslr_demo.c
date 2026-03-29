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

/* Gadget cho phase4 ROP: đảm bảo có 'pop rdi ; ret' trong binary (ROPgadget). */
__attribute__((used)) void rop_pop_rdi_ret(void) {
    __asm__("pop %rdi; ret");
}

/*
 * Chỉ có buffer[64] trong frame của vuln → offset tới saved RIP = 64 + 8 (RBP) = 72
 * (không để malloc pointer làm biến local trong vuln — GCC sắp xếp stack khác nhau → OFFSET_RET lệch).
 */
void vuln(void *heap_ptr) {
    char buffer[64];

    printf("Address of main:   %p (executable)\n", (void *)main);
    printf("Address of printf: %p (library)\n", (void *)printf);
    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", heap_ptr);
    fflush(stdout); /* Flush ngay để script Python readline() không bị treo khi stdout là pipe */

    gets(buffer);   /* Cố tình dùng gets để demo buffer overflow */
}

int main(void) {
    void *heap_ptr = malloc(1);

    setvbuf(stdout, NULL, _IONBF, 0);
    vuln(heap_ptr);
    free(heap_ptr);
    return 0;
}
