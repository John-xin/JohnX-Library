# The input obj file must be specified in the call i.e.
# perl makeRadplane.pl < filename.obj

# Versions
# Written Nov 07
# Rev 08_05_01
# The Header to the Scalar field is added automatically. The user may want to edit the name of the field, which is currently Irradiance. To include spaces use the % code (I'm not sure exactly what it is).
# The bug which caused data to be missed if it exceeded one line has been fixed.

$boolChange = 0;

# Open files to write to
($inputfile)=@ARGV;
if (scalar(@ARGV) == 1){
    open (IN, "<$inputfile");
    
    $found=0;
    $foundvn=0;
    $foundf=0;
    $error=0;
    # Look through input file line by line

    while (<IN>){
        chomp; $myline=$_;
        
    if ($foundvn){
            $lineout[$j-1] = "$templine[0] $templine[1] $templine[2] $myline";
            $foundvn=0;
            $boolChange = 1;
    }elsif($foundf){
            $lineout[$j-1] = "$templine[0] $templine[1] $templine[2] $templine[3] $myline";
            $foundf=0;
            $boolChange = 1;
        }else{
            if ($myline=~ /\\/){
                $error=1;
                if ($myline =~ m/^vn /){
                    @templine=split(/\s+/,$myline);
                    $lineout[$j] = "$templine[0] $templine[1] $templine[2] templine[3]";
                    $foundvn=1;
                    $error=0;
                }
                
                if ($myline =~ m/^f /){
                    @templine=split(/\s+/,$myline);
                    $lineout[$j] = "$templine[0] $templine[1] $templine[2] templine[3] templine[4]";
                    $foundf=1;
                    $error=0;
                }
                if ($error){
                    print "error";
                    $error=0;
                }
            $found=1;
            }
        $lineout[$j]=$myline;
        if ($myline =~ m/^vn 0 0 0/){
            $lineout[$j] = "vn 0 0 1";
            $boolChange = 1;
        }
        $j++;
        }
    }
    close IN;

    # Output the data in the right format into the vtk file and into the dat file

    if ($boolChange==1){
        open (OUT,">temp.tmp");
        for $i(0..$j-1){
            print OUT "$lineout[$i]\n";
        }
        close OUT;
        @tempfilename=split(/.obj/,$inputfile);
        $backupfile = "$tempfilename[0].bak";
        unlink($backupfile);
        rename($inputfile,$backupfile);
        rename("temp.tmp",$inputfile);
    }
    
} else{
    print "Usage: perl objchecker.pl ObjFile\n";
}
