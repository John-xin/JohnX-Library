class Point:
  x=0
  y=0
  z=0
  strVal=(0,0,0)
  def __init__(self,x,y,z):
    self.x = "%.6f" % x
    self.y = "%.6f" % y
    self.z = "%.6f" % z
    self.strVal=(self.x,self.y,self.z)

  def isEqual(self,point):
    if self.x==point.x and self.y==point.y and self.z==point.z:
        print("equal")
        return True
    else:
        print("not equal")
        return False

    
