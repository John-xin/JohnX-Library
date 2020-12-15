# The input obj file must be specified in the call i.e.
# perl makeRadplane.pl < filename.obj

# Versions
# Written Nov 07
# Rev 08_05_01
# The Header to the Scalar field is added automatically. The user may want to edit the name of the field, which is currently Irradiance. To include spaces use the % code (I'm not sure exactly what it is).
# The bug which caused data to be missed if it exceeded one line has been fixed.



# Open files to write to

open (OUT1,">RadPlane.dat");
open (OUT2,">VTKPlane.vtk");

# Look through input file line by line

while (<STDIN>){
    chomp; $myline=$_;
    
    # If the line starts with a space it will be the last part of the previous face connectivity data. The previous line is replaced to include this extra information.
    
        if ($myline =~ m/^ /){
        @arrNewLine=split(/\//,$myline);
        $arrNewLine[0]=$arrNewLine[0]-1;
        $lineoutF[$f-1] = "4 $arrPt1[0] $arrPt2[0] $arrPt3[0] $arrNewLine[0]";
        $count++;
    }
    
    # If line is vertex data split the data up and store it in lineoutV suitable for vtk format
    
    if ($myline =~ m/^v /){
        @arrVertex=split(/\s+/,$myline);
        $lineoutV[$i] = "$arrVertex[1] $arrVertex[2] $arrVertex[3]";
        $i++;
    }
    
    # If line is normal data ...
    
    if ($myline =~ m/^vn /){
        @arrNormal=split(/\s+/,$myline);
        $lineoutVn[$j] = "$arrNormal[1] $arrNormal[2] $arrNormal[3]";
        $j++;
    }
    
    # If line is face connectivity data ...
    
    if ($myline =~ m/^f /){
        @arrFace=split(/\s+/,$myline);
        @arrPt1 = split(/\//,$arrFace[1]);
        $arrPt1[0] = $arrPt1[0]-1;                              # CH? Why do these strings have indices?
        @arrPt2 = split(/\//,$arrFace[2]);
        $arrPt2[0] = $arrPt2[0]-1;
        @arrPt3 = split(/\//,$arrFace[3]);
        $arrPt3[0] = $arrPt3[0]-1;
        
        # If there is a fourth vertex associated with this face also add this vertex data
        
        if ($arrFace[4] != "") { # look at it again!!!
            @arrPt4 = split(/\//,$arrFace[4]);
            $arrPt4[0] = $arrPt4[0]-1;
            $lineoutF[$f] = "4 $arrPt1[0] $arrPt2[0] $arrPt3[0] $arrPt4[0]";          # CH? Does $f need To be initialised Or does it start at 0?
            $count = $count +5;                 # 
        }else{$lineoutF[$f] = "3 $arrPt1[0] $arrPt2[0] $arrPt3[0]";$count = $count+4;} 
        $f++;
    }
    
    # $count counts the number of entries In the required In the polygon part of the vtk file (4 For a triangle And 5 For a square)
    # $f counts the number of faces.
    # These two values are required For vtk file.
}

# Output the data In the right format into the vtk file And into the dat file

print OUT2 "# vtk DataFile Version 2.0\n";
print OUT2 "My Test Plane\n";
print OUT2 "ASCII\n";
print OUT2 "DATASET POLYDATA\n";
print OUT2 "POINTS $j float\n";
for $i(0..$j-1){
    print OUT1 "$lineoutV[$i] $lineoutVn[$i]\n";
    print OUT2 "$lineoutV[$i]\n";
}
print OUT2 "POLYGONS $f $count\n";
for $i(0..$f-1){
    print OUT2 "$lineoutF[$i]\n";
}

print OUT2 "POINT_DATA $j\n";
print OUT2 "SCALARS Irradiance float\n";
print OUT2 "LOOKUP_TABLE Default\n";
