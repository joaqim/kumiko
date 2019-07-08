#!/usr/bin/env python


import os
import cv2 as cv
import numpy as np


def range_overlap(a_min, a_max, b_min, b_max):
    '''Neither range is completely greater than the other
    '''
    return (a_min <= b_max) and (b_min <= a_max)


def imgcrop(img, x1, y1, x2, y2):
    #x1, y1, x2, y2 = bbox
    result = img
    if x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
        result, x1, x2, y1, y2 = pad_img_to_fit_bbox(result, x1, x2, y1, y2)

    #cv.imshow("img", result[y1:y2, x1:x2])
    return result[y1:y2, x1:x2]


def pad_img_to_fit_bbox(img, x1, x2, y1, y2):
    img = np.pad(img, ((np.abs(np.minimum(0, y1)), np.maximum(y2 - img.shape[0], 0)),
                       (np.abs(np.minimum(0, x1)), np.maximum(x2 - img.shape[1], 0)), (0, 0)), mode="constant")
    y1 += np.abs(np.minimum(0, y1))
    y2 += np.abs(np.minimum(0, y1))
    x1 += np.abs(np.minimum(0, x1))
    x2 += np.abs(np.minimum(0, x1))
    return img, x1, x2, y1, y2


def point_of_gradient(img):
    #result, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    unused, thresh = cv.threshold(
        img, 127, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

    dx = cv.Sobel(thresh, cv.CV_32F, 1, 0)
    dy = cv.Sobel(thresh, cv.CV_32F, 0, 1)

    average_dx = np.mean(dx)
    average_dy = np.mean(dy)

    average_gradient = np.arctan2(-average_dy, average_dx)

    center = (thresh.shape[1]/2, thresh.shape[0]/2)
    direction = (np.cos(average_gradient) * 100, -
                 np.sin(average_gradient) * 100)
    #cv.line(img, center, center + direction, (0,0,255), 10)
    cv.line(img, (center[0], center[1]), (int(
        center[0] + direction[0]), int(center[1] + direction[1])), (0, 20, 200), 2)

    cv.imshow('', img)
    cv.waitKey(0)
    cv.destroyAllWindows()


class Kumiko:

    options = {}
    img = False

    def __init__(self, options={}):

        if 'debug' in options:
            self.options['debug'] = options['debug']
        else:
            self.options['debug'] = False

        if 'reldir' in options:
            self.options['reldir'] = options['reldir']
        else:
            self.options['reldir'] = os.getcwd()

    def read_image(self, filename):
        return cv.imread(filename)
        # return cv.imread(filename, cv.CV_LOAD_IMAGE_COLOR)
        # return cv.imread(filename, cv.IMREAD_COLOR)
        # return cv.imread(filename, cv.IMREAD_ANYDEPTH)

    def parse_dir(self, directory):
        filenames = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filenames.append(os.path.join(root, filename))
        filenames.sort()
        #filenames = filenames[0:10]
        return self.parse_images(filenames)

    def parse_images(self, filenames=[]):
        infos = []
        for filename in filenames:
            info = self.parse_image(filename)
            # infos.append(self.parse_image(filename))
            if info is None:
                pass
            else:
                infos.append(info)
        return infos

    def estim_image2(self, img, thrshld):
        is_light = np.mean(img) > thrshld
        return 'light' if is_light else 'dark'

    def estim_image(self, img, thrshld):
        # With kernel size depending upon image size
        blur = cv.blur(img, (5, 5))
        # The range for a pixel's value in grayscale is (0-255), 127 lies midway
        if cv.mean(blur) > thrshld:
            return 'light'  # (127 - 255) denotes light image
        else:
            return 'dark'  # (0 - 127) denotes dark image

    def parse_image(self, filename):
        img = self.read_image(filename)
        # TODO: handle error
        # if len(img.shape) < 2:
        try:
            img.shape
            #print("checked for shape".format(img.shape))
        except AttributeError:
            print("shape not found")
            return
            # code to move to next frame
        if img.shape[2] < 2:
            return

        size = list(img.shape[:2])
        size.reverse()  # get a [width,height] list

        infos = {
            'filename': os.path.relpath(filename, self.options['reldir']),
            'size': size,
            'panels': []
        }

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Erode
        #kernel = np.ones((5,5),np.uint8)
       # gray = cv.erode(gray,kernel,iterations = 1)
        # Opening
        #gray = cv.morphologyEx(gray, cv.MORPH_OPEN, kernel)

#                if(self.estimate_image(gray) == 'dark'):

#                if(self.img_estim(gray, 170) == 'dark'):
#                    gray = cv.bitwise_not(gray)

        height, width, channels = img.shape

        #trsh = 255
        #trsh = 180
        trsh = 20

        black_border = 0
        #size = 40

        if(self.estim_image2(imgcrop(gray, 0, 0, 15, height), trsh) == 'dark'):
            black_border += 1
        if(self.estim_image2(imgcrop(gray, 0, 0, width, 15), trsh) == 'dark'):
            black_border += 1

        # y:y+w, x:x+w
        # Upper border (0,20) -> (width-20,0)
        # if(self.img_estim(gray[size:0, size:width], trsh) == 'dark'):
            #black_border += 1

        # if(self.img_estim(gray[0:size, height:height+size], trsh) == 'dark'):
            #black_border += 1

        # Left border (20,0) -> (height+20,0)
        # if(self.img_estim(gray[20:0, 0:20+height], trsh) == 'dark'):
            #black_border += 1

        # point_of_gradient(gray);

#                point_of_gradient(imgcrop(gray, 0, 0, 15, height))
#                cv.imshow("image",img);
#                cv.waitKey(0)
#                cv.destroyAllWindows()

        if(black_border >= 1):
            gray = cv.bitwise_not(gray)

        tmin = 220
        tmax = 255
        ret, thresh = cv.threshold(gray, tmin, tmax, cv.THRESH_BINARY_INV)

        # OpenCV 3.2+
        # See https://docs.opencv.org/master/d4/d73/tutorial_py_contours_begin.html

        #im2, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # cv.imwrite('tmp/contour.jpg',im2)
        # cv.imwrite('tmp/hierarchy.jpg',hierarchy)
        # print contours

        # OpenCV 2.4
        # https://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html

        contours, hierarchy = cv.findContours(
            thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        # Get panels out of contours
#		for contour in contours:
        for i in range(0, len(contours)):
            if hierarchy[0, i, 3] != -1:
                continue

            contour = contours[i]

            arclength = cv.arcLength(contour, True)

            epsilon = 0.03 * arclength
            approx = cv.approxPolyDP(contour, epsilon, True)

            # the contour is 'bad' if it is not a rectangle
            if not len(approx) >= 2:
                continue

            x, y, w, h = cv.boundingRect(approx)

            # exclude very small panels
            if w < infos['size'][0]/8 or h < infos['size'][1]/15:
                continue

            contourSize = int(sum(infos['size']) / 2 * 0.004)
            cv.drawContours(img, [approx], 0, (0, 0, 255), contourSize)

            panel = [x, y, w, h]
            infos['panels'].append(panel)

        # if len(infos['panels']) <= 1:
            # infos['panels'].append([0,0,infos['size'][0],infos['size'][1]]);

        if len(infos['panels']) > 1:
            for panel in infos['panels']:
                x, y, w, h = panel
                panel = {
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h
                }
            else:
                for panel in infos['panels']:
                    x, y, w, h = panel
                    panel = {
                        'x': 0,
                        'y': 0,
                        'w': img.shape[0],
                        'h': img.shape[1]
                    }

        # Number infos['panels'] comics-wise (left to right for now)
        self.gutterThreshold = sum(infos['size']) / 2 / 20
        # infos['panels'].sort(cmp=self.sort_panels)
        infos['panels'].sort(cmp=self.sort_panels_manga)

        # write panel numbers on debug img
        fontRatio = sum(infos['size']) / 2 / 400
        font = cv.FONT_HERSHEY_SIMPLEX
        fontScale = 1 * fontRatio
        fontColor = (0, 0, 255)
        lineType = 2
        n = 0
        for panel in infos['panels']:
            n += 1
            position = (int(panel[0]+panel[2]/2), int(panel[1]+panel[3]/2))
            cv.putText(img, str(n), position, font,
                       fontScale, fontColor, lineType)

        if (self.options['debug']):
            cv.imwrite(os.path.join('debug', os.path.basename(
                filename)+'-040-contours-numbers.jpg'), img)

        return infos

    def sort_panels(self, p1, p2):
        [p1x, p1y, p1w, p1h] = p1
        [p2x, p2y, p2w, p2h] = p2

        p1b = p1y+p1h  # p1's bottom
        p2b = p2y+p2h  # p2's bottom
        p2r = p1x+p1w  # p1's right side
        p1r = p2x+p2w  # p2's right side

        # p1 is above p2
        if p2y >= p1b - self.gutterThreshold and p2y >= p1y - self.gutterThreshold:
            return -1

        # p1 is below p2
        if p1y >= p2b - self.gutterThreshold and p1y >= p2y - self.gutterThreshold:
            return 1

        # p1 is left from p2
        if p2x >= p1r - self.gutterThreshold and p2x >= p1x - self.gutterThreshold:
            return -1

        # p1 is right from p2
        if p1x >= p2r - self.gutterThreshold and p1x >= p2x - self.gutterThreshold:
            return 1

        return 0  # should we really fall into this case?

    def sort_panels_manga(self, p1, p2):
        [p1x, p1y, p1w, p1h] = p1
        [p2x, p2y, p2w, p2h] = p2

        p1b = p1y+p1h  # p1's bottom
        p2b = p2y+p2h  # p2's bottom
        p1r = p1x+p1w  # p1's right side
        p2r = p2x+p2w  # p2's right side

        # p1 is above p2
        if p2y >= p1b - self.gutterThreshold and p2y >= p1y - self.gutterThreshold:
            return -1

        # p1 is below p2
        if p1y >= p2b - self.gutterThreshold and p1y >= p2y - self.gutterThreshold:
            return 1

        # p1 is left from p2
        if p2x >= p1r - self.gutterThreshold and p2x >= p1x - self.gutterThreshold:
            return 1

        # p1 is right from p2
        if p1x >= p2r - self.gutterThreshold and p1x >= p2x - self.gutterThreshold:
            return -1

        return 0  # should we really fall into this case?
