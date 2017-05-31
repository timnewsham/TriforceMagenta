/*
 * AFL hypercalls
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>
#include "drv.h"

int aflTestMode = 0;
int aflInFd = 0; // stdin

#define SZ 4096
static u_long bufsz;
static char *buf;
static u_int64_t volatile *arr;

static void
aflInit(void)
{
    static int aflInit = 0;
    char *pg;

    if(aflInit)
        return;

    pg = mmap(NULL, SZ, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_LOCKED, -1, 0);
    if(pg == (void*)-1) {
        perror("mmap");
        exit(1);
    }
    memset(pg, 0, SZ); // touch all the bits!

    arr = (u_int64_t *)pg;
    buf = pg + 2 * sizeof arr[0];
    bufsz = SZ - 2 * sizeof arr[0];

    aflInit = 1;
}

static inline u_long
aflCall(u_long a0, u_long a1, u_long a2)
{
    u_long ret;
#if __x86_64__
    __asm__(".byte 0x0f, 0x24" 
            : "=a"(ret) 
            : "D"(a0), "S"(a1), "d"(a2)
            );
#elif __aarch64__
    __asm__(".byte 0x41, 0x46, 0x1f, 0xd4"
            : "=r"(ret)
            : "r"(a0), "r"(a1), "r"(a1)
            );
#endif
    return ret;
}

int
startForkserver(int ticks)
{
    aflInit();
    if(aflTestMode)
        return 0;
    return aflCall(1, ticks, 0);
}

char *
getWork(u_long *sizep)
{
    aflInit();
    if(aflTestMode)
        *sizep = read(aflInFd, buf, bufsz);
    else
        *sizep = aflCall(2, (u_long)buf, bufsz);
    return buf;
}

/* buf should point to u_int64_t[2] */
int
startWork(u_int64_t start, u_int64_t end)
{
    aflInit();
    if(aflTestMode)
        return 0;
    arr[0] = start;
    arr[1] = end;
    arr[0]; arr[1];
    return aflCall(3, (u_long)&arr[0], 0);
}

int
doneWork(int val)
{
    aflInit();
    if(aflTestMode)
        return 0;
    return aflCall(4, (u_long)val, 0);
}

