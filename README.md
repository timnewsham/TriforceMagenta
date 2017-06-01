Fuzzer for Magenta using Triforce AFL

# Notes

- install [Triforce AFL](https://github.com/nccgroup/TriforceAFL) one
  directory up from where this directory is installed
- get [Magenta](https://github.com/fuchsia-mirror/magenta)
- apply magenta-patch.txt.  It disables the security checks
  that prevent you from making system calls from arbitrary addresses.
- symlink this dir under $MAGENTA/third_party/uapp/triforce
- make a link to the top level magenta dir in this dir: `ln -s $HOME/src/magenta $MAGENTA`
- in the magenta directory build with `make -j32 magenta-pc-x86-64`
- run `make` to generate inputs and build testAfl.
- run `runTest inputs/* panicTest` to make sure everything is working.
- to start a fuzzer run `runFuzz -M m0`.  See the runFuzz script for
  more options.
- to get information about crashes, run `repro`.  See script for details.
- If you find interesting crashes and want to analyze them in more
  detail than provided by the `repro` output, copy the input file
  to the current directory, add an entry for it in the
  `USER_MANIFEST_LINES` entry in `rules.mk`, rebuild magenta, and
  then use `runSh` to run a shell.  You can run
  `gdb magenta/magenta/build-magenta-pc-x86-64/magenta.elf` and
  `target remote :1234` to debug the kernel.  To reproduce the
  crash from the shell run `fuzz -tvv /path/to/inputfile` specifying
  the location where you installed the input file.

Tested on magenta commit 867cff6b1131374f17446a032a4879117c098d5a
- note: I had to steal an internal header file.  this should be
  kept up to date if newer versions of magenta are used
- note: I had to patch a few parts of the Magenta system to support
  calling arbitrary syscalls from arbitrary program locations.

## Aarch64

- Build magenta with `make -j32 magenta-qemu-arm64`
- set `AARCH64=1` and run the same tools, ie: `AARCH64=1 ./runFuzz -M m1`

# Files
- `README.md` - hello! thats me!
- `magenta-patch.txt` - patch to magenta system to support fuzzing
- `aflCall.c argfd.c driver.c drv.h parse.c sysc.c sysc.h` - sources for the fuzz driver
- `rules.mk private.h private-remoteio.h` - build helpers for building in magenta, with some stolen private headers
- `Makefile testAfl.c` - testAfl tool for running tests from linux host
- `gen.py parse.py` - Scripts for generating test inputs and showing their contents
- `runTest runFuzz runSh repro` - shell scripts for running tests, running a fuzzer, running the system normally, and reproing crashers.
