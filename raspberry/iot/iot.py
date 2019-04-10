#!/usr/bin/env python3

import sys
import os
import socket
from watermator import *
from constants import *

if len(sys.argv) < 2:
	print("One arguement expected, but received none.")
elif len(sys.argv) > 2:
	print("Too many arguments.")
else:
	if str(sys.argv[1]) == "start":
		#Start IoT Can if not running already
		try:
			os.unlink(server_address)
		except OSError:
			if os.path.exists(server_address):
				raise

		#Create logs directory if not available
		if not os.path.isdir('logs'):
			os.makedirs('logs')

		#Remove old log if available
		if os.path.isfile('logs/iot_can.log'):
			os.remove('logs/iot_can.log')

		#Start IoT Can
		os.system('python3 watermator.py &')
		print("Watermator Started.")
		print("Stop service by giving argument stop.")

	if str(sys.argv[1]) == "stop":
		#Stop IoT Can
		unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		try:
			unix_socket.connect(server_address)
		except socket.error:
			print("Failed to connect to socket")
			sys.exit(1)

		try:
			#send message to IoT_Can
			message = 'stop'
			unix_socket.sendall(message.encode())
		finally:
			unix_socket.close()
			print("Watermator Stopped.")