#!/usr/bin/env python
"""
Generate syscall input files in the driver's file format.
"""
import struct, sys, subprocess
from callsNew import *

BUFDELIM = "\xa5\xc9\x92"
CALLDELIM = "\xb7\xe3\xfe"
NARGS = 8

class Buf(object) :
    def __init__(self) :
        self.buf = []
        self.pos = 0
    def add(self, x) :
        #print repr(self), 'add', x.encode('hex')
        self.buf.append(x)
    def pack(self, fmt, *args) :
        x = struct.pack(fmt, *args)
        self.add(x)
    def __str__(self) :
        return ''.join(self.buf)

class Num(object) :
    def __init__(self, v) :
        self.v = v
    def mkArg(self, buf, xtra) :
        buf.pack('!B', 0)
        buf.pack('!Q', self.v)
    def __repr__(self) :
        return 'Num(%x)' % (self.v)
class Alloc(object) :
    def __init__(self, sz) :
        self.sz = sz
    def mkArg(self, buf, xtra) :
        buf.pack('!BI', 1, self.sz)
    def __repr__(self) :
        return 'Alloc(%x)' % (self.sz)
class String(object) :
    def __init__(self, v) :
        self.v = v
    def Len(self) :
        return Len(self)
    def mkArgTyp(self, typ, buf, xtra) :
        self.pos = xtra.pos
        xtra.pos += 1
        buf.pack('!B', typ)
        xtra.add(BUFDELIM)
        xtra.add(self.v)
    def mkArg(self, buf, xtra) :
        self.mkArgTyp(2, buf, xtra)
    def __repr__(self) :
        return 'String(%r)' % (self.v)
def StringZ(v) :
    return String(v + '\0')

class Len(object) :
    def mkArg(self, buf, xtra) :
        buf.pack('!B', 3)
    def __repr__(self) :
        return 'Len'
class File(String) :
    def mkArg(self, buf, xtra) :
        self.mkArgTyp(4, buf, xtra)
    def __repr__(self) :
        return 'File(%r)' % (self.v)
class StdFile(object) :
    def __init__(self, v) :
        self.v = v
    def mkArg(self, buf, xtra) :
        buf.pack('!BH', 5, self.v)
    def __repr__(self) :
        return 'StdFile(%x)' % (self.v)
class Vec64(object) :
    def __init__(self, *vs) :
        assert len(vs) < 256
        self.v = vs
    def mkArg(self, buf, xtra) :
        buf.pack('!BB', 7, len(self.v))
        for x in self.v :
            mkArg(buf, xtra, x)
    def __repr__(self) :
        return 'Vec64(%r)' % (self.v,)
class Filename(String) :
    def mkArg(self, buf, xtra) :
        self.mkArgTyp(8, buf, xtra)
    def __repr__(self) :
        return 'Filename(%r)' % (self.v)
class Pid(object) :
    def __init__(self, v) :
        self.v = v
    def mkArg(self, buf, xtra) :
        buf.pack('!BB', 9, self.v)
    def __repr__(self) :
        return 'Pid(%x)' % (self.v)
MyPid = Pid(0)
PPid = Pid(1)
ChildPid = Pid(2)

class Ref(object) :
    def __init__(self, nc, na) :
        self.nc, self.na = nc,na
    def mkArg(self, buf, xtra) :
        buf.pack('!BBB', 10, self.nc, self.na)
    def __repr__(self) :
        return 'Ref(%x %x)' % (self.nc, self.na)
class Deref(Ref) :
    def mkArg(self, buf, xtra) :
        buf.pack('!BBB', 12, self.nc, self.na)
    def __repr__(self) :
        return 'Deref(%x %x)' % (self.nc, self.na)
class Vec32(object) :
    def __init__(self, *vs) :
        assert len(vs) < 256
        self.v = vs
    def mkArg(self, buf, xtra) :
        buf.pack('!BB', 11, len(self.v))
        for x in self.v :
            mkArg(buf, xtra, x)
    def __repr__(self) :
        return 'Vec32(%r)' % (self.v,)

def mkArg(buf, xtra, x) :
    if isinstance(x, str) :
        x = StringZ(x)
    elif isinstance(x, int) or isinstance(x, long) :
        x = Num(x)
    x.mkArg(buf, xtra)

def mkSyscall(nr, *args) :
    args = list(args)
    while len(args) < NARGS :
        args.append(0)

    buf = Buf()
    xtra = Buf()
    buf.pack('!H', nr)
    for n,arg in enumerate(args) :
        #print 'arg', n
        mkArg(buf, xtra, arg)
    return str(buf) + str(xtra)

def mkSyscalls(*calls) :
    r = []
    for call in calls :
        r.append(mkSyscall(*call))
    return CALLDELIM.join(r)

def writeFn(fn, buf) :
    with file(fn, 'w') as f :
        f.write(buf)

if __name__ == '__main__' :
    buf = Alloc(1024)
    l = Len()

    evh = StdFile(2) # event_create
    MX_INFO_HANDLE_BASIC = 2
    ex1 = (object_get_info, evh, MX_INFO_HANDLE_BASIC, buf, l, 0, 0)
    writeFn("inputs/ex1", mkSyscalls(ex1))

    ex2 = (channel_create, 0, Vec64(0), Vec64(0))
    writeFn("inputs/ex2", mkSyscalls(ex2))

    ex3 = (event_create, 0, Vec64(0))
    writeFn("inputs/ex3", mkSyscalls(ex3))

    ex4 = (thread_create, 0, String("ThreadName"), l, 0, Vec64(0))
    writeFn("inputs/ex4", mkSyscalls(ex4))

    # send MXRIO_WRITE to fd=1
    # note: buffer lengths wont fuzz effectively because
    # write len must be datalen + 48, which rarely happens by accident
    MXRIO_WRITE = 6
    msg = "Hello World\n"
    assert len(msg) == 12
    ws = struct.unpack('<III', msg)
    buf = Vec32(
            0x01020304, # txid
            MXRIO_WRITE, # op
            len(msg), # datalen
            0, 0, 0, 0, # arg, arg2, reserved
            0, 0, 0, 0, 0, # hcount, handle[0..3]
            *ws # data[]
            )
    stdout = StdFile(21)
    call = channel_write, stdout, 0, buf, 4 * len(buf.v), 0, 0
    writeFn("inputs/exRio", mkSyscalls(call))

    call1 = channel_create, 0, Vec64(0), Vec64(0)
    call2 = channel_write, Deref(0, 2), 0, "Testing", l, 0, 0
    writeFn("inputs/exMulti", mkSyscalls(call1, call2))

    # dont put this in inputs/
    #writeFn("./panicTest", mkSyscalls((PANICTEST, 1,2,3)))

