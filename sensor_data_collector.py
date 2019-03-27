try:
    from pyfirmata import Arduino, util
except:
    import pip

    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

from docopt import docopt
import time

from MicroController import MicroController

usage = """
Usage:
    sensor_data_collector.py 
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
    top_button = board.get_pin('d:12:i')
    top_button.enable_reporting()

    is_outputting_photo = False

    time_start = time.time()
    debounce_start = time.time()

    micro_controller = MicroController(center_button, debounce_start, is_outputting_photo, photo_sensor, temp_sensor,
                                       time_start, red_led, blue_led, args)

    time.sleep(1)  # VERY IMPORTANT, NEEDS TO BE INCLUDED AT THE BEGINNING
    print("Ready!")
    if args['start'] or top_button.read() == 1:
        while True:
            read_data(micro_controller)


def read_data(micro_controller):
    center_button_value = micro_controller.center_button.read()
    # print(f"center_button_value: {center_button_value}")
    if center_button_value != 0 and time.time() - micro_controller.debounce_start > 0.2:
        micro_controller.set_outputting_photo(set_outputting_photo(micro_controller.is_outputting_photo,
                                                                   center_button_value))
        micro_controller.set_debounce_start(time.time())

    photo_value = micro_controller.photo_sensor.read()
    temp_value = micro_controller.temp_sensor.read()

    volt = 4.98
    degrees_celsius = ((temp_value * volt) / 0.01) - 273.15
    degrees_celsius = round(degrees_celsius, 2)

    print_data(micro_controller, photo_value, temp_value, degrees_celsius)


def set_outputting_photo(is_outputting_photo, center_button_value):
    if center_button_value == 1:
        if is_outputting_photo:
            return False
        else:
            return True


def print_data(micro_controller, photo_value, temp_value, degrees_celsius):
    if time.time() - micro_controller.time_start > float(args['<interval>']):
        micro_controller.set_time_start(time.time())
        if micro_controller.is_outputting_photo:
            micro_controller.red_led.write(1)
            print(f"{time.strftime('%a %H:%M:%S')} - {photo_value} - {photo_value}")
            micro_controller.red_led.write(0)

        else:
            micro_controller.blue_led.write(1)
            print(f"{time.strftime('%a %H:%M:%S')} - {temp_value} - {degrees_celsius}")
            micro_controller.blue_led.write(0)


if __name__ == '__main__':
    main()
