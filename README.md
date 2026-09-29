# flamegraph

- generated example and readme :D

## Build

```
make          # builds every *.cpp in this directory into out/main
make clean    # removes out/
```

Add new `.cpp` files to the directory and they're picked up automatically — no
Makefile edits needed.

`main.cpp` is a small synthetic workload (`run_workload -> process_batch ->
dispatch -> {fast_path,slow_path} -> spin`) built specifically to be sampled
by `perf`. It's compiled with `-g -fno-omit-frame-pointer
-fno-optimize-sibling-calls` so stacks unwind cleanly — without
`-fno-optimize-sibling-calls`, GCC turns small tail-call functions like
`dispatch` into a plain `jmp` with no stack frame at all, which erases them
from the profile.

## Profile it with perf and produce a folded stack

1. Record samples while the program runs:

   ```
   perf record -F 99 --call-graph dwarf -o out/perf.data -- ./out/main
   ```

   `--call-graph dwarf` unwinds using DWARF CFI info. On this machine (WSL2),
   `--call-graph fp` (frame-pointer unwinding) silently drops some
   intermediate frames — `dwarf` gave the correct, complete stacks in
   testing, so prefer it here.

2. Turn the recording into readable stack traces, then fold them into the
   standard flamegraph "folded stack" format (one line per unique call
   stack, root-first, with a sample count):

   ```
   perf script -i out/perf.data | scripts/stackcollapse.py > out/out.folded
   ```

3. Inspect it:

   ```
   sort -k2 -n -r out/out.folded | head
   ```

   You should see two dominant stacks, roughly in a 1:2 sample ratio (since
   `slow_path` does 4x the work of `fast_path` but is only taken 1/3 of the
   time):

   ```
   _start;__libc_start_main;[libc.so.6];main;run_workload();process_batch(int);dispatch(int);slow_path();spin(unsigned long) 164
   _start;__libc_start_main;[libc.so.6];main;run_workload();process_batch(int);dispatch(int);fast_path();spin(unsigned long) 79
   ```

   A handful of single-sample stacks involving `ld-linux-x86-64.so.2` are
   normal — that's dynamic-linker startup work captured before `main` runs.

## Rendering it (optional)

`out/out.folded` is the standard folded-stack format used by Brendan Gregg's
[FlameGraph](https://github.com/brendangregg/FlameGraph) tools and by
[speedscope](https://www.speedscope.app) (drag-and-drop the `.folded` file
in "collapsed stack" mode) if you want an actual flame graph image/view.
