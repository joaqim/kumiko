#!/usr/bin/env python3
import json
import argparse
from os import stat
from glob import iglob
from collections import defaultdict

from pathlib import Path, PurePath
from PIL import Image

from panelextractor import *

class DeepDict2(defaultdict):
    def __call__(self):
        return DeepDict(self.default_factory)

def _sub_getitem(self, k):
    try:
        # sub.__class__.__bases__[0]
        real_val = self.__class__.mro()[-2].__getitem__(self, k)
        val = '' if real_val is None else real_val
    except Exception:
        val = ''
        real_val = None
    # isinstance(Avoid,dict)也是true，会一直递归死
    if type(val) in (dict, list, str, tuple):
        val = type('Avoid', (type(val),), {'__getitem__': _sub_getitem, 'pop': _sub_pop})(val)
        # 重新赋值当前字典键为返回值，当对其赋值时可回溯
        if all([real_val is not None, isinstance(self, (dict, list)), type(k) is not slice]):
            self[k] = val
    return val


def _sub_pop(self, k=-1):
    try:
        val = self.__class__.mro()[-2].pop(self, k)
        val = '' if val is None else val
    except Exception:
        val = ''
    if type(val) in (dict, list, str, tuple):
        val = type('Avoid', (type(val),), {'__getitem__': _sub_getitem, 'pop': _sub_pop})(val)
    return val

class DeepDict(dict):
    def __getitem__(self, k):
        return _sub_getitem(self, k)

    def pop(self, k):
        return _sub_pop(self, k)
    def append(self, k, val):
        return self.update( {k: val} )

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class Rect:
    def __init__(self, x=0, y=0, width=0, height=0, data=None, img_data=None, img=None):
        if data is not None:
            self.x = data['x'];
            self.x = data['y'];
            self.w = data['width'];
            self.h = data['height'];
        if img_data is not None:
            self.x = 0;
            self.x = 0;
            self.w = img_data['img_size'][0];
            self.h = img_data['img_size'][1];
        elif img is not None:
            self.x = 0;
            self.x = 0;
            self.w = img.width
            self.h = img.width
        else:
            self.x = x;
            self.y = y;
            self.width = width;
            self.height = height;

    def getScaleX(self, r2):
        return max(self.w / r2.w, r2.w / self.w);
    def getScaleY(self, r2):
        return max(self.h / r2.h, r2.h / self.h);

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-i','--input_json', type=str, default='comics.json', required=False);
parser.add_argument('-o','--output_json', type=str, default='comics_hq_newest.json', required=False);
parser.add_argument('-d','--dir', type=str, default='./', required=False);
parser.add_argument("-v", "--verbose", required=False, action='store_true',
                        help="Show debug images")

args = parser.parse_args()

debug = args.verbose



class Pro:
    def __init__(self):
        self.rel_dir = args.dir;
        if self.rel_dir != './':
            if self.rel_dir[0] == '.':
                self.rel_dir = self.rel_dir[2:] # Remove beginning './' from relative_dir

        self.input_json_path = Path(self.rel_dir+'/'+args.input_json);
        if self.input_json_path.exists():
            with open(self.input_json_path, 'r') as self.json_file:
                self.json_data = defaultdict(json.load(self.json_file));
                #self.json_data = DeepDict(json.load(self.json_file));
        else:
            self.json_data = defaultdict()#DeepDict()

    def add_scale(self, img_src):
        img_path = '/'.join(img_src.split('/')[:-1]);
        img_name = img_src.split('/')[-1];
        if img_path[0] == '.':
            img_path = img_path[2:] # Remove beginning './' from relative_dir


        hq_path = Path(self.rel_dir + '/' + str(img_path) + '/hq');

        if not hq_path.is_dir():
            print('No hq folder in: ' + str(hq_path) + '\n-- for image: ' + img_name);
            return False;

        hq_src = Path(self.rel_dir + '/' + str(img_path) + '/hq/' + img_name);

        if not hq_src.is_file():
            print('No hq file in: ' + str(hq_src)+ '\n-- for image: ' + img_name);
            return False

        img=Rect(img=Image.open(str(hq_src)))
        p = Rect(img=Image.open(str(img_src)))
        scaleX = p.getScaleX(img);
        #scaleX = min(p.getScaleX(img), p.getScaleY(img));
        #scaleX = p.getScaleX(img);
        #scaleY = p.getScaleY(img);
        self.json_page = {
        'img_size': (p.w, p.h),
        'scaleX': scaleX,
        'scaleY': scaleX,
        'filename_hq':str('./' + img_path + '/hq/' + img_name)
        }
        #page['img_size'] = (p.w, p.h)
        #page['scaleX'] = scaleX;
        #page['scaleY'] = scaleX;
        #page['filename_hq'] = str('./' + img_path + '/hq/' + img_name);
        print(scaleX);
        return True;

    def process(self, input_json):
        with open(self.rel_dir + '/' + input_json, 'r') as json_file:
            self.json_data = json.load(json_file);
            for name in iter(self.json_data):
                print('----');
                print(name);
                print('----');
                for chapter in self.json_data[name]:
                        print('chapter:')
                        print(chapter);
                        print('----');
                        for page_nr in self.json_data[name][chapter]:
                                self.json_page = self.json_data[name][chapter][page_nr];
                                print(page_nr);
                                if not self.add_scale(self.json_page['filename']):
                                        break;
                                self.json_data[name][chapter][page_nr] = self.json_page;

    def process_panels(self, input_json):
        with open(self.rel_dir + '/' + input_json, 'r') as json_file:
            self.json_data = json.load(json_file);
            for name in iter(self.json_data):
                print('----');
                print(name);
                print('----');
                for chapter in self.json_data[name]:
                        print('chapter:')
                        print(chapter);
                        print('----');
                        for page_nr in self.json_data[name][chapter]:
                                self.json_page = self.json_data[name][chapter][page_nr];

                                image = cv2.imread(self.json_page['filename'])
                                comicPanels = findComicPanels(image)
                                panel_nr = 0
                                panel_count = len(comicPanels)
                                for panelInfo in comicPanels:
                                    x, y, w, h = panelInfo[0];
                                    self.json_page['panel_count'] = panel_count
                                    self.json_page[str(panel_nr)] = {
                                        'x': x,
                                        'y': y,
                                        'width': w,
                                        'height': h
                                    }
                                self.json_data[name][chapter][page_nr] = self.json_page;

    def create_json(self):
        json_comic = {}

        context = {}
        for img_src in iglob(self.rel_dir + '**[!hq]/*.png', recursive=True):
            img_path = PurePath(img_src)
            img_name = Path(img_path.name)
            # Try to convert filename from alhanumericals to int 001.png -> 1
            try:
                page_nr = int(img_name.stem)
                page_nr = str(page_nr) # Back to string for use as json key
            except ValueError:
                continue
            print(img_src)
            print(page_nr)

            comic_path = PurePath(img_path.parent)
            comic_title = comic_path.name
            comic_base_dir = PurePath(comic_path.parent)
            comic_name = comic_base_dir.name

            if (comic_name == ""):
                comic_name = "."

            self.json_page = {}
            self.add_scale(img_src)
            json_page = {
                'page_nr': page_nr,
               'filename': img_src
            }
            json_page = {**json_page, **self.json_page}
            #context = json_page

            context.update({
                page_nr: json_page
            })

        print(context)
        self.json_data.update({ comic_name: context})

    def save_json(self):
        print("Saving json:" + args.output_json)
        print (self.json_data)

        with open(args.output_json, 'w') as out_file:
            json.dump(self.json_data, out_file)
        print("end")

pro = Pro();
pro.create_json()
pro.save_json();
#pro.process_panels(args.output_json);
#pro.save_json();

#pro.process(args.output_json);

