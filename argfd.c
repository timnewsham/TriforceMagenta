#include <fcntl.h>
#include <unistd.h>
#include <magenta/syscalls.h>
#include <magenta/process.h>
#include <mxio/remoteio.h>
#include "private-remoteio.h" // stole a local copy of this file from mxio

#include "drv.h"
#include "sysc.h"

int fdToHandles(int fd, mx_handle_t *h1, mx_handle_t *h2)
{
    if(fd >= 0 && fd < MAX_MXIO_FD) {
        mxrio_t *p = (mxrio_t*)mxio_fdtab[fd];
        if(p) {
            if(p->io.ops == mxio_fdtab[0]->ops) { // under assumption that fd0 i
                *h1 = p->h;
                *h2 = p->h2;
                return 1;
            }
        }
    }
    return 0;
}

mx_handle_t fdToHandle1(int fd)
{
    mx_handle_t h1, h2;
    if(fdToHandles(fd, &h1, &h2))
        return h1;
    return 0;
}

mx_handle_t fdToHandle2(int fd)
{
    mx_handle_t h1, h2;
    if(fdToHandles(fd, &h1, &h2))
        return h2;
    return 0;
}

mx_handle_t getStdFile(int typ)
{
    mx_handle_t h = 0;
    mx_handle_t dummy;
    int fd;

    switch(typ) {
    /* standard MX objects */
    case 0: mx_channel_create(0, &h, &dummy); break;
    case 1: mx_channel_create(0, &dummy, &h); break;
    case 2: mx_event_create(0, &h); break;
    case 3: mx_eventpair_create(0, &h, &dummy); break;
    case 4: mx_eventpair_create(0, &dummy, &h); break;
    case 5: mx_fifo_create(4, 4, 0, &dummy, &h); break;
    case 6: mx_fifo_create(4, 4, 0, &h, &dummy); break;
    case 7: mx_job_create(mx_job_default(), 0, &h); break;
    case 8: mx_port_create(0, &h); break;
    case 9: mx_process_create(mx_job_default(), "proc", 4, 0, &h, &dummy); break;
    case 10: mx_process_create(mx_job_default(), "proc", 4, 0, &dummy, &h); break;
    case 11: mx_socket_create(0, &h, &dummy); break;
    case 12: mx_socket_create(0, &dummy, &h); break;
    case 13: mx_thread_create(0, "thread", 6, 0, &h); break;
    case 14: mx_vmo_create(8192, 0, &h); break;
    // syscall has been removed
    //case 15: mx_waitset_create(0, &h); break;

    /* handles to channels to servers for "files" */
#define F(n, fn, flg) case n: fd = open(fn, flg); h = fdToHandle1(fd); break;
    F(16, "/", O_RDONLY);
    F(17, "/dev/null", O_RDWR);
    F(18, "/dev/zero", O_RDWR);
    F(19, "/dev/zero", O_RDWR);

    /* handles to channels for stdio */
#define FD(n, m) case n: h = fdToHandle1(m); break;
    FD(20, 0);
    FD(21, 1);

    /* handles to channels to servers for "sockets" */
#define S(n,n2, a,b,c) case n: fd = socket(a, b, c); h = fdToHandle1(fd); break; \
                       case n2: fd = socket(a, b, c); h = fdToHandle2(fd); break;
    S(22,23, AF_INET, SOCK_STREAM, 0);
    S(24,25, AF_INET, SOCK_DGRAM, 0);
    S(26,27, AF_INET6, SOCK_STREAM, 0);
    S(28,29, AF_INET6, SOCK_DGRAM, 0);

    /* mx proc handles */
    case 30: h = mx_process_self(); break;
    case 31: h = mx_vmar_root_self(); break;
    case 32: h = mx_job_default(); break;
    }
    return h;
}

