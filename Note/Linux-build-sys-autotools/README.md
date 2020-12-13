# Linux-build-sys-autotools
Material source: GNU atuomake manual.

Website: https://www.gnu.org/software/automake/manual/html_node/index.html#SEC_Contents

Autotools consists of:
1. autoconf - focuse on configure
2. automake - focuse on Makefiles

Purpose: 
1. create a GNU Build System
2. generate configure files


GNU Build System:

standardized process for build GNU project - related to complier and linker operation

a example for building GNU project:

1. Makefile

the program prog may be built by running the linker on the files main.o, foo.o, and bar.o; 

the file main.o may be built by running the compiler on main.c; 

Each time "make" is run, it reads "Makefile", checks the existence and modification time of the files mentioned, decides what files need to be built (or rebuilt), and runs the associated commands.

2. configure

reason: Makefile need to be adjusted, When a package to be built on a different platform

solution: use "configure" to automatically adjust the Makefile 

usage: running ./configure && make





