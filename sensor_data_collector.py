try:
    from pyfirmata import Arduino, util
except:
    import pip

    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

import time
from tkinter import *

from MicroController import MicroController  # Custom class to hold info of the arduino

is_running = False


def main():
    micro_controller = initiate_arduino()

    root = Tk()
    output_text = Text(root)
    scrollbar = Scrollbar(root)
    entry = Entry(root)
    button = Button(root, text="send", command=lambda: determine_input(entry, root, output_text, micro_controller))
    output_text.grid(row=0, column=0)
    scrollbar.grid(row=0, column=1, sticky='ns')
    entry.grid(row=1, column=0, sticky='we')
    button.grid(row=1, column=1)
    root.bind('<Return>', determine_input(entry, root, output_text, micro_controller))
    output_text.delete('1.0', END)
    output_text.insert(END, "Welcome to the Sensor Data Collector made by Magor Katay and Tijs van Lieshout! \n"
                            "The following commands are accepted: \n\n"
                            "help, ? or menu \t\t\t\t\t Shows this menu \n"
                            "start <interval_in_seconds> \t\t\t\t\t Starts the data collection \n"
                            "stop \t\t\t\t\t Stops the data collection \n")
    root.mainloop()


def determine_input(entry, root, output_text, micro_controller):
    command = entry.get()
    entry.delete(0, 'end')
    global is_running
    if "start" in command:
        is_running = True
        start_data_collection(root, output_text, command, micro_controller)
    elif "stop" in command:
        is_running = False
        output_text.insert(END, "You have stopped the collection of data! \n")
    elif "help" or "?" or "HELP" or "Help" or "menu" or "Menu" or "MENU" in command:
        output_text.insert(END, "\n"
                                "Welcome to the Sensor Data Collector made by Magor Katay and Tijs van Lieshout! \n"
                                "The following commands are accepted: \n\n"
                                "help, ? or menu \t\t\t\t\t Shows this menu \n"
                                "start <interval_in_seconds> \t\t\t\t\t Starts the data collection \n"
                                "stop \t\t\t\t\t Stops the data collection \n")


def initiate_arduino():
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
                                       time_start, red_led, blue_led)

    time.sleep(1)  # Important for pyfirmata to initialize before trying to read values
    print("Ready!")

    return micro_controller


def start_data_collection(root, output_text, command, micro_controller):
    if command == "start":
        interval = "1"
    else:
        interval = command.split("start")[1]

    while is_running:
        read_data(micro_controller, output_text, interval)  # Read the data from the Arduino
        root.update_idletasks()
        root.update()


def read_data(micro_controller, output_window, interval):
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
    print_data(micro_controller, photo_value, temp_value, degrees_celsius, output_window, interval)


def set_outputting_photo(is_outputting_photo, center_button_value):
    """ Determining if the photo sensor or temperature sensor should be outputted."""
    # Just a simple switch when the button has been pressed
    if center_button_value == 1:
        if is_outputting_photo:
            return False
        else:
            return True


def print_data(micro_controller, photo_value, temp_value, degrees_celsius, output_window, interval):
    """ Print the data from either the photo sensor or temperature sensor based on set_outputting_photo."""
    # Only continue if the user-specified interval (in seconds) has passed
    if time.time() - micro_controller.time_start > float(interval):
        # Set start time for next loop
        micro_controller.set_time_start(time.time())
        if micro_controller.is_outputting_photo:  # Output the data from the photo sensor
            micro_controller.red_led.write(1)
            output_window.insert(END, f"{time.strftime('%a %H:%M:%S')} - {photo_value} - {photo_value}\n")
            micro_controller.red_led.write(0)
        else:  # Output the data from the temperature sensor
            micro_controller.blue_led.write(1)
            output_window.insert(END, f"{time.strftime('%a %H:%M:%S')} - {temp_value} - {degrees_celsius}\n")
            micro_controller.blue_led.write(0)
        # output_window.config(state=DISABLED)
        output_window.see("end")


if __name__ == '__main__':
    main()
