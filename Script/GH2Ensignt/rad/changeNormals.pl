while (<stdin>){
    chomp;
    ($x,$y,$z,$nx,$ny,$nz)=split(/\s+/);
    print "$x $y $z 0 0 1\n";
}
