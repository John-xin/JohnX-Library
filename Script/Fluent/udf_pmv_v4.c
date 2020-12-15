#include "udf.h"
#define CLO 1.9
#define MET 1.1 //metabolic rate: Value between sitting (1.0) and standing(1.2)
#define WME 0
#define TA 15.0
#define TR 15.0
#define VEL 1
#define RH 62
real pmvFunc(real _clo, real _met, real _wme, real _ta, real _tr, real _vel, real _rh){
  real hcf, hcn, hc;
  real pa;
  real icl, fcl;
  real m, w, mw;
  real taa, tra;
  real tcla;
  real tcl;
  real p1, p2, p3, p4, p5;
  real xn, xf;
  real n;

  real hl1, hl2, hl3, hl4, hl5, hl6;
  real ts;
  real pmv, ppd;
	
	pa = _rh*10*exp(16.6536-4030.183/(_ta+235));
	icl=0.155*_clo;
	m=_met*58.15;
	w=_wme*58.15;
	mw=m-w;
	  
	if(icl<0.078){
		  fcl=1+1.29*icl;
	}else{
		fcl=1.05+0.645*icl;
		}
		
	//vel=pow((pow(C_U(c,t),2)+pow(C_V(c,t),2)+pow(C_W(c,t),2)),0.5); 	
	hcf=12.1*pow(_vel,0.5);
	taa=_ta+273.15;
	tra=_tr+273.15;
		
	tcla=taa+(35.5-_ta)/(3.5*6.45*icl+0.1);

	p1=icl*fcl;
	p2=p1*3.96;
	p3=p1*100;
	p4=p1*taa;
	p5=308.7-0.028*mw+p2*pow(tra/100,4);
	xn=tcla/100;
	xf=xn;
	n=1;
	if(n<150){
		do {
			xf=(xf+xn)/2;
			hcn=2.38*pow(ABS(100*xf-taa),0.25);
			if(hcf>hcn){
				hc=hcf;
			}else {
				hc=hcn;
			}
			xn=(p5+p4*hc-p2*pow(xf,4))/(100+p3*hc);
			tcl=100*xn-273;
			n=n+1;
		}while(ABS(xn-xf)>0.00015);
	
		hl1=3.05*0.001*(5733-6.99*mw-pa);
		if(mw>58.15){
			hl2=0.42*(mw-58.15);
		}else{
			hl2=0;
		}
	
		hl3=1.7*0.00001*m*(5867-pa);
		hl4=0.0014*m*(34-_ta);
		hl5=3.96*fcl*(pow(xn,4)-pow(tra/100,4));
		hl6=fcl*hc*(tcl-_ta);
		ts=0.303*exp(-0.036*m)+0.028;
		pmv=ts*(mw-hl1-hl2-hl3-hl4-hl5-hl6);
		ppd=100-95*exp(-0.03353*pow(pmv,4)-0.2179*pow(pmv,2));
		return pmv;		
	}else{
		pmv=9999;
		ppd=100;
		return pmv;
	}	
	
	}

DEFINE_ON_DEMAND(udf_pmv)
{
  real vel;
  Thread *t;
  cell_t c;
  Domain *domain;
  domain = Get_Domain(1); //normally domain id starts at 1
	
 thread_loop_c(t,domain)
  {
   begin_c_loop(c,t)
	vel=pow((pow(C_U(c,t),2)+pow(C_V(c,t),2)+pow(C_W(c,t),2)),0.5); 
	C_UDMI(c,t,0)=pmvFunc(1.9,1.1,0,15,15,vel,62); //winter pmv with met 1.1
	C_UDMI(c,t,1)=pmvFunc(1.9,1.2,0,15,15,vel,62); //winter pmv with met 1.2
	 
	C_UDMI(c,t,2)=pmvFunc(0.2,1.1,0,28.2,28.2,vel,85); //summer pmv with met 1.1
	C_UDMI(c,t,3)=pmvFunc(0.2,1.2,0,28.2,28.2,vel,85); //summer pmv with met 1.2	  
   end_c_loop(c,t)
  }
  
  printf("udf_pmv defined");

}





