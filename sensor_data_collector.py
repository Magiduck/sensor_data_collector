from pyfirmata import Arduino, util
import time


def main():
    board = Arduino("COM4")
    it = util.Iterator(board)
    it.start()

    red_led = board.get_pin('d:6:o')
    blue_led = board.get_pin('d:10:o')
    temp_sensor = board.get_pin('a:0:i')
    photo_sensor = board.get_pin('a:2:i')

    time.sleep(1)  # VERY IMPORTANT, NEEDS TO BE INCLUDED AT THE BEGINNING
    photo_value = photo_sensor.read()
    temp_value = temp_sensor.read()
    print(f"Photo sensor value: {photo_value}")
    print(f"Photo sensor value in lux: {photo_value}")
    volt = 4.98
    degrees_celsius = ((temp_value*volt)/0.01)-273.15
    print(f"Temperature sensor value: {temp_value}")
    print(f"Temperature sensor value in degrees Celsius: {degrees_celsius}")

    # loop_times = input('How many times would you like the LED to blink: ')
    #
    # print('Blinking ' + loop_times + ' times.')
    #
    # time.sleep(1.0)
    # for x in range(int(loop_times)):
    #     digital_6.write(1)
    #     time.sleep(0.5)
    #     digital_6.write(0)
    #     time.sleep(0.5)


if __name__ == '__main__':
    main()
