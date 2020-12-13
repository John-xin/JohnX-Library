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
    #根据结构的对称性，只储存和计算一半的网格
    #因此，周向分网数实际上是实际值的一半
    IM = 18 #实际周向分网数=IM*2
    JM = 21 #径向分网数
    L_C = 1 #弦长
    R_OUT = 2.5*L_C #网格外径
    #生成初始网格
    (x,y)=CreatInitMesh(R_OUT,JM,IM)
    #画出初始网格
    PlotMesh(x,y,IM,JM,1)

    #准备迭代：准备储存当前步和推进步的空间
    y_next = np.zeros((JM,IM))
    x_next = np.zeros((JM,IM))
    y_curr = np.zeros((JM,IM))
    x_curr = np.zeros((JM,IM))
    y_curr[:,:] = y[:,:]
    x_curr[:,:] = x[:,:]
    #设置边界条件
    x_next[0,:] = x_curr[0,:]
    x_next[JM-1,:] = x_curr[JM-1,:]
    y_next[0,:] = y_curr[0,:]
    y_next[JM-1,:] = y_curr[JM-1,:]
    x_next[:,IM-1] = x_curr[:,IM-1]
    y_next[:,0] = y_curr[:,0]
    #x_next[:,0] = x_curr[:,0];#这个边界条件需要动态修正,在AdjustBound中进行
    y_next[:,IM-1] = y_curr[:,IM-1]
    #储存误差历程的向量
    MaxError = np.zeros((1,5000))
    re = 1
    for n in range(0,500):
        #进一步调整边界条件
        AdjustBound(x_curr,y_curr,x_next,y_next,IM,JM)
        #迭代一步
        Point_Itera(x_curr,y_curr,x_next,y_next,IM,JM)
        #检查收敛
        (re , MaxError[0][n]) = CheckConvergence(x_curr,y_curr,x_next,y_next,IM,JM)
        if re == 1:
            break
        #递推
        x_curr[:,:] = x_next[:,:]
        y_curr[:,:] = y_next[:,:]

    #画出最终网格
    PlotMesh(x_next,y_next,IM,JM,2)
    #画出残差随迭代的变化
    fig = plt.figure(3)
    ax = fig.add_subplot(1,1,1)
    ax.plot(MaxError[0][0:n])
    plt.show()
