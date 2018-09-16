#! /usr/bin/python

######################################
#
#  Speaker impedance measurement tool
#  the python crontroller app
# 
#  GameInstance.com
#  2018
#
######################################

import numpy
import pyaudio
import math
import serial
from time import sleep

 
class ToneGenerator(object):
 
    def __init__(self, samplerate=44100, frames_per_buffer=4410):
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.frames_per_buffer = frames_per_buffer
        self.streamOpen = False
 
    def sinewave(self):
        if self.buffer_offset + self.frames_per_buffer - 1 > self.x_max:
            # We don't need a full buffer or audio so pad the end with 0's
            xs = numpy.arange(self.buffer_offset,
                              self.x_max)
            tmp = self.amplitude * numpy.sin(xs * self.omega)
            out = numpy.append(tmp,
                               numpy.zeros(self.frames_per_buffer - len(tmp)))
        else:
            xs = numpy.arange(self.buffer_offset,
                              self.buffer_offset + self.frames_per_buffer)
            out = self.amplitude * numpy.sin(xs * self.omega)
        self.buffer_offset += self.frames_per_buffer
        return out
 
    def callback(self, in_data, frame_count, time_info, status):
        if self.buffer_offset < self.x_max:
            data = self.sinewave().astype(numpy.float32)
            return (data.tostring(), pyaudio.paContinue)
        else:
            return (None, pyaudio.paComplete)
 
    def is_playing(self):
        if self.stream.is_active():
            return True
        else:
            if self.streamOpen:
                self.stream.stop_stream()
                self.stream.close()
                self.streamOpen = False
            return False
 
    def play(self, frequency, duration, amplitude):
        self.omega = float(frequency) * (math.pi * 2) / self.samplerate
        self.amplitude = amplitude
        self.buffer_offset = 0
        self.streamOpen = True
        self.x_max = math.ceil(self.samplerate * duration) - 1
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.samplerate,
                                  output=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result 
 
###############################################################################
 
generator = ToneGenerator()

amplitude = 0.90            # Amplitude of the waveform

frequency_start = 80        # Frequency to start the sweep from
frequency_end = 180       # Frequency to end the sweep at
num_frequencies = 140       # Number of frequencies in the sweep
step_duration = 3        # Time (seconds) to play at each step

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
print(ser.name)
sleep(3);

for frequency in numpy.logspace(math.log(frequency_start, 10),
			math.log(frequency_end, 10),
			num_frequencies):
	
	generator.play(frequency, step_duration, amplitude)
	ser.write(str("p\n").encode())
	line = ser.readline()
	v = line.split()
	if (len(v) == 2):
		print("%0.2f %0.10f %0.10f" % (frequency, float(v[0]), float(v[1])))
	else:
		print("{0:0.2f} 0 0".format(frequency))
#	print(line)
	while generator.is_playing():
		pass	# Do something useful in here (e.g. recording)

ser.close()
