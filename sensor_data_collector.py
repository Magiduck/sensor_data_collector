try:
    from pyfirmata import Arduino, util
except:
    import pip
    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

import time


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
    center_button = board.get_pin('d:13:0')
    center_button.enable_reporting()

    previous_button_value = 0

    is_reading_values = False

    time.sleep(1)  # VERY IMPORTANT, NEEDS TO BE INCLUDED AT THE BEGINNING
    print("Ready!")
    while True:
        center_button_value = center_button.read()
        is_reading_values = set_reading_values(is_reading_values, center_button_value, previous_button_value)

        if is_reading_values:
            print(is_reading_values)
            red_led.write(1)
            photo_value = photo_sensor.read()
            temp_value = temp_sensor.read()
            print(f"Photo sensor value: {photo_value}")
            print(f"Photo sensor value in lux: {photo_value}")
            volt = 4.98
            degrees_celsius = ((temp_value * volt) / 0.01) - 273.15
            print(f"Temperature sensor value: {temp_value}")
            print(f"Temperature sensor value in degrees Celsius: {degrees_celsius}")
            red_led.write(0)
        previous_button_value = center_button_value


def set_reading_values(is_reading_values, center_button_value, previous_button_value):
    if center_button_value == 1 and previous_button_value == 0:
        if is_reading_values:
            return False
        else:
            return True


if __name__ == '__main__':
    main()
