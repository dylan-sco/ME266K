# simple geophone test

# imports
import time
import board
import busio
import csv
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# source: https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/blob/main/examples/ads1x15_simpletest.py
# create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# create the ADS object
ads = ADS.ADS1115(i2c)

# Create a single-ended channel on Pin 0
#   Max counts for ADS1015 = 2047
#                  ADS1115 = 32767
chan = AnalogIn(ads, ADS.P0)

# Gain Values
# The ADS1015 and ADS1115 both have the same gain options.
#
#       GAIN    RANGE (V)
#       ----    ---------
#        2/3    +/- 6.144
#          1    +/- 4.096
#          2    +/- 2.048
#          4    +/- 1.024
#          8    +/- 0.512
#         16    +/- 0.256
#
# gains = (2 / 3, 1, 2, 4, 8, 16)

# grab curr time
def current_milli_time():
    return round(time.time() * 1000)

# Constants
geo_gain = 8
start = current_milli_time()
filename = 'insert_filename_here.csv'

# create lists for time and voltage
time_list = []
voltage_list = []


try:
	while True:
		ads.gain = geo_gain
		# grab time and voltage readings, add to lists
		t = current_milli_time() - start
		v = round(chan.voltage, 4)
		# display time and voltage readings on terminal output
		print("time(ms): " + str(t) + "||" + "voltage:" + str(v))
		time_list.append(t)
		voltage_list.append(v)
		time.sleep(0.1)
except:
	print("breaking the while loop & saving data into csv")
	# save into csv file
	with open('sand_test_3s_on_vs_off.csv', 'w') as f:
		w = csv.writer(f)
		w.writerows(zip(time_list, voltage_list))
