import matplotlib.pyplot as plt
import numpy as np
import time
def PlotMesh(x, y, IM, JM, n):
    fig = plt.figure(n)
    ax = fig.add_subplot(1, 1, 1)
    for i in range(0, JM):
        ax.plot(x[i, :], y[i, :], color='blue')
        #ax.plot(x[i, :], -y[i, :], color='blue')
    for i in range(0, IM):
        ax.plot(x[:, i], y[:, i], color='blue')
        #ax.plot(x[:, i], -y[:, i], color='blue')
    plt.ylim(0, 15)
    plt.xlim(0, 15)


