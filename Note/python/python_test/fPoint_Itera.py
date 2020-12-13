def Point_Itera(x_curr,y_curr,x_next,y_next):
    JM = x_curr.shape[0]
    IM = x_curr.shape[1]

    for i in range(1,IM-1):
        for j in range(1,JM-1):
            #得到四个偏导数
            pxpI = (x_curr[j,i+1]-x_curr[j,i-1])/2
            pxpJ = (x_curr[j+1,i]-x_curr[j-1,i])/2
            pypI = (y_curr[j,i+1]-y_curr[j,i-1])/2
            pypJ = (y_curr[j+1,i]-y_curr[j-1,i])/2

            a = pxpJ ** 2 + pypJ ** 2   #pxpJ
            c = pxpI**2 + pypI**2       #pxpI
            b = pxpI*pxpJ + pypI*pypJ
            d = 2*(a+c)

            x_next[j,i] = (a*(x_curr[j,i+1]+x_curr[j,i-1])-
                          (2*b)*(x_curr[j+1,i+1]-x_curr[j-1,i+1]+x_curr[j-1,i-1]-x_curr[j+1,i-1])/4 +
                          c*(x_curr[j+1,i]+x_curr[j-1,i]))/d

            y_next[j,i] = (a*(y_curr[j,i+1]+y_curr[j,i-1])-
                           (2*b)*(y_curr[j+1,i+1]-y_curr[j-1,i+1]+y_curr[j-1,i-1]-y_curr[j+1,i-1])/4 +
                          c*(y_curr[j+1,i]+y_curr[j-1,i]))/d

