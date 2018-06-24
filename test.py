import time

from box import Box

box = Box()

while True:
    raw_input('Press ENTER to start searching text')
    box.calibrate()
    print box.x1, box.y1
    print box.x2, box.y2
    print
    # box.get_text()

# box.calibrate()
# config_file= 'config/iphone_quicktime_hotspot.txt'
# box.load_sub_boxes(config_file)
#
# while True:
#     raw_input('Press ENTER to start searching text')
#     OCR_time = time.time()
#     print 'question', box.get_sub_box_text('question')
#     print 'choix1', box.get_sub_box_text('choice1')
#     print 'choix2', box.get_sub_box_text('choice2')
#     print 'choix3', box.get_sub_box_text('choice3')
#     print 'OCR time', time.time() - OCR_time
