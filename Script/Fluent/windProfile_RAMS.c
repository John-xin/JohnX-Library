#include "udf.H"
#define alphaLine0 0.15
#define alphaLine1 0.15
#define alphaLine2 0.15
#define alphaLine3 0.15
#define maxNoLine0 10
#define maxNoLine1 8
#define maxNoLine2 7
#define maxNoLine3 12
DEFINE_PROFILE(windProfileLine0, thread, index){
real x[ND_ND];
real z;
face_t f;
real v[maxNoLine0];
real h[maxNoLine0];
v[0]=2.3;
h[0]=20;
v[1]=2.5;
h[1]=40;
v[2]=2.6;
h[2]=60;
v[3]=2.75;
h[3]=80;
v[4]=2.9;
h[4]=100;
v[5]=3.3;
h[5]=150;
v[6]=3.7;
h[6]=200;
v[7]=5.33;
h[7]=400;
v[8]=5.8;
h[8]=460;
v[9]=6;
h[9]=500;
begin_f_loop(f,thread){
F_CENTROID(x,f,thread); //find face center coordinate and return to x array
z=x[2];
if(z>=0 && z<h[0]){
      F_PROFILE(f,thread,index)=v[0]*pow(z/h[0],alphaLine0); 
    }else if(z>=h[maxNoLine0-1]){
         F_PROFILE(f,thread,index)=v[maxNoLine0-1];
    }else{
        int i;
        for(i=1; i<=maxNoLine0-1;i++){
            if(z>=h[i-1] && z<h[i]){
                 F_PROFILE(f,thread,index)=(z-h[i-1])*(v[i] - v[i-1])/(h[i]-h[i-1])+v[i-1];
            }
        }
    }       
}end_f_loop(f,thread)

}


DEFINE_PROFILE(windProfileLine1, thread, index){
real x[ND_ND];
real z;
face_t f;
real v[maxNoLine1];
real h[maxNoLine1];
v[0]=2.2;
h[0]=20;
v[1]=2.4;
h[1]=40;
v[2]=2.5;
h[2]=60;
v[3]=2.6;
h[3]=80;
v[4]=2.75;
h[4]=100;
v[5]=3;
h[5]=150;
v[6]=4.35;
h[6]=400;
v[7]=5.05;
h[7]=500;
begin_f_loop(f,thread){
F_CENTROID(x,f,thread);
z=x[2];
if(z>=0 && z<h[0]){
      F_PROFILE(f,thread,index)=v[0]*pow(z/h[0],alphaLine1); 
    }else if(z>=h[maxNoLine1-1]){
         F_PROFILE(f,thread,index)=v[maxNoLine1-1];
    }else{
        int i;
        for(i=1; i<=maxNoLine1-1;i++){
            if(z>=h[i-1] && z<h[i]){
                 F_PROFILE(f,thread,index)=(z-h[i-1])*(v[i] - v[i-1])/(h[i]-h[i-1])+v[i-1];
            }
        }
    }       
}end_f_loop(f,thread)

}


DEFINE_PROFILE(windProfileLine2, thread, index){
real x[ND_ND];
real z;
face_t f;
real v[maxNoLine2];
real h[maxNoLine2];
v[0]=2.52;
h[0]=10;
v[1]=3.1;
h[1]=100;
v[2]=3.35;
h[2]=150;
v[3]=3.4;
h[3]=200;
v[4]=3.45;
h[4]=310;
v[5]=3.8;
h[5]=400;
v[6]=4.25;
h[6]=500;
begin_f_loop(f,thread){
F_CENTROID(x,f,thread);
z=x[2];
if(z>=0 && z<h[0]){
      F_PROFILE(f,thread,index)=v[0]*pow(z/h[0],alphaLine2); 
    }else if(z>=h[maxNoLine2-1]){
         F_PROFILE(f,thread,index)=v[maxNoLine2-1];
    }else{
        int i;
        for(i=1; i<=maxNoLine2-1;i++){
            if(z>=h[i-1] && z<h[i]){
                 F_PROFILE(f,thread,index)=(z-h[i-1])*(v[i] - v[i-1])/(h[i]-h[i-1])+v[i-1];
            }
        }
    }       
}end_f_loop(f,thread)

}


DEFINE_PROFILE(windProfileLine3, thread, index){
real x[ND_ND];
real z;
face_t f;
real v[maxNoLine3];
real h[maxNoLine3];
v[0]=2.3;
h[0]=20;
v[1]=2.5;
h[1]=40;
v[2]=2.6;
h[2]=60;
v[3]=2.9;
h[3]=80;
v[4]=3.1;
h[4]=100;
v[5]=3.65;
h[5]=150;
v[6]=4;
h[6]=180;
v[7]=4.45;
h[7]=245;
v[8]=4.3;
h[8]=300;
v[9]=4.3;
h[9]=380;
v[10]=4.75;
h[10]=460;
v[11]=4.85;
h[11]=500;
begin_f_loop(f,thread){
F_CENTROID(x,f,thread);
z=x[2];
if(z>=0 && z<h[0]){
      F_PROFILE(f,thread,index)=v[0]*pow(z/h[0],alphaLine3); 
    }else if(z>=h[maxNoLine3-1]){
         F_PROFILE(f,thread,index)=v[maxNoLine3-1];
    }else{
        int i;
        for(i=1; i<=maxNoLine3-1;i++){
            if(z>=h[i-1] && z<h[i]){
                 F_PROFILE(f,thread,index)=(z-h[i-1])*(v[i] - v[i-1])/(h[i]-h[i-1])+v[i-1];
            }
        }
    }       
}end_f_loop(f,thread)

}


