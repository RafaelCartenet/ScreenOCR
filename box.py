import pymouse
import time
import pytesseract
from PIL import ImageGrab

class Box:

    def __init__(self, lang='en'):
        self.sub_boxes = {}
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

    def calibrate(self):
        # Load mouse class
        mouse = pymouse.PyMouse()

        print 64*'#','\n\n',17*' ','GET READY FOR BOX CALIBRATION','\n\n',64*'#'
        print '\nPlace the mouse on the TOP LEFT CORNER of the box.'
        raw_input('Press ENTER to capture mouse position')
        print 'DONE!'
        self.x1, self.y1 = mouse.position()

        print '\nPlace the mouse on the BOTTOM RIGHT CORNER of box.'
        raw_input('Press ENTER to capture mouse position')
        print 'DONE!'
        self.x2, self.y2 = mouse.position()
        print '\n',64*'#','\n\n',19*' ','END OF THE BOX CALIBRATION','\n\n',64*'#'
        self.update_width_height()

    def update_width_height(self):
        self.width = abs(self.x2 - self.x1)
        self.height = abs(self.y2 - self.y1)

    def set_corners(self, coordinates):
        self.x1= coordinates['x1']
        self.y1= coordinates['y1']
        self.x2= coordinates['x2']
        self.y2= coordinates['y2']
        self.update_width_height()

    def load_sub_boxes(self, config_file):
        """
        Load sub boxes. (x1, y1) and (x2, y2) represent the top left corner of
        the box and the bottom right corner of the box, respectively.
        Coordinates are given relatively to the current box coordinates.
        All 4 coordinates must be between 0 and 1
        """
        with open(config_file, 'r') as f:
            sub_boxes= f.readlines()

        for sub_box in sub_boxes:
            box_name, x1, y1, x2, y2 = sub_box.split(' ')
            self.sub_boxes[box_name] = Box()
            self.sub_boxes[box_name].set_corners({
                'x1': self.x1 + float(x1) * self.width,
                'y1': self.y1 + float(y1) * self.height,
                'x2': self.x1 + float(x2) * self.width,
                'y2': self.y1 + float(y2) * self.height,
            })

    def get_text(self):
        grab_time = time.time()
        image= ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
        # print 'screenshot', time.time() - grab_time

        crop_time = time.time()
        # print 'crop', time.time() - crop_time

        OCR_time = time.time()
        text = pytesseract.image_to_string(image, lang='fra')
        # print 'OCR', time.time() - OCR_time
        return text


    def get_sub_box_text(self, box_name):
        if box_name not in self.sub_boxes:
            raise ValueError('No sub box called %s:'% box_name)
        return self.sub_boxes[box_name].get_text()
