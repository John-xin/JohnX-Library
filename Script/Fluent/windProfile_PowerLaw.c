#include "udf.H"
#define alpha 0.35//step1

DEFINE_PROFILE(windProfileLine0, thread, index){
real x[ND_ND];
real z;
face_t f;
real v0;
real h0;
v0=2.3;//step2
h0=20;//step3
begin_f_loop(f,thread){
F_CENTROID(x,f,thread); //find face center coordinate and return to x array
z=x[2];
if(z<500){
      F_PROFILE(f,thread,index)=v0*pow(z/h0,alpha); 
    }else if(z>=500){
         F_PROFILE(f,thread,index)=v0*pow(500/h0,alpha); 
    }
}end_f_loop(f,thread)

}




