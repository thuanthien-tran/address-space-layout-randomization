/*
 * aslr_demo.c - Demo Address Space Layout Randomization (ASLR)
 * Môn: An toàn Hệ điều hành
 * In địa chỉ: executable (main), stack (buffer), thư viện (printf), heap (malloc).
 * Đọc đầu vào bằng read(2): cho phép byte 0 trong payload (ROP 64-bit).
 *
 * QUAN TRỌNG: dlopen/dlsym cho leak printf libc phải gọi trong main(), KHÔNG trong vuln().
 * Nếu đặt trong vuln(), GCC thêm khung stack → OFFSET_RET (72) lệch → Phase 1–3 fail.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void);

/* Gadget cho phase4 ROP: đảm bảo có 'pop rdi ; ret' trong binary (ROPgadget). */
__attribute__((used)) void rop_pop_rdi_ret(void) {
    __asm__("pop %rdi; ret");
}

/*
 * Frame tối giản: chỉ buffer[64] → offset tới saved RIP = 64 + 8 (RBP) = 72
 * (khớp exploits/exploit_config.py OFFSET_RET).
 */
void vuln(void *heap_ptr) {
    char buffer[64];

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

    /* In main + printf (libc thật) trước vuln — giữ thứ tự 4 dòng cho script Python */
    {
        void *libc = dlopen("libc.so.6", RTLD_NOW);
        void *libc_printf = libc ? dlsym(libc, "printf") : (void *)printf;
        printf("Address of main:   %p (executable)\n", (void *)main);
        printf("Address of printf: %p (library)\n", libc_printf);
    }

    vuln(heap_ptr);
    free(heap_ptr);
    return 0;
}
