#!/usr/bin/env python
"""
Summarize whats in the repro logs.
Run: script -c "./runTest outputs/*/crashes/id*" crashLog-x86_64.txt; ./summary.py |sort -u
"""

import sys, re, os

known = [
]

def isKnown(x) :
    return any(re.search(pat, x) for pat in known)

def proc(ls) :
    if not ls :
        return
    keep = ''
    stack = ''
    fn = None
    for l in ls :
        m = re.search('Input from ([^ ]*) at', l)
        if m :
            fn = m.group(1)
        if l.startswith('call') :
            nr = int(l.split(' ')[-1])
            keep += callnr.get(nr, '???') + ' '
        if (l.startswith('child died') or
            l.startswith('panic') or
            l.startswith('test ended')) :
            l = re.sub('0x[0-9a-f]*','', l) # dont care about numeric diffs
            keep += l + ' '
        if 'fatal exception:' in l :
            keep += 'fatal '
    if stack :
        keep += 'stack: ' + stack
    if keep and (not SKIPKNOWN or not isKnown(keep)) :
        if SHOWFN :
            print fn
        print keep

import callsNew
callnr = dict()
ns = dir(callsNew)
for n in ns :
    if n.startswith('_') :
        continue
    num = getattr(callsNew, n)
    callnr[num] = n

SHOWFN = 1 if os.getenv("SHOWFN") else 0
SKIPKNOWN = 1

f = file('crashLog-x86_64.txt','r')

r = []
for l in f :
    l = l.rstrip()
    if l.startswith('Input from') :
        proc(r)
        r = []
    r.append(l)
proc(r)
