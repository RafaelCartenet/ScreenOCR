import pymouse
import time
import pytesseract
from PIL import ImageGrab
import multiprocessing as mp


class Box:

    def __init__(self, lang='en'):
        self.sub_boxes = {}

    def calibrate(self):
        # Load mouse class
        mouse = pymouse.PyMouse()

        print 64*'#','\n\n',17*' ','GET READY FOR BOX CALIBRATION','\n\n',64*'#'
        print '\nPlace the mouse on the TOP LEFT CORNER of the box.'
        raw_input('Press ENTER to capture mouse position')
        print 'DONE!'
        self.tlc_x, self.tlc_y = mouse.position()

        print '\nPlace the mouse on the BOTTOM RIGHT CORNER of box.'
        raw_input('Press ENTER to capture mouse position')
        print 'DONE!'
        self.brc_x, self.brc_y = mouse.position()
        print '\n',64*'#','\n\n',19*' ','END OF THE BOX CALIBRATION','\n\n',64*'#'

        self.box = (self.tlc_x, self.tlc_y, self.brc_x, self.brc_y)
        self.update_width_height()

    def update_width_height(self):
        self.width = abs(self.box[2] - self.box[0])
        self.height = abs(self.box[3] - self.box[1])

    def set_box(self, box):
        self.box = box
        self.update_width_height()

    def create_sub_boxes(self, config_file):
        """
        Load sub boxes. (x1, y1) and (x2, y2) represent the top left corner of
        the box and the bottom right corner of the box, respectively.
        Coordinates are given relatively to the current box coordinates.
        All 4 coordinates must be between 0 and 1
        """
        with open(config_file, 'r') as f:
            sub_boxes= f.readlines()

        for sub_box in sub_boxes:
            box_name, tlc_x, tlc_y, brc_x, brc_y = sub_box.split(' ')
            box = (
                float(tlc_x)*self.width,
                float(tlc_y)*self.height,
                float(brc_x)*self.width,
                float(brc_y)*self.height
            )
            self.sub_boxes[box_name] = Box()
            self.sub_boxes[box_name].set_box(box)

    def capture_zones_and_sub_zones(self):
        # Update main zone capture
        self.set_capture(ImageGrab.grab())
        self.update_capture()

        # Update sub zone captures
        for box_name in self.sub_boxes:
            self.sub_boxes[box_name].set_capture(self.box_image)
            self.sub_boxes[box_name].update_capture()

    def set_capture(self, capture):
        self.box_image = capture

    def update_capture(self):
        self.box_image = self.box_image.crop(self.box)
        self.box_image.load()

    def get_text(self, lang='fra'):
        """
        OCR. Get text from the box_image
        - lang: language for tesseract image_to_string
        """
        text = pytesseract.image_to_string(self.box_image, lang='fra')
        return text

    def get_text_process(self, image, output):
        """
        Parallel process for OCR.
        - image: PIL image to get text from
        - output: multiprocessing Queue (mp.Queue())
        """
        text = pytesseract.image_to_string(image['image'], lang='fra')
        result = {
            'box_name': image['box_name'],
            'text': text
        }
        output.put(result)

    def parallel_OCR(self, box_names):
        """
        Method to extract the text from all the given box_names sub_boxes of the
        current Box. Uses multiprocessing for efficiency.
        - box_names: names of the sub_boxes to extract text from
        return: results: list of OCR for all boxes
        """
        self.capture_zones_and_sub_zones()

        # Define an output queue
        output = mp.Queue()

        # Create image objects, with a box_name key so that we can find them
        # in the output queue
        images = []
        for box_name in box_names:
            image = {
                'box_name': box_name,
                'image': self.sub_boxes[box_name].box_image
            }
            images.append(image)

        # Define the process get_text_process to all sub boxes
        processes = [
            mp.Process(
                target=self.get_text_process,
                args=(image, output)
            ) for image in images]

        # Run the processes
        for process in processes:
            process.start()

        # Exit the completed processes
        for process in processes:
            process.join()

        # Get process results from the output queue
        results = [output.get() for process in processes]

        # Find the box_name key in the output key
        results = [filter(lambda x: x['box_name'] == box_name, \
            results)[0]['text'] for box_name in box_names]

        return results
