class MicroController:
    """ A custom class for saving data about the Arduino."""

    def __init__(self, center_button, debounce_start, is_outputting_photo, photo_sensor, temp_sensor, time_start,
                 red_led, blue_led):
        self.center_button = center_button
        self.debounce_start = debounce_start
        self.is_outputting_photo = is_outputting_photo
        self.photo_sensor = photo_sensor
        self.temp_sensor = temp_sensor
        self.time_start = time_start
        self.red_led = red_led
        self.blue_led = blue_led

    def set_outputting_photo(self, is_outputting_photo):
        self.is_outputting_photo = is_outputting_photo

    def set_debounce_start(self, debounce_start):
        self.debounce_start = debounce_start

    def set_time_start(self, time_start):
        self.time_start = time_start
