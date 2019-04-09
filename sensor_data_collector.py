try:
    from pyfirmata import Arduino, util
except:
    import pip

    pip.main(['install', "pyfirmata"])
    from pyfirmata import Arduino, util

import time
from tkinter import *
import csv
import os

from MicroController import MicroController  # Custom class to hold info of the Arduino

is_running = False  # Global boolean to determine if data collection is on or not
is_waiting = False  # Global boolean to determine if data collection should be on (Arduino button related)


def main():
    """ The main function which sets up the GUI"""
    micro_controller = initiate_arduino()  # Get information about the Arduino and set it to micro_controller

    # Tkinter GUI creation
    root = Tk()
    root.title("Sensor Data Collector")
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
    root.resizable(width=False, height=False)
    root.bind('<Return>', (lambda event: determine_input(entry, root, output_text, micro_controller)))
    output_text.delete('1.0', END)
    # The menu to show to the user
    output_text.insert(END, "Welcome to the Sensor Data Collector made by Magor Katay and Tijs van Lieshout! \n"
                            "The following commands are accepted: \n\n"
                            "help, ? or menu \t\t\t\t Shows this menu \n"
                            "start (temp | light | all) <interval_in_seconds> \t\t\t Starts the data collection \n"
                            "stop \t\t\t\t Stops the data collection \n"
                            "list \t\t\t\t Lists the CSV files of collected data \n"
                            "display <ID of CSV file> \t\t\t\t displays a csv file with some stats \n"
                            "wait \t\t\t\t Toggle to wait for input on the Arduino \n")
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
    center_button.enable_reporting()

    # Starting values
    time_start = time.time()  # Used for the interval
    debounce_start = time.time()  # Used for the button bouncing

    # Custom object to store info of the Arduino micro controller
    micro_controller = MicroController(center_button, debounce_start, photo_sensor, temp_sensor,
                                       time_start, red_led, blue_led)

    time.sleep(1)  # Important for pyfirmata to initialize before trying to read values
    print("Ready!")

    return micro_controller


def determine_input(entry, root, output_text, micro_controller):
    """ Determine which command the user has entered and call their respective functions"""
    command = entry.get()  # Get the command
    entry.delete(0, 'end')  # And clear the entry field
    global is_running   # Boolean to see if the program should collect data or not
    if "start" in command:  # Start the collection of data
        is_running = True
        start_data_collection(root, output_text, command, micro_controller)
    elif "stop" in command:   # Stop the collection of data
        is_running = False
        output_text.insert(END, "You have stopped the collection of data! \n")
    elif "list" in command:  # lists the csv files that contain collection of data
        list_csv_files(output_text)
    elif "display" in command:  # displays data of chosen csv file
        display_csv_file(command, output_text)
    elif "wait" in command:  # waits for input on the Arduino
        wait_for_arduino(root, output_text, command, micro_controller)
    elif "help" or '?' or "HELP" or "Help" or "menu" or "Menu" or "MENU" in command:   # Show the help menu
        output_text.insert(END, "\n"
                                "Welcome to the Sensor Data Collector made by Magor Katay and Tijs van Lieshout! \n"
                                "The following commands are accepted: \n\n"
                                "help, ? or menu \t\t\t\t Shows this menu \n"
                                "start (temp | light | all) <interval_in_seconds> \t\t\t Starts the data collection \n"
                                "stop \t\t\t\t Stops the data collection \n"
                                "list \t\t\t\t Lists the CSV files of collected data \n"
                                "display <ID of CSV file> \t\t\t\t displays a csv file with some stats \n"
                                "wait \t\t\t\t Toggle to wait for input on the Arduino \n")
    output_text.see("end")


def start_data_collection(root, output_text, command, micro_controller):
    """ Starts the collection of data and updates the GUI accordingly. Creates a loop that runs until the user send the
    stop command."""
    # Open the csv file writer and write an header
    csvfilename = 'output/collected_data_' + time.strftime('%a %H:%M:%S') + '.csv'
    csvfilename = csvfilename.replace(' ', '_')
    csvfilename = csvfilename.replace(':', "_")
    with open(csvfilename.lower(), 'w', newline='') as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerow(['Time stamp', 'Sensor name', 'Raw sensor value'])
        global is_running
        should_run = False  # For waiting on the Arduino button input
        while is_running:
            if command == "wait":  # Data collection started with wait command
                center_button_value = micro_controller.center_button.read()
                # Check if the button has been pressed, keeping in mind the debounce
                if center_button_value != 0 and time.time() - micro_controller.debounce_start > 0.2:
                    if should_run:
                        should_run = False
                        is_running = False
                    else:
                        should_run = True
                    # Set the debounce again for the next loop
                    micro_controller.set_debounce_start(time.time())
                if should_run:
                    read_data(micro_controller, output_text, command, data_writer)  # Read the data from the Arduino
            else:  # Data collection started with start command
                read_data(micro_controller, output_text, command, data_writer)  # Read the data from the Arduino
            # Refreshing the GUI
            root.update_idletasks()
            root.update()


def read_data(micro_controller, output_text, command, data_writer):
    """ Reading light sensor and temperature sensor data from the Arduino."""

    # Read values of both sensors
    photo_value = micro_controller.photo_sensor.read()
    temp_value = micro_controller.temp_sensor.read()

    # Voltage of the Arduino
    volt = 4.98

    # Converting the raw output of the photo sensor into lux
    vout = photo_value * volt
    ldr_resistance = 10.0 * ((5-vout)/vout)
    lux = 500 / ldr_resistance

    # Converting the raw output of the temp sensor into degrees celsius
    degrees_celsius = ((temp_value * volt) / 0.01) - 273.15
    degrees_celsius = round(degrees_celsius, 2)
    # Print the data based on which sensor should be outputted
    print_and_write_data(micro_controller, photo_value, lux, temp_value, degrees_celsius, output_text, command,
                         data_writer)


def print_and_write_data(micro_controller, photo_value, lux, temp_value, degrees_celsius, output_text, command,
                         data_writer):
    """ Print and write the data to csv from either the photo sensor or temperature sensor based on users input. """
    # Only continue if the user-specified interval (in seconds) has passed
    interval = "1"
    if command == "wait" or command == "start temp" or command == "start light" or command == "start all":
        interval = float(1)
    else:
        if "start temp" in command:
            interval = float(command.split("start temp ")[1])
        if "start light" in command:
            interval = float(command.split("start light ")[1])
        if "start all" in command:
            interval = float(command.split("start all ")[1])
    if interval < 1:
        interval = 1
    elif interval > 3600:
        interval = 3600
    # Only do loop if interval has passed
    if time.time() - micro_controller.time_start > interval:
        timestamp = time.strftime('%a %H:%M:%S')
        # Set start time for next loop
        micro_controller.set_time_start(time.time())
        if "light" in command or "all" in command or "wait" in command:
            # Blink LED, output to monitor and write to CSV file
            micro_controller.red_led.write(1)
            output_text.insert(END, f"Light sensor: {timestamp} - {photo_value} - {lux}\n")
            data_writer.writerow([timestamp, 'Light sensor', photo_value])
            micro_controller.red_led.write(0)
        if "temp" in command or "all" in command or "wait" in command:
            # Blink LED, output to monitor and write to CSV file
            micro_controller.blue_led.write(1)
            output_text.insert(END, f"Temperature sensor: {timestamp} - {temp_value} - {degrees_celsius}\n")
            data_writer.writerow([timestamp, 'Temperature sensor', temp_value])
            micro_controller.blue_led.write(0)
        if "all" in command or "wait" in command:
            output_text.insert(END, "\n")
        output_text.see("end")


def list_csv_files(output_text):
    """ Display a list to the user of csv files in the output directory."""
    counter = 0
    output_text.insert(END, "ID: \t File name: \n")
    for file in os.listdir('output'):
        output_text.insert(END, f"{counter} \t {file} \n")
        counter += 1


def display_csv_file(command, output_text):
    """ Display the data from a chosen CSV file with the minimum, maximum and average value"""
    temp_raw_values = []
    light_raw_values = []
    csv_id = int(command.split(" ")[1])  # Get the CSV ID from the users input
    counter = 0
    csv_path = ""
    # Find the path of the chosen CSV file based on the CSV ID
    try:
        for file in os.listdir('output'):
            if counter == csv_id:
                csv_path = "output/" + file
            counter += 1
    except IOError as e:
        print("Error, output couldn't be found!: ")
        print(e)
    if csv_path != "":  # If found
        with open(csv_path, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=",")
            for row in csvreader:
                output_text.insert(END, row)
                output_text.insert(END, "\n")
                if "Temperature sensor" in row[1]:  # row[1] is the sensor name
                    temp_raw_values.append(float(row[2]))  # row[2] is the raw value
                if "Light sensor" in row[1]:  # row[1] is the sensor name
                    light_raw_values.append(float(row[2]))  # row[2] is the raw value

    if temp_raw_values:  # if not empty
        output_text.insert(END, f"Minimum Temperature value: {min(temp_raw_values)} \n")
        output_text.insert(END, f"Maximum Temperature value: {max(temp_raw_values)} \n")
        output_text.insert(END, f"Average Temperature value: {sum(temp_raw_values) / len(temp_raw_values)} \n")
    if light_raw_values:  # if not empty
        output_text.insert(END, f"Minimum Light value: {min(light_raw_values)} \n")
        output_text.insert(END, f"Maximum Light value: {max(light_raw_values)} \n")
        output_text.insert(END, f"Average Light value: {sum(light_raw_values) / len(light_raw_values)} \n")


def wait_for_arduino(root, output_text, command, micro_controller):
    """ Waits for an button input on the Arduino to run or stop the data collection"""
    global is_waiting
    if is_waiting:
        is_waiting = False
        output_text.insert(END, "Stopped waiting for the Arduino \n")
    else:
        is_waiting = True
        output_text.insert(END, "Press the middle button on the Arduino to start / stop the collection of data \n"
                                "Stop waiting by typing 'wait' again \n")
        global is_running
        is_running = True
        start_data_collection(root, output_text, command, micro_controller)


if __name__ == '__main__':
    main()
