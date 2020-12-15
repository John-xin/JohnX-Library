($file1,$file2)=@ARGV;

open(F1,$file1) or die"XX";
open(F2,$file2) or die"XX";

($name,$temp1)= split(/\./,$file1);
$outfile=join ("","$name","_output.vtk");

open(F3,">$outfile") or die"XX";

while (<F1>) {
$line=$_;
print F3 "$line";
};

while (<F2>) {
$line=$_;
print F3 "$line";
};

close F1;
close F2;
close F3;
