#include "udf.H"
#define alpha 0.35//step1
#define MaxNumPts 8//step2
#define V_500 7.2

DEFINE_PROFILE(windProfile_E, thread, index){
real x[ND_ND];
real z;
face_t f;
real v[MaxNumPts];
real h[MaxNumPts];
//step3	
v[0]=0.502*V_500;
v[1]=0.503*V_500;
v[2]=0.540*V_500;
v[3]=0.574*V_500;
v[4]=0.668*V_500;
v[5]=0.743*V_500;
v[6]=0.827*V_500;
v[7]=0.900*V_500;
	
h[0]=25;
h[1]=50;
h[2]=75;
h[3]=100;
h[4]=200;
h[5]=300;
h[6]=400;
h[7]=500;

begin_f_loop(f,thread){
F_CENTROID(x,f,thread); //find face center coordinate and return to x array
z=x[2];
if(z>=0 && z<h[0]){
      F_PROFILE(f,thread,index)=v[0]*pow(z/h[0],alpha); 
    }else if(z>=h[MaxNumPts-1]){
         F_PROFILE(f,thread,index)=v[MaxNumPts-1];
    }else{
        int i;
        for(i=1; i<=MaxNumPts-1;i++){
            if(z>=h[i-1] && z<h[i]){
                 F_PROFILE(f,thread,index)=(z-h[i-1])*(v[i] - v[i-1])/(h[i]-h[i-1])+v[i-1];
            }
        }
    }       
}end_f_loop(f,thread)

}




