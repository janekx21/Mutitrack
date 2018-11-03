"""PyAudio Example: Play a wave file (callback version)."""
import pyaudio
import wave
import time
import sys,os
import threading




#Constanten
CHANNELS = 2
FORMAT = pyaudio.paInt16
RATE = 48000
DIR = "."

helpMSG = "usage: python " + sys.argv[0] + " indexes [options]\n"\
"indexes:\n"\
"  by index\t<index>[,<index>,<index>]\n"\
"  named index\t<name>=<index>[,<name>=<index>,<name>=<index>]\n"\
"options:\n"\
"  -d path\tpath of a directory\n"\
"  -r rate\tspecify the sample rate\n"\
"  -w width\tspecify the sample width\n"\
"\t\t1=8bit, 2=16bit, 3=24bit, 4=32bit\n"\
"\n"\
"\n"\
"by index will create new files called recording<index>.wav\n"\
"named index will create a file called <name>.wav for each index\n"\

timeToClose = False


def printHelp():
	print(helpMSG)

p = pyaudio.PyAudio()
if len(sys.argv)<=1:
	printHelp()
	print("-"*16)
	print("possible indexes:")
	for x in range(p.get_device_count()):
		info = p.get_device_info_by_index(x)
		if info["maxInputChannels"] > 0:
			print(f"{x}\tname: {info['name']}")
	sys.exit(0)
indexes = []
names = {}
try:
	indexes = [int(x) for x in sys.argv[1].split(",")]
except ValueError:
	strings = sys.argv[1].split(",")
	for string in strings:
		split = string.split("=")
		if len(split) != 2:
			printHelp()
			sys.exit(-1)
		try:
			index = int(split[1])
			indexes.append(index)
			names[index] = split[0]
		except ValueError:
			printHelp()
			sys.exit(-1)
if len(sys.argv) > 2:
	other = sys.argv[2:]
	for i,arg in enumerate(other):
		if arg == "-d":
			if len(other) > i+1:
				DIR = other[i+1]
				if not os.path.isdir(DIR):
					print(f"{DIR} is not a directory")
					sys.exit(-1)
			else:
				printHelp()
				sys.exit(-1)

		if arg == "-r":
			if len(other) > i+1:
				try:
					RATE = int(other[i+1])
				except ValueError:
					print(f"{other[i+1]} not a number")
					sys.exit(-1)
			else:
				printHelp()
				sys.exit(-1)

		if arg == "-w":
			if len(other) > i+1:
				try:
					FORMAT = p.get_format_from_width(int(other[i+1]))
				except ValueError:
					print(f"{other[i+1]} not a valid number")
					sys.exit(-1)
			else:
				printHelp()
				sys.exit(-1)




def Track(index):
	global timeToClose
	# instantiate PyAudio (1)
	
	if names[index] != None:
		waveFile = wave.open(f"{DIR}/{names[index]}.wav", 'wb')
	else:
		waveFile = wave.open(f"{DIR}/recording{index}.wav", 'wb')


	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(p.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)

	# define callback (2)
	def callback(in_data, frame_count, time_info, status):
		waveFile.writeframes(in_data)
		return (None, pyaudio.paContinue)

	# open stream using callback (3)
	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					stream_callback=callback,
					input_device_index=index)

	# start the stream (4)
	stream.start_stream()

	while not timeToClose:
		time.sleep(.5)

	stream.stop_stream()
	stream.close()
	waveFile.close()

for index in indexes:
	t = threading.Thread(target=Track,args = (index,))
	t.start()
time.sleep(.5)
while True:
	if timeToClose:break
	c = input()
	if c == "exit":
		break
time.sleep(.5)
for index in indexes:
	timeToClose = True
p.terminate()