#!/usr/bin/env python
"""
translate old sys call numbers to new
"""
import os
import callsOld, callsNew
from parse import *

def mkTab() :
    map = dict()
    ns = dir(callsOld)
    for n in ns :
        if n.startswith('_') :
            continue
        onum = getattr(callsOld, n)
        if hasattr(callsNew, n) :
            nnum = getattr(callsNew, n)
            map[onum] = nnum
    return map

def trans1(x, map) :
    for call in x :
        if call[0] not in map :
            raise Error("no translation for %s" % call[0])
        call[0] = map[call[0]]
    
targDir = "trans"
nextFn = iter("%s/%d" % (targDir, n) for n in xrange(100000))

def trans(fns, map) :
    for fn in fns :
        try :
            x = readFile(fn)
            trans1(x, map)
        except Error, e :
            print "cant translate", fn, e
            continue
        fn2 = nextFn.next()
        print "translated", fn, fn2
        writeFn(fn2, mkSyscalls(*x))

def main() :
    if not os.path.exists(targDir) :
        os.mkdir(targDir)
    map = mkTab()
    trans(sys.argv[1:], map)

if __name__ == '__main__' :
    main()

