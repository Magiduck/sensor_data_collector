try:
    from pyfirmata import Arduino, util
except:
    import pip

    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

from docopt import docopt

import time

usage = """
Usage: 
    sensor_data_collector.py start <interval>
"""

args = docopt(usage)

def main():
    board = Arduino("COM4")
    it = util.Iterator(board)
    it.start()

    red_led = board.get_pin('d:6:o')
    blue_led = board.get_pin('d:10:o')
    temp_sensor = board.get_pin('a:0:i')
    temp_sensor.enable_reporting()
    photo_sensor = board.get_pin('a:2:i')
    photo_sensor.enable_reporting()
    center_button = board.get_pin('d:13:i')
    center_button.enable_reporting()

    is_outputting_photo = False

    time_start = time.time()
    debounce_start = time.time()

    time.sleep(1)  # VERY IMPORTANT, NEEDS TO BE INCLUDED AT THE BEGINNING
    print("Ready!")
    if args['start']:
        while True:
            center_button_value = center_button.read()
            # print(f"center_button_value: {center_button_value}")
            if center_button_value != 0 and time.time() - debounce_start > 0.2:
                is_outputting_photo = set_outputting_photo(is_outputting_photo, center_button_value)
                debounce_start = time.time()

            red_led.write(1)
            photo_value = photo_sensor.read()
            temp_value = temp_sensor.read()

            volt = 4.98
            degrees_celsius = ((temp_value * volt) / 0.01) - 273.15

            if time.time() - time_start > float(args['<interval>']):
                time_start = time.time()
                if is_outputting_photo:
                    print(f"Photo sensor value: {photo_value}")
                    print(f"Photo sensor value in lux: {photo_value}")
                else:
                    print(f"Temperature sensor value: {temp_value}")
                    print(f"Temperature sensor value in degrees Celsius: {degrees_celsius}")

            red_led.write(0)


def set_outputting_photo(is_outputting_photo, center_button_value):
    if center_button_value == 1:
        if is_outputting_photo:
            return False
        else:
            return True


if __name__ == '__main__':
    main()
