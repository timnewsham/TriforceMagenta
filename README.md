Fuzzer for Magenta using Triforce AFL

# Notes

- install [Triforce AFL](https://github.com/nccgroup/TriforceAFL) one
  directory up from where this directory is installed
- get [Magenta](https://github.com/fuchsia-mirror/magenta)
- apply magenta-patch.txt.  This patch will launch the fuzzer instead
  of the shell if "fuzz=true" is passed on the kernel cmd line.
  It also fixes a few bugs and disables the security checks
  that prevent you from making system calls from arbitrary addresses.
- symlink this dir under $MAGENTA/third_party/uapp/triforce
- make a link to the top level magenta dir in this dir: `ln -s $HOME/src/magenta $MAGENTA`
- in the magenta directory build with `make -j32 magenta-pc-x86-64`
- run `make` to generate inputs and build testAfl.
- run `runTest inputs/* panicTest` to make sure everything is working.
- to start a fuzzer run `runFuzz -M m0`.  See the runFuzz script for
  more options.
- to get information about crashes, run `repro`.  See script for details.

Tested on magenta commit cdf18c50c75685dd550edb91394f214062d725f0.
- note: I had to steal an internal header file.  this should be
  kept up to date if newer versions of magenta are used
- note: I had to patch a few parts of the Magenta system to support
  calling arbitrary syscalls from arbitrary program locations, and to
  fix two bugs that were fixed today..  Those bugs might be fixed
  in mainline by the time you read this.

# Files
- `README.md` - hello! thats me!
- `magenta-patch.txt` - patch to magenta system to support fuzzing
- `aflCall.c argfd.c driver.c drv.h parse.c sysc.c sysc.h` - sources for the fuzz driver
- `rules.mk private.h private-remoteio.h` - build helpers for building in magenta, with some stolen private headers
- `Makefile testAfl.c` - testAfl tool for running tests from linux host
- `gen.py` - Script for generating test inputs
- `runTest runFuzz runSh repro` - shell scripts for running tests, running a fuzzer, running the system normally, and reproing crashers.
