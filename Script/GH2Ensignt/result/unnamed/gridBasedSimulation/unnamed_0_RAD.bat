SET RAYPATH=.;C:\Radiance\lib
PATH=C:\Radiance\bin;$PATH
F:
cd F:\AECOM\GH2Ensignt\result\unnamed\gridBasedSimulation\
rtrace -I  -h -dp 64 -ds 0.5 -dt 0.5 -dc 0.25 -dr 0 -st 0.85 -lr 4 -lw 0.05 -ab 1 -ad 1000 -as 128 -ar 300 -aa 0.1  -af unnamed.amb -e error.log unnamed_RAD.oct < unnamed_0.pts > unnamed_0.res
