$inputfile=$ARGV[0];

($name,$temp1)= split(/\./,$inputfile);
$outfile=join ("","$name",".dat");

# Open files To write To

open (IN,"<$inputfile");
open (OUT,">$outfile");
$flag_point=0;
$flag_element=0;
$flag_value=0;
$p=0;
$c=0;
$fc=0;
$v=0;
# Look through input file line by line
while(<IN>){
        chomp;s/\"//g;
        $myline=$_;
        
        # read value data
        if ($flag_value){
                @value[$v]=$_;
                $v=$v+1;
            }
        # start reading value data when reach "LOOKUP_TABLE"
        if(/LOOKUP_TABLE/){
            $flag_value=1;
        }
        # Stop reading connectivity data when reach "POINT_DATA"
        if(/POINT_DATA/){
            $flag_element=0;
        }

        # read connectivity data
        if ($flag_element){
                @connectivity_line[$c]=$_;
                $c=$c+1;
                #(@connectivity)=split /\s+/, $_;
                #print OUT "@connectivity\n"If defined @connectivity;
            }
        # Stop reading point data when reach "POLYGONS"
        if(/POLYGONS/){
            $flag_point=0;
            $flag_element=1;
            ($temp1,$N_element,$temp2)= split /\s+/, $_;   
        }
        
         # read point data       
        if ($flag_point){
                @point_line[$p]=$_;
                $p=$p+1;
                #(@pointloc)=split /\s+/, $_;
                #print OUT "$pointloc[0] $pointloc[1] $pointloc[2]\n"If defined @pointloc;
        }
        # start reading point data when reach "POINTS"
        if (/POINTS/){
            ($temp1,$N_point,$temp2)= split /\s+/, $_;
            $flag_point=1;
        }
            
}

#change 4 side element To 3 side
for $i(0..$N_element-1){
    ($Nside,$con1,$con2,$con3,$con4)=split(' ',$connectivity_line[$i]);
    if ($Nside==4){
        $final_connectivity[$fc]=join(" ",$con1+1,$con2+1,$con3+1);
        $fc++;
        $final_connectivity[$fc]=join(" ",$con3+1,$con4+1,$con1+1);
        $fc++;
    }else{
        $final_connectivity[$fc]=join(" ",$con1+1,$con2+1,$con3+1);
        $fc++;
    }
}
$E_out=$fc;
#write header
print OUT "TITLE=\"Output\"\n";
print OUT "VARIABLES=\"X\",\"Y\",\"Z\",\"Irradiance\"\n";
print OUT "ZONE T=\"Irradiance\",N=$p,E=$E_out,ET=TRIANGLE,F=FEPOINT\n";

#dump out point data
for $i(0..$N_point){
    print OUT "$point_line[$i] $value[$i]\n"if defined $point_line[$i];
}
#dump out connectivity data
for $j(0..$fc){
    print OUT "$final_connectivity[$j]\n"if defined $final_connectivity[$j];
}
close IN;
close OUT;
