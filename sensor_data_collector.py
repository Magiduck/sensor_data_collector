try:
    from pyfirmata import Arduino, util
except:
    import pip

    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

import time
from tkinter import *
import csv

from MicroController import MicroController  # Custom class to hold info of the arduino

is_running = False  # Global boolean to determine if data collection is on or not


def main():
    micro_controller = initiate_arduino()  # get information about the arduino and set it to micro_controller

    # Tkinter GUI creation
    root = Tk()
    output_text = Text(root)
    scrollbar = Scrollbar(root)
    entry = Entry(root)
    # Make the button determine what was typed in the entry field
    button = Button(root, text="send", command=lambda: determine_input(entry, root, output_text, micro_controller))
    # Some layout
    output_text.grid(row=0, column=0)
    scrollbar.grid(row=0, column=1, sticky='ns')  # Fill up from north to south
    entry.grid(row=1, column=0, sticky='we')  # Fill up from west to east
    button.grid(row=1, column=1)
    root.bind('<Return>', determine_input(entry, root, output_text, micro_controller))
    output_text.delete('1.0', END)
    # The menu to show to the user
    output_text.insert(END, "Welcome to the Sensor Data Collector made by Magor Katay and Tijs van Lieshout! \n"
                            "The following commands are accepted: \n\n"
                            "help, ? or menu \t\t\t\t\t\t     Shows this menu \n"
                            "start (temp | light | all) <interval_in_seconds> \t\t\t Starts the data collection \n"
                            "stop \t\t\t\t\t\t     Stops the data collection \n")
    root.mainloop()


def initiate_arduino():
    """ Sets up the Arduino port and pins. Returns a microController object for saving data about the Arduino."""
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


def determine_input(entry, root, output_text, micro_controller):
    """Determine which command the user has entered and call their respective functions"""
    command = entry.get()  # Get the command
    entry.delete(0, 'end')  # And clear the entry field
    global is_running   # Boolean to see if the program should collect data or not
    if "start" in command:  # Start the collection of data
        is_running = True
        start_data_collection(root, output_text, command, micro_controller)
    elif "stop" in command:   # Stop the collection of data
        is_running = False
        output_text.insert(END, "You have stopped the collection of data! \n")
    elif "help" or '?' or "HELP" or "Help" or "menu" or "Menu" or "MENU" in command:   # Show the help menu
        output_text.insert(END, "\n"
                                "Welcome to the Sensor Data Collector made by Magor Katay and Tijs van Lieshout! \n"
                                "The following commands are accepted: \n\n"
                                "help, ? or menu \t\t\t\t\t\t     Shows this menu \n"
                                "start (temp | light | all) <interval_in_seconds> \t\t\t Starts the data collection \n"
                                "stop \t\t\t\t\t\t     Stops the data collection \n")


def start_data_collection(root, output_text, command, micro_controller):
    """Starts the collection of data and updates the GUI accordingly. Creates a loop that runs until the user send the
    stop command."""
    # Open the csv file writer and write an header
    with open('output/collected_data.csv', 'w', newline='') as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerow(['Time stamp', 'Sensor name', 'Raw sensor value'])
        while is_running:
            read_data(micro_controller, output_text, command, data_writer)  # Read the data from the Arduino
            # Refreshing the GUI
            root.update_idletasks()
            root.update()


def read_data(micro_controller, output_window, command, data_writer):
    """ Reading light sensor and temperature sensor data from the Arduino."""

    # Read values of both sensors
    photo_value = micro_controller.photo_sensor.read()
    temp_value = micro_controller.temp_sensor.read()

    # Converting the raw output of the temp sensor into degrees celsius
    volt = 4.98
    degrees_celsius = ((temp_value * volt) / 0.01) - 273.15
    degrees_celsius = round(degrees_celsius, 2)

    # Print the data based on which sensor should be outputted
    print_and_write_data(micro_controller, photo_value, temp_value, degrees_celsius, output_window, command, data_writer)


def print_and_write_data(micro_controller, photo_value, temp_value, degrees_celsius, output_window, command, data_writer):
    """ Print and write the data to csv from either the photo sensor or temperature sensor based on
    set_outputting_photo. """
    # Only continue if the user-specified interval (in seconds) has passed
    interval = "1"
    if command == "start temp" or command == "start light" or command == "start all":
        interval = float(1)
    else:
        if "start temp" in command:
            interval = float(command.split("start temp")[1])
        if "start light" in command:
            interval = float(command.split("start light")[1])
        if "start all" in command:
            interval = float(command.split("start all")[1])
    if interval < 1:
        interval = 1
    elif interval > 3600:
        interval = 3600
    # Only do loop if interval has passed
    if time.time() - micro_controller.time_start > interval:
        timestamp = time.strftime('%a %H:%M:%S')
        # Set start time for next loop
        micro_controller.set_time_start(time.time())
        if "light" in command or "all" in command:
            # Blink LED, output to monitor and write to CSV file
            micro_controller.red_led.write(1)
            output_window.insert(END, f"Light sensor: {timestamp} - {photo_value} - {photo_value}\n")
            data_writer.writerow([timestamp, 'Light sensor', photo_value])
            micro_controller.red_led.write(0)
        if "temp" in command or "all" in command:
            # Blink LED, output to monitor and write to CSV file
            micro_controller.blue_led.write(1)
            output_window.insert(END, f"Temperature sensor: {timestamp} - {temp_value} - {degrees_celsius}\n")
            data_writer.writerow([timestamp, 'Temperature sensor', temp_value])
            micro_controller.blue_led.write(0)
        # output_window.config(state=DISABLED)
        if "all" in command:
            output_window.insert(END, "\n")
        output_window.see("end")


if __name__ == '__main__':
    main()
