#!/usr/bin/env python
import cv2
import numpy as np
from matplotlib import pyplot as plt
from dataclasses import dataclass

import json
import argparse

from typeslib import Rect, Point

from pathlib import Path

from elim_rects import *

def draw(rect, img):
    print('draw')
    cv2.rectangle(img, (rect.x, rect.y), (rect.topRight(), rect.bottomLeft()), (0,0,255),2)


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-i','--input', nargs='?', type=str, default="./test/014.png");
parser.add_argument('-o','--output', nargs='?', type=str, default="./out.png");
parser.add_argument('-d','--directory', nargs='?', type=str, default='./');

args = parser.parse_args()

filename = args.input

orig = cv2.imread(filename)
img = orig.copy()
result = orig.copy()
imgh, imgw, channels = img.shape;

#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#img = np.zeros((400, 400,3), dtype='uint8')
#img[np.where((img==[0,0,0]).all(axis=2))] = [255,255,255]
#img[np.where((img == [0]).all(axis = 2))] = [255]

#img = np.zeros((400,400,3), dtype="uint8")

img[np.where((img < [255]).all(axis=2))] = [0,0,0] # Make everything not white into black

#raw = img.copy()
#cv2.imshow('Test', img)
#cv2.imshow('Test2', raw)
#if cv2.waitKey() == ord('q'):
#    cv2.destroyAllWindows()


#print('done')
#quit()

img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY_INV)

contours, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

panel_thresh = ((imgw/8) * (imgh/10))/2

rect_data = []
rect_list = []

for cnt in contours:
    hull = cv2.convexHull(cnt)

    cv2.drawContours(result, [cnt], -1, (0, 0, 0), -1)
    cv2.drawContours(result, [hull], -1, (0, 0, 0), -1)

    rect = Rect(data=cv2.boundingRect(hull))

    x,y,w,h = cv2.boundingRect(hull)
    if(rect.area() > panel_thresh):
#        rect_list.append(rect);
        cv2.rectangle(result, (x,y), (x+w,y+h), (0,0,0), -1)


cv2.imwrite(args.output, result)

print('done')
quit()

def draw_rect(a, b):
    if a is not b:
        if a.left < b.left:
            draw(a, result)

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]

rects = []
for r1 in rect_list:
    addRect=True
    for r2 in rect_list:
        if(r1.intersects(r2)):
            pass
            r1.join(r2)
            #addRect=False
    if(addRect):
        rects.append(r1)

for rect in rects:
    draw(rect,result)


#l1, l2 = split_list(rect_list,2)
#collideAllVsAll(l1, l1, draw_rect)

print(len(rects))

#plt.subplot(121), plt.imshow(orig)
plt.subplot(122), plt.imshow(result)
plt.show()


