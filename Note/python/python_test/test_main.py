#用TTM方法生车贴体网格
#范雨 2010/12/5
import numpy as np
import matplotlib.pyplot as plt
from fCreateInitMesh import CreatInitMesh
from fPlotMesh import *
from fAdjustBound import *
from fPoint_Itera import *
from fCheckConvergence import *

if __name__ == '__main__':
    #-----------------------------
    #参数表
    #-----------------------------

    #boundary_out = [(0, 0), (5, 0), (10, 0), (15, 0), (15, 5), (15, 10), (15, 15), (10, 15), (5, 15), (0, 15), (0, 10), (0, 5),(0, 0)]
    boundary_out = [(18.18, -1.95), (21.48, 4.66), (21.03, 12.03), (16.95, 18.13), (10.34, 21.47), (2.97, 21.02), (-3.18, 16.95), (-6.47, 10.34),
                    (-6.02, 2.97), (-1.95, -3.18), (4.658, -6.47), (12.03, -6.03), (18.18, -1.95)]
    #boundary_in = [(5, 5), (6.5, 5), (8.5, 5), (10, 5), (10, 6.5), (10, 8.5), (10, 10), (8.5, 10), (6.5, 10), (5, 10), (5, 8.5), (5, 6.5),(5,5)]
    boundary_in = [ (10, 5), (10, 6.5), (10, 8.5), (10, 10), (8.5, 10), (6.5, 10), (5, 10),
                   (5, 8.5), (5, 6.5), (5, 5), (6.5, 5), (8.5, 5),(10, 5)]
    #boundary_out2in = [(0,0), (1.3, 1.5), (2.8, 2.8), (4, 4), (5, 5)]
    boundary_out2in = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),(0, 0),(0, 0),(0, 0)]

    IM=len(boundary_out)
    JM=len(boundary_out2in)

    #define matrix current and next --------
    y_next = np.zeros((JM,IM))
    x_next = np.zeros((JM,IM))
    y_curr = np.zeros((JM,IM))
    x_curr = np.zeros((JM,IM))

    #设置边界条件@current
    for j in range(0, IM):
        x_curr[0, j]=boundary_out[j][0]
        y_curr[0, j] = boundary_out[j][1]
        x_curr[JM-1, j]=boundary_in[j][0]
        y_curr[JM-1, j] = boundary_in[j][1]

    for i in range(1,JM-1):
        x_curr[i, 0]=boundary_out2in[i][0]
        y_curr[i, 0] = boundary_out2in[i][1]
        x_curr[i, IM-1]=boundary_out2in[i][0]
        y_curr[i, IM-1] = boundary_out2in[i][1]

    # 设置边界条件@next
    x_next[(0, JM-1), :] = x_curr[(0, JM-1), :]
    y_next[(0, JM-1), :] = y_curr[(0, JM-1), :]
    x_next[:, (0, IM-1)] = x_curr[:, (0, IM-1)]
    y_next[:, (0, IM-1)] = y_curr[:, (0, IM-1)]

    #plot ------------------------------------------
    for i in range(0, JM):
        plt.plot(x_curr[i, :], y_curr[i, :], 'r')
    #for i in range(0, IM):
        #plt.plot(x_curr[:, i], y_curr[:, i], 'b')

    plt.ylim(-10, 25)
    plt.xlim(-10, 25)
    #plt.show()

#step 2 -----------------------------------------------------------------------------------------------------

    CreatInitMesh(x_curr, y_curr)
    x_next[:,:]=x_curr[:,:]
    y_next[:,:]=y_curr[:,:]

    for i in range(0, JM):
        plt.plot(x_curr[i, :], y_curr[i, :], 'r')
    for i in range(0, IM):
        plt.plot(x_curr[:, i], y_curr[:, i], 'b')

    plt.ylim(-10, 25)
    plt.xlim(-10, 25)
    plt.show()

# step 3 -----------------------------------------------------------------------------------------------------
    #储存误差历程的向量
    MaxError = np.zeros((1,5000))
    re = 1
    a = 1
    for n in range(0,100):
        #进一步调整边界条件

        #迭代一步
        Point_Itera(x_curr,y_curr,x_next,y_next)
        #检查收敛
        (re , MaxError[0][n]) = CheckConvergence(x_curr,y_curr,x_next,y_next,IM,JM)
        if re == 1:
            break
        #递推
        x_curr[:,:] = x_next[:,:]
        y_curr[:,:] = y_next[:,:]

        AdjustBound(x_curr, y_curr, x_next, y_next)

        if n==1*a:
            a=a+1
            for i in range(0, JM):
                plt.plot(x_curr[i, :], y_curr[i, :], 'r')
            for i in range(0, IM):
                plt.plot(x_curr[:, i], y_curr[:, i], 'b')

            plt.ylim(-10, 25)
            plt.xlim(-10, 25)
            plt.title("itr %s" % n)
            plt.draw()
            plt.pause(0.5)
            plt.clf()

    #画出最终网格
    #PlotMesh(x_next,y_next,IM,JM,2)

    for i in range(0, JM):
        plt.plot(x_curr[i, :], y_curr[i, :], 'r')
    for i in range(0, IM):
        plt.plot(x_curr[:, i], y_curr[:, i], 'b')

    plt.ylim(-1, 16)
    plt.xlim(-1, 16)
    plt.show()

    #画出残差随迭代的变化
    fig = plt.figure(3)
    ax = fig.add_subplot(1,1,1)
    ax.plot(MaxError[0][0:n])
    plt.show()
