#!/usr/bin/env python
"""
Parse syscall records and show them
"""
from gen import *

class Error(Exception) :
    pass

class Getter(object) :
    def __init__(self, buf) :
        self.buf = buf
        self.pos = 0
    def get(self, n) :
        if self.pos + n > len(self.buf) :
            raise Error("missing data")
        b = self.buf[self.pos : self.pos + n]
        self.pos += n
        return b
    def rest(self) :
        n = len(self.buf) - self.pos
        return self.get(n)
    def unpack(self, fmt) :
        b = self.get(struct.calcsize(fmt))
        return struct.unpack(fmt, b)
    def unpack1(self, fmt) :
        return self.unpack(fmt)[0]

def pop(bufs) :
    if not bufs :
        raise Error("missing buf")
    return bufs.pop(0)

def parseArgNum(g, bufs) :
    return Num(g.unpack1('!Q'))
def parseArgAlloc(g, bufs) :
    return Alloc(g.unpack1('!I'))
def parseArgBuf(g, bufs) :
    return String(pop(bufs))
def parseArgBuflen(g, bufs) :
    return Len()
def parseArgFile(g, bufs) :
    return File(pop(bufs))
def parseArgStdFile(g, bufs) :
    return StdFile(g.unpack1('!H'))
def parseArgVec64(g, bufs) :
    n = g.unpack1('B')
    vs = [parseArg(g, bufs) for cnt in xrange(n)]
    return Vec64(*vs)
def parseArgFilename(g, bufs) :
    return Filename(pop(bufs))
def parseArgPid(g, bufs) :
    return Pid(g.unpack('B'))
def parseArgRef(g, bufs) :
    nc,na = g.unpack('BB')
    return Ref(nc, na)
def parseArgVec32(g, bufs) :
    n = g.unpack1('B')
    vs = [parseArg(g, bufs) for cnt in xrange(n)]
    return Vec32(*vs)
def parseArgDeref(g, bufs) :
    nc,na = g.unpack('BB')
    return Deref(nc, na)

tyTab = {
    0: parseArgNum,
    1: parseArgAlloc,
    2: parseArgBuf,
    3: parseArgBuflen,
    4: parseArgFile,
    5: parseArgStdFile,
    7: parseArgVec64,
    8: parseArgFilename,
    9: parseArgPid,
    10: parseArgRef,
    11: parseArgVec32,
    12: parseArgDeref,
}

def parseArg(g, bufs) :
    ty = g.unpack1('B')
    if ty not in tyTab :
        raise Error("bad arg type")
    return tyTab[ty](g, bufs)

def parseSyscall(buf) :
    bs = buf.split(BUFDELIM)
    g = Getter(bs[0])
    bufs = bs[1:]
    nr = g.unpack1('!H')
    args = [parseArg(g, bufs) for cnt in xrange(NARGS)]
    ret = [nr] + args
    # for now we ignore g.rest() and residual bufs
    return ret

def parseSyscalls(buf) :
    try :
        cs = buf.split(CALLDELIM)
        return [parseSyscall(c) for c in cs]
    except Error, e :
        return e

def readFile(fn) :
    with file(fn, 'r') as f :
        return parseSyscalls(f.read())

def show(x) :
    if isinstance(x,  Error) :
        print '   ', x
    else :
        for call in x :
            print '   ', call
def main() :
    for fn in sys.argv[1:] :
        print fn
        x = readFile(fn)
        show(x)
        print

if __name__ == "__main__" :
    main()
