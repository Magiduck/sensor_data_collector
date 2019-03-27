try:
    from pyfirmata import Arduino, util
except:
    import pip

    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

from docopt import docopt  # Library for CLI
import time

from MicroController import MicroController  # Custom class to hold info of the arduino

# Command line options / menu
usage = """
Usage:
    sensor_data_collector.py 
    sensor_data_collector.py start <interval_in_seconds>
"""

args = docopt(usage)


def main():
    # Pyfirmata
    board = Arduino("COM4")
    it = util.Iterator(board)
    it.start()

    # Setting up pins on the Arduino board
    red_led = board.get_pin('d:6:o')
    blue_led = board.get_pin('d:10:o')
    temp_sensor = board.get_pin('a:0:i')
    temp_sensor.enable_reporting()
    photo_sensor = board.get_pin('a:2:i')
    photo_sensor.enable_reporting()
    center_button = board.get_pin('d:13:i')
    top_button = board.get_pin('d:12:i')
    top_button.enable_reporting()

    # Starting values
    is_outputting_photo = False
    time_start = time.time()
    debounce_start = time.time()

    # Custom object to store info of the Arduino micro controller
    micro_controller = MicroController(center_button, debounce_start, is_outputting_photo, photo_sensor, temp_sensor,
                                       time_start, red_led, blue_led, args)

    time.sleep(1)  # Important for pyfirmata to initialize before trying to read values
    print("Ready!")
    if args['start']:  # If the argument start was given
        while True:  # Infinite loop for not finishing the program but waiting on Arduino inputs
            read_data(micro_controller)  # Read the data from the Arduino


def read_data(micro_controller):
    """ Reading light sensor and temperature sensor data from the Arduino."""

    center_button_value = micro_controller.center_button.read()

    # Check if the button has been pressed, keeping in mind the debounce
    if center_button_value != 0 and time.time() - micro_controller.debounce_start > 0.2:
        # Set boolean to true or false based on if photo sensor should be outputting or temperature sensor
        micro_controller.set_outputting_photo(set_outputting_photo(micro_controller.is_outputting_photo,
                                                                   center_button_value))
        # Set the debounce again for the next loop
        micro_controller.set_debounce_start(time.time())

    # Read values of both sensors
    photo_value = micro_controller.photo_sensor.read()
    temp_value = micro_controller.temp_sensor.read()

    # Converting the raw output of the temp sensor into degrees celsius
    volt = 4.98
    degrees_celsius = ((temp_value * volt) / 0.01) - 273.15
    degrees_celsius = round(degrees_celsius, 2)

    # Print the data based on which sensor should be outputted
    print_data(micro_controller, photo_value, temp_value, degrees_celsius)


def set_outputting_photo(is_outputting_photo, center_button_value):
    """ Determining if the photo sensor or temperature sensor should be outputted."""
    # Just a simple switch when the button has been pressed
    if center_button_value == 1:
        if is_outputting_photo:
            return False
        else:
            return True


def print_data(micro_controller, photo_value, temp_value, degrees_celsius):
    """ Print the data from either the photo sensor or temperature sensor based on set_outputting_photo."""
    # Only continue if the user-specified interval (in seconds) has passed
    if time.time() - micro_controller.time_start > float(args['<interval_in_seconds>']):
        # Set start time for next loop
        micro_controller.set_time_start(time.time())
        if micro_controller.is_outputting_photo:  # Output the data from the photo sensor
            micro_controller.red_led.write(1)
            print(f"{time.strftime('%a %H:%M:%S')} - {photo_value} - {photo_value}")
            micro_controller.red_led.write(0)

        else:  # Output the data from the temperature sensor
            micro_controller.blue_led.write(1)
            print(f"{time.strftime('%a %H:%M:%S')} - {temp_value} - {degrees_celsius}")
            micro_controller.blue_led.write(0)


if __name__ == '__main__':
    main()
