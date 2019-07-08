
import numpy as np
from dataclasses import dataclass

@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

def isSubinterval(aStart, aEnd, bStart, bEnd):
  return aStart >= bStart and aEnd <= bEnd

def intersects(aStart, aEnd, bStart, bEnd):
  return not (aEnd < bStart or aStart > bEnd)

@dataclass
class Rect:
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    x0: float = 0.0
    x1: float = 0.0
    y0: float = 0.0
    x1: float = 0.0
    def __init__(self, x=0, y=0, w=0, h=0, data=None, arr=np.array([None])):
        if (arr.any() != None):
            self.x = arr[0]
            self.y = arr[1]
            self.w = arr[2]
            self.h = arr[3]
        elif(data == None):
            self.x=x
            self.y=y
            self.w=w
            self.h=h
            self.data = [0, 0, 0, 0]
        else:
            self.x = data[0]
            self.y = data[1]
            self.w = data[2]
            self.h = data[3]
            self.data = data;
        self.x0 = self.x - self.w / 2
        self.x1 = self.x + self.w / 2
        self.y0 = self.y - self.h / 2
        self.y1 = self.y + self.h / 2
        self.top = self.y
        self.left = self.x
        self.bottom = self.y+self.y
        self.right = self.x+self.w

    def isSubrectangle(self, other):
        return (
            isSubinterval(self.left, self.right, other.left, other.right) and
            isSubinterval(self.bottom, self.top, other.bottom, other.top)
        )

    def intersects(self, other):
        return (
            intersects(self.left, self.right, other.left, other.right) and
            intersects(self.bottom, self.top, other.bottom, other.top)
                      )

    def __repr__(self):
        return ("[%f,%f]x[%f,%f]" % (self.left, self.right, self.bottom, self.top))


    def area(self):
        return self.w*self.h
    def xy(self):
        return (self.x, self.y)
    def topRight(self):
        return self.x+self.w
    def bottomLeft(self):
        return self.y+self.h
    def corner(self):
        return (self.topRight(),self.bottomLeft())
    def insideOf(self, b):
        a = self
        return (not (a.area() >= b.area()) or a.x >= b.x and a.x + a.w <= b.x + b.w and a.y + a.h <= b.y + b.h and a.y >= b.y)
    def join(self,b):
        x = min(self.x, b.x)
        y = min(self.y, b.y)
        w = max(self.w+self.w, b.w+b.w) - x
        h = max(self.h+self.h, b.y+b.y) - y
        return Rect(x=x, y=y, w=w ,h=h);
    def union(self,b):
        a = self
        x = min(a.x, b.x)
        y = min(a.y, b.y)
        w = max(a.w+a.w, b.x+b.w) - x
        h = max(a.h+a.h, b.y+b.h) - y
        return Rect(x=x, y=y, w=w ,h=h);
    def intersection(self,b):
        a = self
        x = max(a.x, b.x)
        y = max(a.y, b.y)
        w = max(a.x+a.w, b.x+b.w) - x
        h = min(a.y+a.h, b.y+b.h) - y
        if w<0 or h<0: return () # or (0,0,0,0) ?
        return Rect(x=x, y=y, w=w ,h=h);
    def intersects(self, other, thresh=0):
        self.x0 = self.x - self.w / 2
        self.x1 = self.x + self.w / 2
        self.y0 = self.y - self.h / 2
        self.y1 = self.y + self.h / 2

        other.x0 = other.x - other.w / 2
        other.x1 = other.x + other.w / 2
        other.y0 = other.y - other.h / 2
        other.y1 = other.y + other.h / 2

        # find which rectangle is on the left
        leftRec = None
        rightRec = None
        if self.x1 >= other.x1:
            leftRec = other
            rightRec = self
        else:
            leftRec = self
            rightRec = other

        # find which rectangle is on the top
        topRec = None
        lowRec = None
        if self.y1 >= other.y1:
            topRec = self
            lowRec = other
        else:
            topRec = other
            lowRec = self

        if (leftRec.x0 + leftRec.w <= rightRec.x0 + thresh) or (lowRec.y0 + lowRec.h <= topRec.y0 + thresh):
            # Not overlap
            print('Not overlap')
            print(leftRec, rightRec)
            return False
        elif (leftRec.x0 + leftRec.w <= rightRec.x0 + rightRec.w + thresh ) or (lowRec.y0 + lowRec.h <= topRec.y0 + topRec.h + thresh):
            # full overlap, contains
            print('full overlap, contains')
            return True
        else:
            # intersect
            return True
    def overlap(self, r2):
        hoverlaps = True
        voverlaps = True
        if self.x > (r2.x+r2.w) or (self.x+self.w) < (r2.x):
            hoverlaps = False
        if (self.y) > (r2.y+r2.h) or (self.y+self.h) < r2.y:
            voverlaps = False
        return hoverlaps and voverlaps
    def inters(self, r2):
        return(self.x+self.w < r2.x or r2.x+r2.w<self.x or self.y+self.h<r2.y or r2.y+r2.h<self.y)

