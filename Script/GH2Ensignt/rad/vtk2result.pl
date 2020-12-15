($threshold,$inputfile,$outfile)=@ARGV;
#$inputfile=$ARGV[0];

if (scalar(@ARGV) == 3) {
    ($name,$temp1)= split(/\./,$inputfile);
    #$outfile=join ("","$name","_area.dat");

    #$outfile="irradiance.dat";
    $lines=0;
    open (IN,"<$outfile");
    while(<IN>){
            chomp;s/\"//g;
            $myline=$_;
            $filelines[$lines]=$_;
            $lines++;
        }
    close IN;
    open (OUT,">$outfile");
    for $i(0..$lines-1){
        print OUT "$filelines[$i]\n";
    }

    # Open files to write to
    open (IN,"<$inputfile");
    #$threshold=270;
    $flag_point=0;
    $flag_element=0;
    $flag_value=0;
    $sumarea=0;
    $totalvalue=0;
    $Tarea=0;
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
            # stop reading connectivity data when reach "POINT_DATA"
            if(/POINT_DATA/){
                $flag_element=0;
            }

            # read connectivity data
            if ($flag_element){
                    @connectivity_line[$c]=$_;
                    $c=$c+1;
                    #(@connectivity)=split /\s+/, $_;
                    #print OUT "@connectivity\n"if defined @connectivity;
                }
            # stop reading point data when reach "POLYGONS"
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
                    #print OUT "$pointloc[0] $pointloc[1] $pointloc[2]\n"if defined @pointloc;
            }
            # start reading point data when reach "POINTS"
            if (/POINTS/){
                ($temp1,$N_point,$temp2)= split /\s+/, $_;
                $flag_point=1;
            }
                
    }

    #change 4 side element to 3 side
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
    $E_out=$fc-1;

    #read point data
    for $i(0..$N_point-1){
        ($px[$i],$py[$i],$pz[$i])= split /\s+/, $point_line[$i] if defined $point_line[$i];
    }

    #dump out connectivity data
    for $j(0..$fc-1){
        ($con1,$con2,$con3)=split(' ',$final_connectivity[$j]);
        $x1=$px[$con2-1]-$px[$con1-1];
        $x2=$px[$con3-1]-$px[$con1-1];
        $y1=$py[$con2-1]-$py[$con1-1];
        $y2=$py[$con3-1]-$py[$con1-1];
        $z1=$pz[$con2-1]-$pz[$con1-1];
        $z2=$pz[$con3-1]-$pz[$con1-1]; 
        $xc=($px[$con1-1]+$px[$con2-1]+$px[$con3-1])/3.0;
        $yc=($py[$con1-1]+$py[$con2-1]+$py[$con3-1])/3.0;
        $zc=($pz[$con1-1]+$pz[$con2-1]+$pz[$con3-1])/3.0;
        $a=$y1*$z2-$y2*$z1;
        $b=$x2*$z1-$x1*$z2;
        $c=$x1*$y2-$y1*$x2;
        $area=sqrt($a*$a+$b*$b+$c*$c)*0.5;
        $d1=1.0/sqrt(($xc-$px[$con1-1])*($xc-$px[$con1-1])+($yc-$py[$con1-1])*($yc-$py[$con1-1])+($zc-$pz[$con1-1])*($zc-$pz[$con1-1]));
        $d2=1.0/sqrt(($xc-$px[$con2-1])*($xc-$px[$con2-1])+($yc-$py[$con2-1])*($yc-$py[$con2-1])+($zc-$pz[$con2-1])*($zc-$pz[$con2-1]));
        $d3=1.0/sqrt(($xc-$px[$con3-1])*($xc-$px[$con3-1])+($yc-$py[$con3-1])*($yc-$py[$con3-1])+($zc-$pz[$con3-1])*($zc-$pz[$con3-1]));
        $cvalue=($value[$con1-1]*$d1+$value[$con2-1]*$d2+$value[$con3-1]*$d3)/($d1+$d2+$d3);
        #print OUT "$area\n" if defined $final_connectivity[$j];
        $sumarea=$sumarea+$area;
        $totalvalue=$totalvalue+$cvalue*$area;
        if ($cvalue >= $threshold) {
            $Tarea=$Tarea+$area;
        }
    }

    $temp = $Tarea/$sumarea*100.0;


    #print "Parts: $name\n";
    #print "  Total Area = $sumarea\n";
    #print "  Integral value = $totalvalue\n";
    #print "  % of area over threshold = $temp";
    #print "Total Area = $sumarea\n";
    #print "Total Irradiance = $totalvalue\n";
    ($tempname,$temp2) = split(/_output/,$name);
    #print OUT "$temp\t$sumarea\t$totalvalue\n";
    if ($threshold == 0) {
        print OUT "$tempname\t$sumarea\t$totalvalue\n";
        print "Layer Name, Total Area, Total Value, writen to $outfile\n";
    } else {
        print OUT "$tempname\t$sumarea\t$Tarea\n";
        print "Layer Name, Total Area, Area over threshold, writen to $outfile\n";
    }

    close IN;
    close OUT;
} else {
    print "Usage: perl vtk2result.pl Threshold InputFile OutputFile\n";
}
