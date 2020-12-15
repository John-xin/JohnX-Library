($file1,$file2)=@ARGV;

$boolFileFound = 1;
open(F1,$file1) or $boolFileFound = 0;
open(F2,$file2) or die"XX";

$outfile="Combined_output.vtk";

if ($boolFileFound == 1) {
    ($name,$temp1)= split(/\./,$file1);

    open(TEMPPT,">temppt.tmp") or die"XX";
    open(TEMPPTDATA,">tempptdata.tmp") or die"XX";
    open(TEMPPOLYGONS,">temppolygons.tmp") or die"XX";

    $startpt = 0;
    $startptdata = 0;
    $startpolygons = 0;

    while (<F1>) {
        $line=$_;
        @temp = split(/\s+/,$line);
        if ($startpt) {
            $count++;
            if ($count <= $nopt1) {
                print TEMPPT "$line";
            }
        }
        if ($startpolygon) {
            $count++;
            if ($count <= $nopolygons1) {
                print TEMPPOLYGONS "$line";
            }
        }
        if ($startptdata) {
            print TEMPPTDATA "$line";
        }
        if ($temp[0] eq "POINTS") {
            $nopt1 = $temp[1];
            $count = 0;
            $startpt = 1;
        }
        if ($temp[0] eq "POLYGONS") {
            $nopolygons1 = $temp[1];
            $nopolydata1 = $temp[2];
            $count = 0;
            $startpt = 0;
            $startpolygon = 1;
        }
        if ($temp[0] eq "LOOKUP_TABLE") {
            $startpolygon = 0;
            $startptdata = 1;
        }
    };

    $startpt = 0;
    $startptdata = 0;
    $startpolygons = 0;
    while (<F2>) {
        $line=$_;
        @temp = split(/\s+/,$line);
        if ($startpt) {
            $count++;
            if ($count <= $nopt2) {
                print TEMPPT "$line";
            }
        }
        if ($startpolygon) {
            $count++;
            if ($count <= $nopolygons2) {
                print TEMPPOLYGONS "$temp[0]";
                $temp1 = $temp[1] + $nopt1;
                print TEMPPOLYGONS " $temp1";
                $temp1 = $temp[2] + $nopt1;
                print TEMPPOLYGONS " $temp1";
                $temp1 = $temp[3] + $nopt1;
                print TEMPPOLYGONS " $temp1";
                if ($temp[0] == 4) {
                    $temp1 = $temp[4] + $nopt1;
                    print TEMPPOLYGONS " $temp1";
                }
                print TEMPPOLYGONS "\n";
            }
        }
        if ($startptdata) {
            print TEMPPTDATA "$line";
        }
        if ($temp[0] eq "POINTS") {
            $nopt2 = $temp[1];
            $count = 0;
            $startpt = 1;
        }
        if ($temp[0] eq "POLYGONS") {
            $nopolygons2 = $temp[1];
            $nopolydata2 = $temp[2];
            $count = 0;
            $startpt = 0;
            $startpolygon = 1;
        }
        if ($temp[0] eq "LOOKUP_TABLE") {
            $startpolygon = 0;
            $startptdata = 1;
        }
    };

    #while (<F2>) {
    #$line=$_;
    #print F3 "$line";
    #};

    close F1;
    close F2;
    close TEMPPT;
    close TEMPPTDATA;
    close TEMPPOLYGONS;

    open(TEMPPT,"temppt.tmp") or die"XX";
    open(TEMPPTDATA,"tempptdata.tmp") or die"XX";
    open(TEMPPOLYGONS,"temppolygons.tmp") or die"XX";
    open(F3,">$outfile") or die"XX";

    print F3 "# vtk DataFile Version 2.0\n";
    print F3 "My Test Plane\nASCII\nDATASET POLYDATA\n";

    $temp = $nopt1 + $nopt2;
    print F3 "POINTS $temp float\n";

    while (<TEMPPT>) {
        print F3 "$_";
    };

    $temp = $nopolygons1 + $nopolygons2;
    $temp1 = $nopolydata1 + $nopolydata2;
    print F3 "POLYGONS $temp $temp1\n";

    while (<TEMPPOLYGONS>) {
        print F3 "$_";
    };

    $temp = $nopt1 + $nopt2;
    print F3 "POINT_DATA $temp\nSCALARS Irradiance float\n";
    print F3 "LOOKUP_TABLE default\n";

    while (<TEMPPTDATA>) {
        print F3 "$_";
    };

    close TEMPPT;
    close TEMPPTDATA;
    close TEMPPOLYGONS;
    close F3;
} else {
    if ($file1 eq $outfile) {
        open(OUT,">$outfile") or die"XX";
        while (<F2>) {
            print OUT $_;
        }
        close F2;
        close OUT;
    } else {
        print "XX";
    }
}
