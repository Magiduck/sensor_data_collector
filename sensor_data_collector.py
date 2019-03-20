from pyfirmata import Arduino, util

import time


def main():
    board = Arduino("COM4")
    digital_6 = board.get_pin('d:6:o')

    loop_times = input('How many times would you like the LED to blink: ')

    print('Blinking ' + loop_times + ' times.')

    time.sleep(1.0)
    for x in range(int(loop_times)):
        digital_6.write(1)
        time.sleep(0.5)
        digital_6.write(0)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
