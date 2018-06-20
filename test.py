

from box import Box

box = Box()

while True:
    raw_input('Press ENTER to start searching text')
    box.calibrate()
    box.get_text()
