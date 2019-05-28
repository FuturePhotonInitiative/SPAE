# Class for Agilent E3643A DC Power Supply

import inspect
import re
import pyvisa
import pyvisa.constants


class AgilentDSO7000A(object):
	"""
	This class models the Agilent DC power supply.
	"""

	methods = []

	def __init__(self, device):
		"""
		Constructor method.

		:param device: device from PyVisa open_resource object
		:type: PyVisa open_resource object
		"""
		self.device = device

	def __enter__(self):
		"""
		Enter method for ability to use "with open" statements
		:return: Driver Object
		"""
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Exit to close object
		:param exc_type:
		:param exc_val:
		:param exc_tb:
		:return:
		"""
		self.device.close()
		pass

	def who_am_i(self):
		if self.check_connected():
			return "Agilent DSO7000A at " + self.device.resource_info[0].alias
		else:
			return "Agilent DSO7000A DISCONNECTED"

	def what_can_i(self):
		if len(AgilentDSO7000A.methods) is 0:
			for method in inspect.getmembers(self, inspect.ismethod):
				if re.match('^run_.+', method[0]):
					AgilentDSO7000A.methods.append(method)
		return AgilentDSO7000A.methods

	def check_connected(self):
		if not self.device:
			return False
		try:
			return self.device.session is not None
		except pyvisa.errors.InvalidSession:
			self.device = None
			return False

	def run_identify(self):
		"""
		Identifies itself using IDN query
		:return:
		"""
		if self.check_connected():
			identity = self.device.query("*IDN?")
			return identity
		else:
			raise Exception('Serial communication port is not open.')

	def run_measure_set_source(self, channel_num):
		"""
		Set source to measure
		:param: channel_num, channel number to measure
		:return: None
		"""
		self.device.write(":MEASURE:SOURCE CHANNEL"+str(channel_num))

	def run_measure_vpp(self, channel_num=None):
		"""
		Measure VPP from preset source
		:param: channel_num, channel number to measure
		:return: VPP from Source
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:VPP? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:VPP?", delay=8.25)

	def run_measure_vaverage(self, channel_num=None):
		"""
		Measure average voltage
		:param: channel_num, channel number to measure
		:return: Voltage average
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:VAV? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:VAV?", delay=8.25)

	def run_measure_clear(self):
		"""
		Clears commands from all measurements and markers
		:return:
		"""
		self.device.write(":MEAS:CLE")

	def run_measure_duty_cycle(self, channel_num):
		"""
		Measures duty cycle of source provided
		:param: channel_num: channel number to measure
		:return: Duty Cycle
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:DUTY? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:DUTY?", delay=8.25)

	def run_measure_fall_time(self, channel_num=None):
		"""
		Measure fall time of source provided
		:param channel_num, channel number to measure
		:return: Fall Time (seconds)
		"""
		if channel_num is not None:
			return self.device(":MEAS:FALL? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device(":MEAS:FALL?", delay=8.25)

	def run_measure_frequency(self, channel_num=None):
		"""
		Measure frequency of source provided
		:param channel_num, channel number to measure
		:return: Frequency (Hertz)
		"""
		if channel_num is not None:
			return self.device(":MEAS:FREQ? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device(":MEAS:FREQ?", delay=8.25)

	def run_measure_nwidth(self, channel_num=None):
		"""
		Measures negative pulse width of source provided
		:param channel_num, channel number to measure
		:return: Pulse Width (seconds)
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:NWID? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:NWID?", delay=8.25)

	def run_measure_overshoot(self, channel_num=None):
		"""
		Measure overshoot of source provided
		:param channel_num, channel number to measure
		:return: Overshoot percentage
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:OVER? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:OVER?", delay=8.25)

	def run_measure_period(self, channel_num=None):
		"""
		Measure period of source provided
		:param channel_num, channel number to measure
		:return: Period (seconds)
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:PER? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:PER?", delay=8.25)

	def run_measure_phase(self, channel_num=None):
		"""
		Measure phase of source provided
		:param channel_num, channel number to measure
		:return: Phase (degrees)
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:PHAS? CHAN" + str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:PHAS?", delay=8.25)

	def run_measure_preshoot(self, channel_num=None):
		"""
		Measure preshoot of source provided
		:param channel_num, channel number to measure
		:return: Preshoot (percentage)
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:PRES? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:PRES?", delay=8.25)

	def run_measure_pulse_width(self, channel_num=None):
		"""
		Measure pulse width of source provided
		:param channel_num, channel number to measure
		:return: Pulse width (seconds)
		"""
		if channel_num is not None:
			return self.device.query(":MEAS:PWID? CHAN"+str(channel_num), delay=8.25)
		else:
			return self.device.query(":MEAS:PWID?", delay=8.25)

	def run_measure_results(self, channel_num=None):
		"""
		Measure all results
		:param channel_num, channel number to measure
		:return: Results (list of variables)
		"""
		# Turn on statistics to also provide labels for values received
		self.device.write(":MEAS:STAT 1")
		return_results = {}
		if channel_num is not None:
			results = self.device.query(":MEAS:RES? CHAN"+str(channel_num), delay=8.25)
		else:
			results = self.device.query(":MEAS:RES?", delay=8.25)
		first_header = re.compile(r'(?P<header>[a-zA-Z\-]+?)\(.*\),')
		header = re.compile(r',+?(?P<header>[a-zA-Z\-]+?)\(.*\),')
		value = re.compile(r'.*?,(?P<value>.*?),')
		header_match = first_header.match(results)
		while True:
			if header_match is not None:
				head = header_match.group('header')
				return_results[head] = []
				results = results[results.index(head) + len(head):]
			header_match = header.match(results)
			while header_match is None:
				value_match = value.match(results)
				if value_match is not None:
					val = value_match.group('value')
					return_results[head].append(val)
					results = results[results.index(val) + len(val):]
				header_match = header.match(results)
				if header_match is None and value_match is None:
					return return_results

	def run_start_acquisition(self):
		"""
		Start acquiring data
		:return: None
		"""
		self.device.write(":RUN")

	def run_single_acquisition(self):
		"""
		Run a single acquisition
		:return: None
		"""
		self.device.write(":SINGLE")

	def run_stop_acquisition(self):
		"""
		Stop running acquisition
		:return: None
		"""
		self.device.write(":STOP")

	def run_set_channel_coupling(self, channel_num, acdc):
		"""
		Set AC/DC coupling for channels
		:param: channel_num, channel number to set coupling
		:param: acdc, choice of ac or dc coupling to channel selected
		:return: None
		"""
		self.device.write(":CHAN"+str(channel_num)+":COUP "+str(acdc))

	def run_set_channel_label(self, channel_num, label):
		"""
		Set channel label
		:param: channel_num, channel number to set label
		:param: label, label to set to channel_num
		:return: None
		"""
		self.device.write("CHAN"+str(channel_num)+":LAB "+str(label))

	def run_set_channel_impedance(self, channel_num, imp):
		"""
		Set the channel impedance
		:param: channel_num, number of channel to change
		:param: imp, impedance choice of either ONEMEG or FIFTY
		:return: None
		"""
		self.device.write(":CHAN"+str(channel_num)+":IMP "+imp)

	def run_set_channel_scale(self, channel_num, scale):
		"""
		Set the channel scaling
		:param: channel_num, number of channel to change
		:param: scale, scaling factor 5V or 4mV
		:return: None
		"""
		self.device.write(":CHAN"+str(channel_num)+":SCALE"+str(scale))

	def run_save_capture(self, name="Image"):
		"""
		Saves the current capture from the oscilloscope
		:return: Filepath to find the file
		"""
		# Sets file name to name
		self.device.write("SAVE:FIL "+str(name))
		# Saves image
		self.device.write(":SAVE:IMAG")
		# Return the saved file path and file name
		return self.device.query(":SAVE:PWD?")+self.device.query("SAVE:FIL?")

	def run_time_range(self, time_val):
		"""
		Update the timebase to specified value
		:param time_val: time to set, in ns
		:return: None
		"""
		self.device.write(":TIM:RANG "+str(time_val))

	def run_time_scale(self, time_val):
		"""
		Update the time scale to specified value
		:param time_val: time to set, in ps
		:return: None
		"""
		self.device.write(":TIM:SCAL "+str(time_val))

	def run_time_window_scale(self, time_val):
		"""
		Update the window time scale seconds/division
		:param time_val: time in seconds
		:return: None
		"""
		self.device.write(":TIM:WIND:SCAL "+str(time_val))

	def run_trigger_mode(self, mode):
		"""
		Set the trigger mode to any of the following:
		EDGE, GLITch, PATTern, CAN, DURation, I2S, IIC, EBURst, LIN, M1553, SEQuence, SPI, TV,
		UART, USB, FLEXray
		:param mode: mode to change the trigger to. See above for options
		:return: None
		"""
		self.device.write("TRIG:MODE "+mode)