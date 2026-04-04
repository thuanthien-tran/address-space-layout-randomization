/*
 * Đo khoảng cách &buffer → saved RIP trong một hàm giống vuln() (aslr_demo.c).
 * Phải biên dịch với CÙNG cờ với demo_aslr/Makefile: BASE_FLAGS + -z noexecstack -no-pie
 * (gdb_measure_offset.py truyền cờ này khi gọi gcc).
 */
#include <stddef.h>
#include <stdio.h>

static void vuln(void *heap_ptr) {
    char buffer[64];

    (void)heap_ptr;
    {
        unsigned char *rbp = (unsigned char *)__builtin_frame_address(0);
        size_t off = (size_t)((rbp + 8) - (unsigned char *)&buffer);
        printf("OFFSET_RET_PROBE=%zu\n", off);
    }
}

int main(void) {
    vuln((void *)0);
    return 0;
}
