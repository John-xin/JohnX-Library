import numpy as np


def CheckConvergence(x_curr, y_curr, x_next, y_next, IM, JM):
    lim_max_error = 1e-5
    max_error = np.max(np.abs(x_curr[:, :] - x_next[:, :])) + np.max(np.abs(y_curr[:, :] - y_next[:, :]))
    re = 1
    if max_error < lim_max_error:
        re = 1
    else:
        re = 0
    print(max_error)
    return re, max_error
