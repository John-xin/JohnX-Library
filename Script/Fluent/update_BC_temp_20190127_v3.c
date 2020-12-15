/*
DEFINE_ADJUST - execute before each iteration

you can use DEFINE_ADJUST to modify flow variables
(e.g., velocities, pressure) and compute integrals. 

You can also use it to integrate a scalar quantity over a
domain and adjust a boundary condition based on the result

Domain *d
Pointer to the domain over which the adjust function is to be applied. The domain
argument provides access to all cell and face threads in the mesh.
 
*/

#include "udf.h"

real avg_temp_inlet[12]={308, 308, 308, 308, 308, 308, 308, 308, 308, 308, 308, 308};

//Boundary zone ID
int ID_inlet[12]={48, 49, 51, 53,
		    55, 57,59, 61,
		    63, 65, 67, 69};

  DEFINE_ADJUST(get_avg_temp_inlet, domain) //execute before each iteration
 {

    face_t f;
    real NV_VEC(area);
    real total_area;
    int i;
    real tmp;
    Thread* thread;
    int mNum=0;
	 
   for(i=0; i<12; i++)
    {
        thread = Lookup_Thread(domain, ID_inlet[i]);
	total_area=0;
	tmp=0;
	

        begin_f_loop(f, thread)
       {
	    F_AREA(area, f, thread);  /* computes area of each face */    
            tmp+=F_T(f,thread)*NV_MAG(area);
            total_area +=NV_MAG(area); 
	     
	    //printf("face no %d -- %f \n", mNum, F_T(f,thread) );	
	    mNum=mNum+1;  
        }
        end_f_loop(f,thread)
        
	avg_temp_inlet[i]=tmp/total_area;
    
	printf("inlet_%d -- total area -- %f -- avg temp -- %f \n", i, total_area, (avg_temp_inlet[i]-273.15));

    }

}
    
    
  DEFINE_ON_DEMAND(update_BC_tmp)
 {

    Domain *domain;
    face_t f;
    real NV_VEC(area);
    real total_area;
    int i;
    real tmp;
    Thread* thread;
    int mNum=0;
	 
    domain=Get_Domain(1);
	 
   for(i=0; i<12; i++)
    {
        thread = Lookup_Thread(domain, ID_inlet[i]);
	total_area=0;
	tmp=0;
	

        begin_f_loop(f, thread)
       {
	    F_AREA(area, f, thread);  /* computes area of each face */    
            tmp+=F_T(f,thread)*NV_MAG(area); //returned temp in K unit
            total_area +=NV_MAG(area); 
	     
	    //printf("face no %d -- %f \n", mNum, F_T(f,thread) );	
	    mNum=mNum+1;  
        }
        end_f_loop(f,thread)
        
	avg_temp_inlet[i]= tmp/total_area;
    
	printf("inlet_%d -- total area -- %f -- avg temp -- %f \n", i,  total_area, (avg_temp_inlet[i]-273.15));

    }

}



 DEFINE_PROFILE(temp_profile_outlet1, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[0] +5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    printf("outlet1 -- setted --  \n");
 } 
 
  DEFINE_PROFILE(temp_profile_outlet2, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[1]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    printf("outlet2 -- setted --  \n");
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet3, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[2]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet4, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[3]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet5, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[4]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet6, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[5]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
 
   DEFINE_PROFILE(temp_profile_outlet7, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[6]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
 
   DEFINE_PROFILE(temp_profile_outlet8, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[7]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet9, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[8]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet10, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[9]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
 
   DEFINE_PROFILE(temp_profile_outlet11, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[10]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
   DEFINE_PROFILE(temp_profile_outlet12, thread, index) //index - variable assigned by FLUENT solver
 {
    face_t f;
    begin_f_loop(f,thread)
    {
	F_PROFILE(f,thread,index) = avg_temp_inlet[11]+5.2; //set temp in K unit
    }
    end_f_loop(f,thread)
    
    //printf("outlet1 -- avg temp -- %f \n", avg_temp_inlet[1]);
 } 
 
