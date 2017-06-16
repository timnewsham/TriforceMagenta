#!/usr/bin/env python

dn = 'magenta/build-magenta-pc-x86-64/'
fn = 'gen/include/magenta/mx-syscall-numbers.h'

print '# syscall numbers from', fn
print '# note: these will likely change over time!'
for l in file(dn + fn) :
    l = l.strip()
    if l.startswith('#define') :
        l = l.replace('#define MX_SYS_', '').replace(' ', ' = ')
        print l

