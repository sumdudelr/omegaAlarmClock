#-------------------------------------------------------------------------------
#				Binary Alarm Clock
#
#	This program creates an alarm clock that displays the time as a binary
#	output using the GPIO on the Onion Omega 2. The specific times when you
#	want the active buzzer alarm to go off should be stored in the file
#	'alarmTime.txt' in the format 'HH:MM' with each time on its own line.
#	This file is required to be in the same directory as the program. The
#	'registerClass.py' file from Onion's projects is required to be in the
#	directory as well.
#
#	--Logan Reich - 6/23/17
#-------------------------------------------------------------------------------

from registerClass import shiftRegister
import time
import sys
import onionGpio
import signal
import copy

# Data is GPIO 1, serial clock is GPIO 2, latch is GPIO 3
shiftRegister = shiftRegister(1, 2, 3)

# Active buzzer is GPIO 0
buzzer = onionGpio.OnionGpio(0)
buzzer.setOutputDirection(0)

# Signal interupt handler to break loop
def signal_handler(signal, frame):
	global interrupted
	interrupted = True
signal.signal(signal.SIGINT, signal_handler)

# Set the alarm time from file alarmTime.txt
inFile = open('alarmTime.txt')
alarmList = []
for line in inFile:
	# Creates a list containing time structs
	# Strings in file should be of format 'HH:MM'
	alarmString = line.rstrip()
	alarmList.append(alarmString)
# The list should be sorted so that it is easier to evaluate
alarmList.sort(key=None, reverse=True)

interrupted = False
checkList = []

# Infinite loop to run main program
while True:
	currentTime = time.localtime()
	currentMinutes = currentTime.tm_min
	currentHours = currentTime.tm_hour

	# Format the current time as a byte string
	binaryMinutes = format(currentMinutes, '08b')
	binaryHours = format(currentHours, '08b')

	# Check if there are times left in the alarm list
	if not checkList:
		# The alarm list needs to be copied
		checkList = copy.deepcopy(alarmList)
	# Check if the alarm should go off
	tmp = checkList.pop()
	if tmp == time.strftime('%H:%M', currentTime):
		# Activate the buzzer
		buzzer.setValue(1)
		time.sleep(2)
	# elif tmp < time.strftime('%H:%M', currentTime):
		# Old times will be removed from the queue
		# checkList.pop()
	else:
		# Replace the list item
		checkList.append(tmp)

	# Output the updated values
	shiftRegister.outputBits(binaryMinutes)
	time.sleep(2)
	shiftRegister.outputBits(binaryHours)
	time.sleep(2)
	buzzer.setValue(0)

	# Interrupt handler
	if interrupted:
		shiftRegister.clear()
		buzzer.setValue(0)
		break
