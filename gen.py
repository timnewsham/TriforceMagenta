#!/usr/bin/env python
"""
Generate syscall input files in the driver's file format.
"""
import struct, sys, subprocess

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

# syscall numbers from gen/include/magenta/mx-syscall-numbers.h
# note: these will likely change over time!
time_get = 0
nanosleep = 1
handle_close = 2
handle_duplicate = 3
handle_replace = 4
object_wait_one = 5
object_wait_many = 6
object_wait_async = 7
object_signal = 8
object_signal_peer = 9
object_get_property = 10
object_set_property = 11
object_set_cookie = 12
object_get_cookie = 13
object_get_info = 14
object_get_child = 15
channel_create = 16
channel_read = 17
channel_write = 18
channel_call = 19
socket_create = 20
socket_write = 21
socket_read = 22
thread_exit = 23
thread_create = 24
thread_start = 25
thread_read_state = 26
thread_write_state = 27
process_exit = 28
process_create = 29
process_start = 30
process_read_memory = 31
process_write_memory = 32
job_create = 33
job_set_policy = 34
task_bind_exception_port = 35
task_suspend = 36
task_resume = 37
task_kill = 38
event_create = 39
eventpair_create = 40
futex_wait = 41
futex_wake = 42
futex_requeue = 43
waitset_create = 44
waitset_add = 45
waitset_remove = 46
waitset_wait = 47
port_create = 48
port_queue = 49
port_wait = 50
port_bind = 51
port_cancel = 52
vmo_create = 53
vmo_read = 54
vmo_write = 55
vmo_get_size = 56
vmo_set_size = 57
vmo_op_range = 58
vmo_clone = 59
vmo_set_cache_policy = 60
vmar_allocate = 61
vmar_destroy = 62
vmar_map = 63
vmar_unmap = 64
vmar_protect = 65
cprng_draw = 66
cprng_add_entropy = 67
fifo_create = 68
fifo_read = 69
fifo_write = 70
log_create = 71
log_write = 72
log_read = 73
ktrace_read = 74
ktrace_control = 75
ktrace_write = 76
mtrace_control = 77
debug_transfer_handle = 78
debug_read = 79
debug_write = 80
debug_send_command = 81
interrupt_create = 82
interrupt_complete = 83
interrupt_wait = 84
interrupt_signal = 85
mmap_device_io = 86
mmap_device_memory = 87
io_mapping_get_info = 88
vmo_create_contiguous = 89
bootloader_fb_get_info = 90
set_framebuffer = 91
set_framebuffer_vmo = 92
clock_adjust = 93
pci_get_nth_device = 94
pci_claim_device = 95
pci_enable_bus_master = 96
pci_enable_pio = 97
pci_reset_device = 98
pci_map_mmio = 99
pci_get_bar = 100
pci_get_config = 101
pci_io_write = 102
pci_io_read = 103
pci_map_interrupt = 104
pci_map_config = 105
pci_query_irq_mode_caps = 106
pci_set_irq_mode = 107
pci_init = 108
pci_add_subtract_io_range = 109
acpi_uefi_rsdp = 110
acpi_cache_flush = 111
resource_create = 112
resource_destroy = 113
resource_get_handle = 114
resource_do_action = 115
resource_connect = 116
resource_accept = 117
hypervisor_create = 118
hypervisor_op = 119
system_mexec = 120
syscall_test_0 = 121
syscall_test_1 = 122
syscall_test_2 = 123
syscall_test_3 = 124
syscall_test_4 = 125
syscall_test_5 = 126
syscall_test_6 = 127
syscall_test_7 = 128
syscall_test_8 = 129
syscall_test_wrapper = 130

PANICTEST = 121

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

    # dont put this in inputs/
    #writeFn("./panicTest", mkSyscalls((PANICTEST, 1,2,3)))

