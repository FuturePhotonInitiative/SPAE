import re
import pyvisa

from src.Instruments.PyVisaDriver import PyVisaDriver


class Xilinx_VCU108(PyVisaDriver):
    """
    This class models a Xilinx VCU108 FPGA Evaluation Kit
    """

    def __init__(self, device):
        PyVisaDriver.__init__(self)
        self.device = device
        self.name += "VCU108"

        self._locked = False

    def read_data(self):
        """
        Read data from self.device until nothing is left in the buffer
        :return: data, all the data read from the buffer
        """
        data = []
        line = self.device.read()
        print(line)
        data.append(line)
        while self.device.bytes_in_buffer > 0:
            line = self.device.read()
            print(line)
            data.append(line)
        return data

    def eyescan(self, range_value=0, scale_factor=0, horizontal=127, vertical=512, drp=0, step=2):
        """
        Eyescan test
        :param range_value: range for eyescan
        :param scale_factor: scaling factor for eyescan
        :param horizontal: horizontal boundary
        :param vertical: vertical boundary
        :param drp: choice of drp
        :param step: step size of voltages
        :return: data, all data from command, will need to be parsed later
        """
        data = []
        line = ""
        if not self.check_connected():
            return False
        else:
            self.device.write("petb eyescan "+str(range_value)+" "+str(scale_factor)+" "+str(horizontal)+" "+str(vertical)+" "+str(drp)+" "+str(step))
            while "END" not in line:
                try:
                    line = self.device.read()
                    print(line)
                    data.append(line)
                except pyvisa.VisaIOError:
                    continue
            return data

    def raw_command(self, command):
        if not self.check_connected():
            return False
        else:
            self.device.write(command)
            return self.read_data()

    def petb_read(self, pin):
        """
        petb gpio read [port=0] [pin], port is always 0
        :param pin: string, pin value, must be in valid_pins
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = ["modsel", "reset", "modprs", "int", "lpmode", "all"]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                return "Invalid pin sent."
            self.device.write("petb gpio read 0 "+str(pin))
            return self.read_data()

    def petb_set(self, pin):
        """
        petb gpio write [port=0] [pin], port is always 0
        :param pin: string, pin value, must be in valid_pins
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = ["modsel", "reset", "modprs", "int", "lpmode", "all"]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                return "Invalid pin sent."
            self.device.write("petb gpio set 0 "+str(pin))
            return self.read_data()

    def petb_clear(self, pin):
        """
        petb gpio write [port=0] [pin], port is always 0
        :param pin: string, pin value, must be in valid_pins
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = ["modsel", "reset", "modprs", "int", "lpmode", "all"]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                return "Invalid pin sent."
            self.device.write("petb gpio clear 0 "+str(pin))
        return self.read_data()

    def petb_toggle(self, pin):
        """
        petb gpio write [port=0] [pin], port is always 0
        :param pin: string, pin value, must be in valid_pins
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = ["modsel", "reset", "modprs", "int", "lpmode", "all"]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                return "Invalid pin sent."
            self.device.write("petb gpio toggle 0 "+str(pin))
            return self.read_data()

    def pek_read(self, pin=0, port=0):
        """
        pek gpio read [port=0] [pin=0]
        :param pin: string, pin value, must be in valid_pins
        :param port: int, port number, must be in valid_ports
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = [0, 1, 2, 3, 4, 5, 6, 7]
        valid_ports = [0, 1, 2, 3]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                print("Invalid pin sent.")
                return False
            if port not in valid_ports:
                print("Invalid port sent.")
                return False
            self.device.write("pek gpio read " + str(port) + " " + str(pin))
            return self.read_data()

    def pek_set(self, pin=0, port=0):
        """
        pek gpio set [port=0] [pin=0]
        :param pin: string, pin value, must be in valid_pins
        :param port: int, port number, must be in valid_ports
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = [0, 1, 2, 3, 4, 5, 6, 7]
        valid_ports = [0, 1, 2, 3]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                print("Invalid pin sent.")
                return False
            if port not in valid_ports:
                print("Invalid port sent.")
                return False
            self.device.write("pek gpio set " + str(port) + " " + str(pin))
            return self.read_data()

    def pek_clear(self, pin=0, port=0):
        """
        pek gpio clear [port=0] [pin=0]
        :param pin: string, pin value, must be in valid_pins
        :param port: int, port number, must be in valid_ports
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = [0, 1, 2, 3, 4, 5, 6, 7]
        valid_ports = [0, 1, 2, 3]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                print("Invalid pin sent.")
                return False
            if port not in valid_ports:
                print("Invalid port sent.")
                return False
            self.device.write("pek gpio clear " + str(port) + " " + str(pin))
            return self.read_data()

    def pek_toggle(self, pin=0, port=0):
        """
        pek gpio toggle [port=0] [pin=0]
        :param pin: string, pin value, must be in valid_pins
        :param port: int, port number, must be in valid_ports
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = [0, 1, 2, 3, 4, 5, 6, 7]
        valid_ports = [0, 1, 2, 3]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                print("Invalid pin sent.")
                return False
            if port not in valid_ports:
                print("Invalid port sent.")
                return False
            self.device.write("pek gpio toggle " + str(port) + " " + str(pin))
            return self.read_data()

    def pek_write(self, pin=0, port=0, value=0):
        """
        pek gpio write [port=0] [pin=0]
        :param pin: string, pin value, must be in valid_pins
        :param port: int, port number, must be in valid_ports
        :param value: int, value, must be 0 or 1
        :return: data, all data from command, will need to be parsed later
        """
        valid_pins = [0, 1, 2, 3, 4, 5, 6, 7]
        valid_ports = [0, 1, 2, 3]
        valid_values = [0, 1]
        if not self.check_connected():
            return False
        else:
            if pin not in valid_pins:
                print("Invalid pin sent.")
                return False
            if port not in valid_ports:
                print("Invalid port sent.")
                return False
            if value not in valid_values:
                print("Invalid port sent.")
                return False
            self.device.write("pek gpio write " + str(port) + " " + str(pin) + " " + str(value))
            return self.read_data()

    def pek_list(self):
        """
        pek gpio list
        :return: data, all data from command, will need to be parsed later
        """
        if not self.check_connected():
            return False
        else:
            self.device.write("pek gpio list")
            return self.read_data()

    def adc_read(self, channel="00"):
        """
        adc read [channel]
        :param channel: string, must be in valid_channels
        :return: data, all data from command, will need to be parsed later
        """
        valid_channels = ["00", "0e", "10", "13", "16", "17"]

        if not self.check_connected():
            return False
        else:
            if channel not in valid_channels:
                print("Channel not valid.")
                return False
            self.device.write("adc read " + str(channel))
            return self.read_data()

    def dac_write(self, value=""):
        """
        dac write []
        :param value: string, data to be written to the DAC
        :return: data, all data from command, will need to be parsed later
        """
        if not self.check_connected():
            return False
        else:
            self.device.write("dac write " + str(value))
            return self.read_data()

    def spixfer(self, value):
        """
        spixfer [string]
        :param value: string, data to be written to SPI
        :return: data, all data from command, will need to be parsed later
        """
        if not self.check_connected():
            return False
        else:
            self.device.write("spixfer " + str(value))
            return self.read_data()

    def spilib(self, value):
        """
        spilib [string]
        :param value: string, data to be written to SPI
        :return: data, all data from command, will need to be parsed later
        """
        if not self.check_connected():
            return False
        else:
            self.device.write("spilib "+str(value))
            return self.read_data()

    def i2cwrite(self, address, value):
        """
        i2cwrite [address] [byte value]
        :param address: string, must be between 0x00 and 0xFF
        :param value: string, byte value to write to address
        :return: data, all data from command, will need to be parsed later
        """
        valid_address = re.compile(r'(?P<name>0x[0-9ABCDEF][0-9ABCDEF])')
        match = valid_address.match(address)
        if not self.check_connected():
            return False
        else:
            if match is None:
                print("Enter a valid address")
                return False
            self.device.write("i2cwrite " + str(address) + " " + str(value))
            return self.read_data()

    def i2cread(self, address, value=""):
        """
        i2cwrite [address] [byte value]
        :param address: string, must be between 0x00 and 0xFF
        :param value: string, optional, number of bytes to read
        :return: data, all data from command, will need to be parsed later
        """
        valid_address = re.compile(r'(?P<name>0x[0-9ABCDEF][0-9ABCDEF])')
        match = valid_address.match(address)
        if not self.check_connected():
            return False
        else:
            if match is None:
                print("Enter a valid address")
                return False
            self.device.write("i2cread " + str(address) + " " + str(value))
            return self.read_data()
