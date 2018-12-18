import time
import inspect
import re

import pyvisa


class TSL_210H(object):
	methods = []

	def __init__(self, device):

		self.max_wavelength = 1580
		self.min_wavelength = 1510

		self.device = device
		self.active = False
		self.run_turn_output_on()
		self.locked = True

		self.sweep_start = None
		self.sweep_end = None
		self.sweep_step = None
		self.wavelength = None

	def who_am_i(self):
		if self.check_connected():
			return "Santec TSL-210H at " + self.device.resource_info[0].alias
		else:
			return "Santec TSL-210H DISCONNECTED"

	def what_can_i(self):
		if len(TSL_210H.methods) == 0:
			for method in inspect.getmembers(self, inspect.ismethod):
				if re.match('^run_.+', method[0]):
					TSL_210H.methods.append(method)
		return TSL_210H.methods

	def check_connected(self):
		if not self.device:
			return False
		try:
			return self.device.session is not None
		except pyvisa.errors.InvalidSession:
			self.device = None
			return False

	def run_change_state(self):
		self.active = ~self.active

	def run_get_max_wavelength(self):
		return self.max_wavelength

	def run_get_min_wavelength(self):
		return self.min_wavelength

	def run_set_wavelength(self, wavelength):
		if wavelength > self.max_wavelength or wavelength < self.min_wavelength:
			print 'Wavelength out of range'
		else:
			wavelength = "{0:.3f}".format(float(wavelength))
			self.device.write('WA' + wavelength)
			time.sleep(0.5)
			self.device.write('WA')
			self.wavelength = wavelength
			check = "0.000"
			while check != wavelength:
				while self.device.bytes_in_buffer == 0:
					time.sleep(0.1)
				check = self.device.read()
		return

	def run_sweep_setup(self, start, end, step):
		if start < self.min_wavelength or start > self.max_wavelength or \
				end < self.min_wavelength or start > self.max_wavelength:
			print 'Wavelength out of range'
		else:
			self.sweep_start = start
			self.sweep_end = end
			self.sweep_step = step

	def run_sweep_step(self):
		if self.sweep_end > self.wavelength >= self.sweep_start:
			self.wavelength = float(self.wavelength) + float(self.sweep_step)
			self.run_set_wavelength(self.wavelength)

	def run_start_sweep(self):
		if self.sweep_start is None or self.sweep_end is None or self.sweep_step is None:
			print 'Sweep not configured'
		else:
			self.run_set_wavelength(self.sweep_start)

	def run_pause_sweep(self):
		"""
		Pause sweep
		"""
		self.device.write('WA')

	def run_stop_sweep(self):
		"""
		Stop the sweep
		"""
		self.run_turn_output_off()

	def run_check_status(self):
		"""
		Check the status of the instrument

		:returns: Booleans
		"""
		#
		# try:
		# 	self.device.write('SU')
		# 	status = int(self.device.read())
		# 	if status > 0:
		# 		return True
		# 	else:
		# 		return False
		# except Exception:
		# 	time.sleep(0.2)
		# 	return self.checkStatus()
		self.device.write('SU')
		for x in range(0, 50, 1):
			if self.device.bytes_in_buffer < 1:
				time.sleep(0.2)
				continue
			return int(self.device.read()) > 0
		return False

	def run_turn_output_on(self):
		"""
		Turns output of laser source ON.
		"""
		self.device.write('LO')  # turn on diode

	def run_turn_output_off(self):
		"""
		Turns output of laser source OFF. Output occasionally doesn't turn off unless turned ON beforehand
		"""
		self.device.write('LF')  # turn off diode

	def run_get_wavelength(self):
		"""
		Query the current wavelength

		:returns: Float
		"""
		# self.gpib.write('WA')
		# return float(self.device.read())
		return float(self.device.query('WA'))

	def run_set_power(self, power):
		"""
		Set power in dbm

		:param power: power specified to set
		:type power: Float
		"""
		self.device.write('OP' + str(power))

	def run_get_power(self):
		"""
		Gets output power in dbm

		:returns: Float
		"""
		# self.gpib.write('OP')
		# return float(self.gpib.read())
		return float(self.device.query('OP'))

	def run_set_current(self, current):
		"""
		Set the current. Note: current is mA

		:param current: specified current to set
		:type current: Integer
		"""
		self.device.write('CU' + str(current))

	def run_get_current(self):
		"""
		Queries the current, Note: current is mA

		:returns: Float
		"""
		# self.gpib.write('CU')
		# return float(self.gpib.read())
		return float(self.device.query('CU'))

	def run_set_temperature(self, temperature):
		"""
		Set the temperature. Note: temperature is C

		:param temperature: specified temperature to set
		:type temperature: Integer
		"""
		self.device.write('TL' + str(temperature))

	def run_get_temperature(self):
		"""
		Queries the temperature, Note: temperature is C

		:returns: Float
		"""
		# self.gpib.write('TL')
		# return float(self.gpib.read())
		return float(self.device.query('TL'))

	def run_set_ACC(self):
		"""
		Sets the ACC
		"""
		self.device.write('AO')

	def run_set_APC(self):
		"""
		Sets the APC
		"""
		self.device.write('AF')

	def run_get_status(self):
		"""
		Queries the status of the...

		:returns: String
		"""
		# self.gpib.write('SU')
		# return self.gpib.read()
		return self.device.query('SU')

	def run_set_power_mw(self, powermw):
		"""
		Sets the powerMW

		:param powermw: specified powerMW to set
		:type powermw: Integer
		"""
		self.device.write('LP' + str(powermw))

	def run_get_power_mw(self):
		"""
		Queries the status of the powerMW

		:returns: Float
		"""
		# self.gpib.write('LP')
		# return float(self.gpib.read())
		return float(self.device.query('LP'))

	def run_coherence_on(self):
		"""
		Turns coherence ON
		"""
		self.device.write('CO')

	def run_coherence_off(self):
		"""
		Turns coherence OFF
		"""
		self.device.write('CF')

	def run_set_coherence(self, coherence):
		"""
		Sets the coherence

		:param coherence: Specified coherence
		:type coherence: Integer
		"""
		self.device.write('CV' + str(coherence))

	def run_get_coherence(self):
		"""
		Queries the coherence value

		:returns: Float
		"""
		# self.gpib.write('CV')
		# return float(self.gpib.read())
		return float(self.device.query('CV'))