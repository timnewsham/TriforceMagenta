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
channel_call_noretry = 19
channel_call_finish = 20
socket_create = 21
socket_write = 22
socket_read = 23
thread_exit = 24
thread_create = 25
thread_start = 26
thread_read_state = 27
thread_write_state = 28
process_exit = 29
process_create = 30
process_start = 31
process_read_memory = 32
process_write_memory = 33
job_create = 34
job_set_policy = 35
task_bind_exception_port = 36
task_suspend = 37
task_resume = 38
task_kill = 39
event_create = 40
eventpair_create = 41
futex_wait = 42
futex_wake = 43
futex_requeue = 44
waitset_create = 45
waitset_add = 46
waitset_remove = 47
waitset_wait = 48
port_create = 49
port_queue = 50
port_wait = 51
port_bind = 52
port_cancel = 53
timer_create = 54
timer_start = 55
timer_cancel = 56
vmo_create = 57
vmo_read = 58
vmo_write = 59
vmo_get_size = 60
vmo_set_size = 61
vmo_op_range = 62
vmo_clone = 63
vmo_set_cache_policy = 64
vmar_allocate = 65
vmar_destroy = 66
vmar_map = 67
vmar_unmap = 68
vmar_protect = 69
cprng_draw = 70
cprng_add_entropy = 71
fifo_create = 72
fifo_read = 73
fifo_write = 74
log_create = 75
log_write = 76
log_read = 77
ktrace_read = 78
ktrace_control = 79
ktrace_write = 80
mtrace_control = 81
debug_transfer_handle = 82
debug_read = 83
debug_write = 84
debug_send_command = 85
interrupt_create = 86
interrupt_complete = 87
interrupt_wait = 88
interrupt_signal = 89
mmap_device_io = 90
mmap_device_memory = 91
io_mapping_get_info = 92
vmo_create_contiguous = 93
bootloader_fb_get_info = 94
set_framebuffer = 95
set_framebuffer_vmo = 96
clock_adjust = 97
pci_get_nth_device = 98
pci_claim_device = 99
pci_enable_bus_master = 100
pci_enable_pio = 101
pci_reset_device = 102
pci_get_bar = 103
pci_get_config = 104
pci_io_write = 105
pci_io_read = 106
pci_map_interrupt = 107
pci_query_irq_mode_caps = 108
pci_set_irq_mode = 109
pci_init = 110
pci_add_subtract_io_range = 111
acpi_uefi_rsdp = 112
acpi_cache_flush = 113
resource_create = 114
resource_destroy = 115
resource_get_handle = 116
resource_do_action = 117
resource_connect = 118
resource_accept = 119
hypervisor_create = 120
hypervisor_op = 121
system_mexec = 122
syscall_test_0 = 123
syscall_test_1 = 124
syscall_test_2 = 125
syscall_test_3 = 126
syscall_test_4 = 127
syscall_test_5 = 128
syscall_test_6 = 129
syscall_test_7 = 130
syscall_test_8 = 131
syscall_test_wrapper = 132
COUNT = 133
