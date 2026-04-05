/*
 * Đo khoảng cách &buffer → saved RIP tại thời điểm giống ngay trước read() trong vuln().
 * Phải khớp thứ tự biến cục bộ trong khối đọc của demo_aslr/aslr_demo.c (q, left, n).
 * Biên dịch với CÙNG cờ Makefile: BASE_FLAGS + -z noexecstack -no-pie.
 */
#include <stddef.h>
#include <stdio.h>
#include <sys/types.h>

static void vuln(void *heap_ptr) {
    char buffer[64];

    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", heap_ptr);
    fflush(stdout);

    {
        unsigned char *q = (unsigned char *)buffer;
        size_t left = 400;
        ssize_t n = 0;
        (void)n;
        printf(
            "OFFSET_RET_PROBE=%zu\n",
            (size_t)(((unsigned char *)__builtin_frame_address(0) + 8)
                     - (unsigned char *)&buffer));
        (void)q;
        (void)left;
    }
}

int main(void) {
    vuln((void *)0);
    return 0;
}
