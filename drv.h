
#include <sys/types.h>
#include <stdlib.h>

typedef uint8_t u_int8_t;
typedef uint16_t u_int16_t;
typedef uint32_t u_int32_t;
typedef uint64_t u_int64_t;

struct slice {
    unsigned char *cur;
    unsigned char *end;
};

/* aflCall.c */
extern int aflTestMode;
extern int aflInFd;
int startForkserver(int ticks);
char *getWork(u_long *sizep);
int startWork(u_int64_t start, u_int64_t end);
int doneWork(int val);

/* parse.c */
void mkSlice(struct slice *b, void *base, size_t sz);
unsigned char *sliceBuf(struct slice *b);
size_t sliceSize(struct slice *b);
int getEOF(struct slice *b);
int getU8(struct slice *b, u_int8_t *x);
int getU16(struct slice *b, u_int16_t *x);
int getU32(struct slice *b, u_int32_t *x);
int getU64(struct slice *b, u_int64_t *x);
int getDelimSlices(struct slice *b, const char *delim, int delsz, size_t max, struct slice *x, size_t *nx);

