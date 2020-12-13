def FZeros(func,bound,paralist):
    """对指定的一元函数在指定的点求导数值

        func     函数对象，其定义形式应为，（注意，该函数以一个 元组 为参数）
                 test((x,p1,p2,p3,p4,...))
        bound    求根区间及初始值(x_min,x_max,x_init)
        paralist (p1,p2,p3,p4,...)
    """
    (x_min,x_max,x_init) = bound
    root_last = x_init
    root_now = x_init
    while True:
        root_now = root_last - func((root_last,) + paralist)/diff(func,root_last,paralist)
        if abs(root_last - root_now) <= 1e-4:
            break
        if x_min <= root_now <= x_max:
            root_last = root_now
        else:
            raise NoRootException(bound,paralist)
    return root_now


def diff(func,x,paralist):
    """对指定的一元函数在指定的点求导数值

        func     函数对象，其定义形式应为，（注意，该函数以一个 元组 为参数）
                 test((x,p1,p2,p3,p4,...))
        x        自变量的值
        paralist (p1,p2,p3,p4,...)
    """
    dx = 1e-8
    return (func((x + dx,) + paralist) - func((x - dx,) + paralist))/(2*dx)


class NoRootException(Exception):
    """求根过程自定义的异常"""
    def __init__(Self,bound,paralist):
        Exception.__init__(Self)
        Self.ebound = bound
        Self.eparalist = paralist


if __name__ == '__main__':
    def test(x_p):
        y = x_p[1]*x_p[0]**2 + x_p[2]*x_p[0] + x_p[3]
        return y
    try:
        print(FZeros(test,(5,10,6),(1,-4,3)))
    except NoRootException as e:
        print ("在所设置的区间" , e.ebound , "及参数表" , e.eparalist , "内没有根")