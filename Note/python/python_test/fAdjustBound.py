def AdjustBound(x_curr,y_curr,x_next,y_next):

    JM = x_curr.shape[0]
    IM = x_curr.shape[1]

    '''
    i=0
    ii = IM-2
    for j in range(1,JM-1):

        pxpI = (x_curr[j,i+1]-x_curr[j,ii])/2 #first derivative of keci
        pxpJ = (x_curr[j+1,i]-x_curr[j-1,i])/2 #first derivative of yita
        pypI = (y_curr[j,i+1]+y_curr[j,ii])/2
        pypJ = (y_curr[j+1,i]-y_curr[j-1,i])/2
        c = pxpI**2 + pypI**2 #gamma
        b = pxpI*pxpJ + pypI*pypJ #beta
        a = pxpJ**2 + pypJ**2 #alpha
        d=2*(a+c)

        x_next[j,i]= (c*(x_curr[j+1,i]+x_curr[j-1,i])-
                      2*b*(x_curr[j+1,i+1]-x_curr[j-1,i+1]+x_curr[j-1,ii]-x_curr[j+1,ii])/4 +
                      a*(x_curr[j,i+1]+x_curr[j,ii]))/d

        y_next[j,i]= (c*(y_curr[j+1,i]+y_curr[j-1,i])-
                      2*b*(y_curr[j+1,i+1]-y_curr[j-1,i+1]+y_curr[j-1,ii]-y_curr[j+1,ii])/4 +
                      a*(y_curr[j,i+1]+y_curr[j,ii]))/d

        x_next[:, IM - 1] = x_next[:, 0]
        y_next[:, IM - 1] = y_next[:, 0]
        #x_next[:, 0] = x_next[:, IM-1]
        #y_next[:, 0] = y_next[:, IM-1]
    '''
    i = 0

    for j in range(1, JM - 1):
        pxpI = (x_curr[j, i + 1] - x_curr[j, i + 1]) / 2
        pxpJ = (x_curr[j + 1, i] - x_curr[j - 1, i]) / 2
        pypI = (y_curr[j, i + 1] + y_curr[j, i + 1]) / 2
        pypJ = (y_curr[j + 1, i] - y_curr[j - 1, i]) / 2
        a = pxpI ** 2 + pypI ** 2
        b = pxpI * pxpJ + pypI * pypJ
        c = pxpJ ** 2 + pypJ ** 2
        x_next[j, i] = (a * (x_curr[j + 1, i] + x_curr[j - 1, i]) -
                        b * (x_curr[j + 1, i + 1] - x_curr[j - 1, i + 1] - x_curr[j + 1, i + 1] + x_curr[
                    j - 1, i + 1]) / 2 +
                        c * (x_curr[j, i + 1] + x_curr[j, i + 1])) / (a + c) / 2
    for j in range(1, JM - 1):
        pxpI = (x_curr[j, i + 1] - x_curr[j, i + 1]) / 2
        pxpJ = (x_curr[j + 1, i] - x_curr[j - 1, i]) / 2
        pypI = (y_curr[j, i + 1] + y_curr[j, i + 1]) / 2
        pypJ = (y_curr[j + 1, i] - y_curr[j - 1, i]) / 2
        a = pxpI ** 2 + pypI ** 2
        b = pxpI * pxpJ + pypI * pypJ
        c = pxpJ ** 2 + pypJ ** 2
        y_next[j, i] = (a * (y_curr[j + 1, i] + y_curr[j - 1, i]) -
                        b * (y_curr[j + 1, i + 1] - y_curr[j - 1, i + 1] - y_curr[j + 1, i + 1] + y_curr[
                    j - 1, i + 1]) / 2 +
                        c * (y_curr[j, i + 1] + y_curr[j, i + 1])) / (a + c) / 2
    x_next[:, IM - 1] = x_next[:, 0]
    y_next[:, IM - 1] = y_next[:, 0]


    x_curr[:,(0,IM-1)] = x_next[:, (0,IM-1)]
    y_curr[:,(0,IM-1)] = y_next[:, (0,IM-1)]


