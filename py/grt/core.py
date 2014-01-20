__author__ = "Calvin Huang"
import time
import threading


class Sensor(object):
    """
    Abstract sensor class.
    Stores data as class attributes, updated when poll() is called.

    Take care to not accidentally override vital class attributes
    with update_state.
    """
    def __init__(self):
        self.listeners = set()  # set of listeners

    def get(self, name):
        """
        Returns the datum associated with some name.
        """
        return self.__dict__[name]

    def add_listener(self, l):
        """
        Add a listener, a method that will be called
        when this sensor's state changes.
        Method has format l(sensor, state_id, datum)
        """
        self.listeners.add(l)

    def remove_listener(self, l):
        """
        Remove a listener.
        """
        self.listeners.remove(l)

    def __setattr__(self, key, value):
        self.update_state(key, value)

    def update_state(self, state_id, datum):
        """
        Updates the state of this sensor.

        Updates state state_id with data datum.
        Also notifies listeners of state change (on change, not add).
        """
        if state_id not in self.__dict__:
            self.__dict__[state_id] = datum
        elif self.__dict__[state_id] != datum:
            self.__dict__[state_id] = datum
            for l in self.listeners:
                l(self, state_id, datum)

    def poll(self):
        """
        Polls the sensor, notifies any listeners if necessary.

        Should be overridden by all sensors.
        """
        pass


class SensorPoller(object):
    """
    Class that periodically polls sensors.
    """

    def __init__(self, sensors):
        """
        Sets the polltime (in seconds) and the initial set of sensors.
        """
        self.sensors = sensors

    def add_sensor(self, sensor):
        """
        Adds a sensor to poll.
        """
        self.sensors.append(sensor)

    def remove_sensor(self, sensor):
        """
        Removes a sensor.
        """
        self.sensors.remove(sensor)

    def poll(self):
        """
        Polls all sensors in this sensorpoller.
        """
        for sensor in self.sensors:
            sensor.poll()


class Constants(Sensor):
    """
    Class for reading, and keeping track of, constants in a file.

    File is read line by line, in [key],[number] format.
    Lines starting with '/' are treated as add'l constants files,
    and are read recursively.
    Blank lines, and lines starting with '#' are ignored.

    Behaves more or less like a sensor.
    """

    def __init__(self, file_loc='/c/constants.txt'):
        """
        Creates Constants with an initial file.
        """
        super().__init__()
        self.file_loc = file_loc

    def poll(self):
        """
        Reloads file data.
        """
        self.load_file(self.file_loc)

    def load_file(self, file_loc):
        """
        Loads file data from a file.
        If other files are listed inside this file,
        recursively loads them.

        (Beware of "include loops" that will cause a crash)
        """
        f = open(file_loc)
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('/'):  # is a file, load it!
                self.load_file(line)
                continue
            # continue with getting data
            key, _, value = line.partition(',')
            try:
                self.update_state(key, float(value))
            except ValueError:
                print("Malformed constants file " + file_loc +
                      " with key " + key + " and value " + value)
        f.close()


class GRTMacro(object):
    """
    Abstract macro class.
    """
    running = False
    timed_out = False
    started = False
    start_time = None

    def __init__(self, timeout=float('inf'), poll_time=0.05):
        """
        Creates a macro with timeout (infinite by default)
        and poll interval, in seconds (0.05s by default)
        """
        self.timeout = timeout
        self.poll_time = poll_time

    def run(self):
        """
        Start macro in new thread.
        See execute() for more details on macro execution.
        """
        self.thread = threading.Thread(target=self.execute)
        self.thread.run()

    def execute(self):
        """
        Starts macro in current thread.
        First calls initialize(), then calls perform()
        periodically until timeout or completion.
        After completion, calls die().
        """
        if not self.started:
            self.started = True
            self.start_time = time.time()

            self.initialize()
            self.running = True
            while not self.running:
                self.perform()
                time.sleep(self.poll_time)

                if (time.time() - self.start_time) > self.timeout:
                    self.timed_out = True
                    break
            self.running = False
            self.die()

    def reset(self):
        """
        Resets a macro, allowing it to be started again
        """
        self.running = self.started = self.timed_out = False

    def initialize(self):
        """
        Run once, at the beginning of macro execution.
        """
        pass

    def perform(self):
        """
        Macro execution body, run periodically.
        """
        pass

    def die(self):
        """
        Cleanup after macro execution.
        """
        pass

    def kill(self):
        """
        Stop macro execution.
        """
        if self.running:
            print("Killing macro: " + self.name)
            self.running = False
