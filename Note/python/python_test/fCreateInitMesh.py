import numpy as np
import matplotlib.pyplot as plt
from fFZeros import *


def CreatInitMesh(x_curr, y_curr):
    #IM=len(x_curr[0])
    #JM=len(x_curr)
    JM = x_curr.shape[0]
    IM = x_curr.shape[1]

    x = np.zeros((JM,IM))
    y = np.zeros((JM, IM))
    x[:,:] = x_curr[:,:]
    y[:,:] = y_curr[:,:]

    for n in range(0, 100):
        '''
        # for re-entrant boundary points
        for j in range(1, JM -1):
            x[j, 0] = (x_curr[j + 1, 0] + x_curr[j - 1, 0]) / 2
            y[j, 0] = (y_curr[j + 1, 0] + y_curr[j - 1, 0]) / 2

        x[:,IM-1] = x[:, 0]
        y[:,IM-1] = y[:, 0]
        '''
        # for interior points
        for i in range(0, IM):
            for j in range(1, JM -1):
                x[j, i] = (x_curr[j + 1, i] + x_curr[j - 1, i]) / 2
                y[j, i] = (y_curr[j + 1, i] + y_curr[j - 1, i]) / 2


        # for interior points
        '''
        for i in range(0,IM):
            for j in range(1,JM-1):
                #x[j, i] = (x_curr[j+1,i]+x_curr[j-1,i]+x_curr[j,i-1]+x_curr[j,i+1])/4
                #y[j, i] = (y_curr[j + 1, i] + y_curr[j - 1, i] + y_curr[j, i - 1] + y_curr[j, i + 1]) / 4
                a1=(JM-1-j)/(JM-1-0)
                a2=(j-0)/(JM-1-0)
                a3=(IM-1-i)/(IM-1-0)
                a4=(i-0)/(IM-1-0)
                x[j, i] = (a1 * x[0, i] + a2 * x[JM - 1, i] + a3 * x[j, 0] + a4 * x[j, IM - 1])/2
                y[j, i] = (a1 * y[0, i] + a2 * y[JM - 1, i] + a3 * y[j, 0] + a4 * y[j, IM - 1])/2
        '''
        x_curr[:,:] = x[:,:]
        y_curr[:,:] = y[:,:]


    '''
    for n in range(0, 100):
        i = 0
        for j in range(1, JM - 1):
            pxpI = (x_curr[j, i + 1] - x_curr[j, IM - 2]) / 2  # first derivative of keci
            pxpJ = (x_curr[j + 1, i] - x_curr[j - 1, i]) / 2  # first derivative of yita
            pypI = (y_curr[j, i + 1] + y_curr[j, IM - 2]) / 2
            pypJ = (y_curr[j + 1, i] - y_curr[j - 1, i]) / 2
            a = pxpI ** 2 + pypI ** 2  # gamma
            b = pxpI * pxpJ + pypI * pypJ  # beta
            c = pxpJ ** 2 + pypJ ** 2  # alpha
            d = (a + c) / 2
            x[j, i] = (a * (x_curr[j + 1, i] + x_curr[j - 1, i]) -
                           b * (x_curr[j + 1, i + 1] - x_curr[j - 1, i + 1] - x_curr[j + 1, IM - 2] + x_curr[
                            j - 1, IM - 2]) / 2 +
                           c * (x_curr[j, i + 1] + x_curr[j, IM - 2])) / d

            y[j, i] = (a * (y_curr[j + 1, i] + y_curr[j - 1, i]) -
                           b * (y_curr[j + 1, i + 1] - y_curr[j - 1, i + 1] - y_curr[j + 1, IM - 2] + y_curr[
                            j - 1, IM - 2]) / 2 +
                           c * (y_curr[j, i + 1] + y_curr[j, IM - 2])) / d
            x[:, IM - 1] = x[:, 0]
            y[:, IM - 1] = y[:, 0]

        # for interior points
        for i in range(1, IM - 1):
            for j in range(1, JM - 1):
                # x[j, i] = (x_curr[j+1,i]+x_curr[j-1,i]+x_curr[j,i-1]+x_curr[j,i+1])/4
                # y[j, i] = (y_curr[j + 1, i] + y_curr[j - 1, i] + y_curr[j, i - 1] + y_curr[j, i + 1]) / 4
                a1 = (JM - 1 - j) / (JM - 1 - 0)
                a2 = (j - 0) / (JM - 1 - 0)
                a3 = (IM - 1 - i) / (IM - 1 - 0)
                a4 = (i - 0) / (IM - 1 - 0)
                x[j, i] = (a1 * x[0, i] + a2 * x[JM - 1, i] + a3 * x[j, 0] + a4 * x[j, IM - 1]) / 2
                y[j, i] = (a1 * y[0, i] + a2 * y[JM - 1, i] + a3 * y[j, 0] + a4 * y[j, IM - 1]) / 2

        x_curr[:,:] = x[:,:]
        y_curr[:,:] = y[:,:]

        if n==10*a:
            a=a+1
            for i in range(0, JM):
                plt.plot(x_curr[i, :], y_curr[i, :], 'r')
            for i in range(0, IM):
                plt.plot(x_curr[:, i], y_curr[:, i], 'b')

            plt.ylim(-1, 16)
            plt.xlim(-1, 16)
            plt.show()
    '''





if __name__ == '__main__':
    try:
        IM = 18  # 实际周向分网数=IM*2
        JM = 21  # 径向分网数
        L_C = 1  # 弦长
        R_OUT = 2.5 * L_C  # 网格外径

        CreatInitMesh(R_OUT, JM, IM)
    except NoRootException as e:
        print("在所设置的区间", e.ebound, "及参数表", e.eparalist, "内没有根")
