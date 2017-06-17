/* 
 * Syscall driver
 */

#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <launchpad/launchpad.h>
#include <magenta/syscalls.h>

#include "drv.h"
#include "sysc.h"

#define MAXFILTCALLS 10

static void usage(const char *prog) {
    printf("usage:  %s [watch] [-tvx] [-f nr]* [input]\n", prog);
    printf("\t\twatch\tRun tests in a child process, watching for its death\n");
    printf("\t\t-f nr\tFilter out cases that dont make this call. Can be repeated\n");
    printf("\t\t-t\ttest mode, dont use AFL hypercalls\n");
    printf("\t\t-T\tenable qemu's timer in forked children\n");
    printf("\t\t-v\tverbose mode\n");
    printf("\t\t-x\tdon't perform system call\n");
    exit(1);
}

/* 
 * Execute tests in a child process, and watch for its death.
 */
static void watcher(int argc, char** argv) {
    /* shift args */
    char *prog = argv[0];
    argv++;
    argc--;

    launchpad_t *lp;
    launchpad_create(0, "fuzz-child", &lp);
    launchpad_load_from_file(lp, prog);
    launchpad_clone(lp, LP_CLONE_ALL);
    launchpad_set_args(lp, argc, (const char * const*)argv);
    mx_handle_t proc;
    const char *err;
    mx_status_t st = launchpad_go(lp, &proc, &err);
    if(st != MX_OK) {
        printf("failed to launch: %d %s\n", st, err);
        exit(1);
    }
    st = mx_object_wait_one(proc, MX_PROCESS_TERMINATED, MX_TIME_INFINITE, NULL);
    if(st != MX_OK) {
        printf("failed to wait %d\n", st);
        exit(1);
    }

    mx_info_process_t info;
    st = mx_object_get_info(proc, MX_INFO_PROCESS, &info, sizeof info, NULL, NULL);
    mx_handle_close(proc);
    if(st != MX_OK) {
        printf("failed to get info %d\n", st);
        exit(1);
    }

    /* if we got here the driver died */
    printf("child died: %d\n", info.return_code);
    doneWork(0);
    exit(0);
}

static int
parseU16(char *p, unsigned short *x)
{
    unsigned long val;
    char *endp;

    val = strtoul(p, &endp, 10);
    if(endp == p || *endp != 0 || val >= 65536)
        return -1;
    *x = val;
    return 0;
}

/* return true if we should execute this call */
static int
filterCalls(unsigned short *filtCalls, int nFiltCalls, struct sysRec *recs, int nrecs) 
{
    int i, j, match;

    /* all records should have calls on the filtCalls list */
    for(i = 0; i < nrecs; i++) {
        match = 0;
        for(j = 0; j < nFiltCalls; j++) {
            if(recs[i].nr == filtCalls[j])
                match = 1;
        }
        /* note: empty list is a match */
        if(!match && nFiltCalls > 0) 
            return 0;
    }
    return 1;
}

int verbose = 1;

int
main(int argc, char **argv)
{
    struct sysRec recs[3];
    struct slice slice;
    unsigned short filtCalls[MAXFILTCALLS];
    char *buf, *prog;
    u_long sz;
    long x;
    int opt, nrecs, nFiltCalls, parseOk;
    int noSyscall = 0;
    int enableTimer = 0;

    nFiltCalls = 0;
    prog = argv[0];
    if(argc > 1 && strcmp(argv[1], "watch") == 0) {
        sleep(2); // let the system settle down after boot
        watcher(argc, argv);
        return 0; // not reached
    }
    while((opt = getopt(argc, argv, "f:tTvx")) != -1) {
        switch(opt) {
        case 'f': 
            if(nFiltCalls >= MAXFILTCALLS) {
                printf("too many -f args!\n");
                exit(1);
            }
            if(parseU16(optarg, &filtCalls[nFiltCalls]) == -1) {
                printf("bad arg to -f: %s\n", optarg);
                exit(1);
            }
            nFiltCalls++;
            break;
        case 't':
            aflTestMode = 1;
            break;
        case 'T':
            enableTimer = 1;
            break;
        case 'v':
            verbose++;
            break;
        case 'x':
            noSyscall = 1;
            break;
        case '?':
        default:
            usage(prog);
            break;
        }
    }
    argc -= optind;
    argv += optind;
    if(argc == 1 && aflTestMode) {
        aflInFd = open(argv[0], O_RDONLY);
        if(aflInFd == -1) {
            printf("cant open %s\n", argv[0]);
            exit(1);
        }
        argc -= 1;
        argv += 1;
    }
    if(argc)
        usage(prog);

    startForkserver(enableTimer);
    buf = getWork(&sz);
    //printf("got work: %d - %.*s\n", sz, (int)sz, buf);

    /* trace our driver code while parsing workbuf */
    extern void *_end;
    startWork((u_long)main, (u_long)&_end);
    mkSlice(&slice, buf, sz);
    parseOk = parseSysRecArr(&slice, 3, recs, &nrecs);
    if(verbose) {
        printf("read %ld bytes, parse result %d nrecs %d\n", sz, parseOk, (int)nrecs);
        if(parseOk == 0)
            showSysRecArr(recs, nrecs);
    }

    if(parseOk == 0 && filterCalls(filtCalls, nFiltCalls, recs, nrecs)) {
        /* trace kernel code while performing syscalls */
        startWork(0xffff000000000000L, 0xffffffffffffffffL);

        if(noSyscall) {
            x = 0;
        } else {
            /* note: if this crashes, watcher will do doneWork for us */
            x = doSysRecArr(recs, nrecs);
        }
        if (verbose) printf("syscall returned %ld\n", x);
    } else {
        if (verbose) printf("Rejected by filter\n");
    }
    fflush(stdout);
    doneWork(0);
    return 0;
}

