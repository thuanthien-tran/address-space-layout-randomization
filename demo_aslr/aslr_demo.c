/*
 * aslr_demo.c - Demo Address Space Layout Randomization (ASLR)
 * Môn: An toàn Hệ điều hành
 * In địa chỉ: executable (main), stack (buffer), thư viện (printf), heap (malloc).
 * Đọc đầu vào bằng read(2): cho phép byte 0 trong payload (ROP 64-bit).
 * Gom nhiều lần read tới 400 byte: một lần read qua PTY đôi khi chỉ trả về một phần → ROP không đủ byte.
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
 * OFFSET_RET (&buffer → saved RIP) phụ thuộc GCC + khối cục bộ (q, left, n) — đo bằng probe/GDB.
 */
void vuln(void *heap_ptr) {
    char buffer[64];

    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", heap_ptr);
    fflush(stdout);

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstringop-overflow="
    {
        unsigned char *q = (unsigned char *)buffer;
        size_t left = 400;
        ssize_t n;
        while (left > 0) {
            n = read(STDIN_FILENO, q, left);
            if (n <= 0) {
                break;
            }
            q += (size_t)n;
            left -= (size_t)n;
        }
    }
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
