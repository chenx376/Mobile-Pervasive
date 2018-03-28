import os
import struct
import math
import matplotlib.pyplot as plt

base_dir = '10feet_9step_1'
file_prefix = 'data_'
file_size = 5 * 1024
separator1 = '\xff\xff'
separator2 = '\xfe\xfe'
buffer_size = 256
time_size = 6
TIME_OVERFLOW = 1099511627776
TIME_RES = 0.000015650040064103
all_vib = []
all_time = []
sensor_cnt = 2
for sensor_id in range(sensor_cnt):
    sensor_id = str(sensor_id)
    file_read = 0
    pre_buffer = ''
    vib = []
    times = []
    pre_time = 0
    pre_vib = []
    while True:
        file_name = file_prefix + str(file_read)
        file_path = os.path.join(base_dir, sensor_id, file_name)
        if not os.path.exists(file_path) or os.path.getsize(file_path) != file_size:
            break
        with open(file_path, 'rb') as f:
            content = pre_buffer + f.read()
            buffers = content.split(separator1)
            if len(buffers[0]) == 0:
                del buffers[0]
            buffer_count = len(buffers)
            if len(buffers[buffer_count - 1]) != time_size and len(buffers[buffer_count - 1]) != buffer_size:
                pre_buffer = buffers[buffer_count - 1]
                del buffers[buffer_count - 1]
            else:
                if len(buffers[buffer_count - 1]) == time_size:
                    time_check = buffers[buffer_count - 1]
                    if time_check[0:2] != separator2:
                        pre_buffer = buffers[buffer_count - 1]
                        del buffers[buffer_count - 1]
                    else:
                        pre_buffer = ''
                else:
                    pre_buffer = ''
            for buf in buffers:
                if len(buf) == buffer_size:
                    for i in range(0, buffer_size - 1, 2):
                        value = ord(buf[i]) + ord(buf[i + 1]) * 256
                        pre_vib.append(value)
                        # print 'sensor ' + sensor_id + ' add vib: ' + str(len(vib))
                elif len(buf) == time_size:
                    buf = buf[2:]
                    time = bytearray()
                    for i in buf:
                        time.append(i)
                    for i in range(4):
                        time.append('\x00')
                    time = struct.unpack('L', time)[0]
                    if time < 0:
                        print 'time < 0: ' + str(time)
                        time = math.fmod(float(time), TIME_OVERFLOW) * TIME_RES
                    if pre_time > 0:
                        time_diff = time - pre_time
                        size_diff = len(pre_vib)
                        time_interval = time_diff / size_diff
                        for i, v in enumerate(pre_vib):
                            times.append(time_interval * i + pre_time)
                            vib.append(v)
                    pre_vib = []
                    pre_time = time
                else:
                    print 'error: ' + str(len(buf))
        file_read += 1
    all_vib.append(vib)
    all_time.append(times)

import numpy as np
from scipy.stats import norm

windowSize = (int)(2000)
WIN1=windowSize/2
WIN2=windowSize
offSet = windowSize/2
eventSize = WIN1+WIN2
sigmaSize = 10
states = 0
stepPeak = 1
windowDataEnergyArray = np.array([])
stepStartIdxArray = np.array([])
stepStopIdxArray = np.array([])
stepEventsSig = np.array([])
stepEventsIdx = np.array([])
stepEventsVal = np.array([])
stepEnergy = np.array([])
stepPeakArray = np.array([])

# In[75]:
# data = open('tenfeetninestep2_0.txt')
# sig = np.loadtxt(data)
# # #
# noisedata = open('1114sensor0_4.txt')
# noise = np.loadtxt(noisedata)

sig0 = np.asarray(all_vib[0])
sig1 = np.asarray(all_vib[1])

# data = open('tenfeetninestep1_0.txt')
# sig0 = np.loadtxt(data)
#
# data = open('tenfeetninestep1_1.txt')
# sig1 = np.loadtxt(data)

noiseSig = sig0[:10000]
rawSig = sig0[:60000]

# stepSig1 = rawSig[21800:21900]
# sEnergy1 = np.dot(stepSig1.T, stepSig1)
#
# print sEnergy1

# In[76]:

idx = 1
while idx < len(noiseSig) - max(windowSize, eventSize) - 10:
    windowData = noiseSig[idx:idx+windowSize-1]
    windowDataEnergy = np.dot(windowData.T, windowData)
    windowDataEnergyArray = np.hstack((windowDataEnergyArray, windowDataEnergy))
#     if idx == 1:
#         windowDataEnergyArray = windowDataEnergy
#     else:
#         windowDataEnergyArray = np.hstack((windowDataEnergyArray, windowDataEnergy))
    idx = idx + offSet


# In[77]:

(noiseMu,noiseSigma) = norm.fit(windowDataEnergyArray)
print (noiseMu,noiseSigma)

# In[70]:

idx = 1
signal = rawSig


# In[78]:

while idx < len(signal) - 2 * max(windowSize, eventSize):
    # if one sensor detected, we count all sensor detected it
    windowData = signal[idx:idx+windowSize-1]
    windowDataEnergy = np.dot(windowData.T, windowData)

    # gaussian fit
    if abs(windowDataEnergy - noiseMu) < noiseSigma * sigmaSize:
        if states == 1 and (idx < len(signal) - eventSize):
            # find the event peak as well as the event
            stepEnd = idx
            stepRange = rawSig[stepStart:stepEnd]
            localPeakValue = np.max(np.abs(stepRange))
            localPeak = np.argmax(np.abs(stepRange))
            stepPeak = stepStart + localPeak - 1

            stepPeakArray = np.append(stepPeakArray, stepPeak)

            # extract clear signal
            stepStartIdx = max(stepPeak - WIN1, stepStart)
            stepStopIdx = stepStartIdx + eventSize - 1
            stepSig = rawSig[stepStartIdx:stepStopIdx]
            sEnergy = np.dot(stepSig.T, stepSig)
            stepEnergy = np.append(stepEnergy, sEnergy)
            stepStartIdxArray = np.hstack((stepStartIdxArray, stepStartIdx))
            stepStopIdxArray = np.hstack((stepStopIdxArray, stepStopIdx))

            # save the signal
            #if stepSig.shape[1] == 1:
            #    stepEventsSig = np.vstack((stepEventsSig, stepSig.T))
            #else:
            #print stepEventsSig.shape
            #print stepSig.shape
            stepEventsSig = np.hstack((stepEventsSig, stepSig))

            stepEventsIdx = np.hstack((stepEventsIdx, stepPeak))
            stepEventsVal = np.hstack((stepEventsVal, localPeakValue))

            # move the index to skip the event
            idx = stepStopIdx - offSet
        states = 0
    else:
        # mark step
        if states == 0:
            stepStart = idx
            states = 1

    idx = idx + offSet


# In[79]:

# unfinished Step
if states == 1:
    stepEnd = len(signal)
    stepRange = rawSig[stepStart:stepEnd]
    localPeakValue = np.max(np.abs(stepRange))
    localPeak = np.argmax(np.abs(stepRange))
    stepPeak = stepStart + localPeak - 1

    stepPeakArray = np.append(stepPeakArray, stepPeak)

    # extract clear signal
    stepStartIdx = max(stepPeak - WIN1, stepStart)
    stepStopIdx = stepStartIdx + eventSize - 1
    stepSig = rawSig[stepStartIdx:stepStopIdx]
    stepStartIdxArray = np.hstack((stepStartIdxArray, stepStartIdx))
    stepStopIdxArray = np.hstack((stepStopIdxArray, stepStopIdx))
    sEnergy = np.dot(stepSig.T, stepSig)
    stepEnergy = np.append(stepEnergy, sEnergy)

    # save the signal
    #if stepSig.shape[1] == 1:
    #    stepEventsSig = np.vstack((stepEventsSig, stepSig.T))
    #else:
    stepEventsSig = np.hstack((stepEventsSig, stepSig))

    stepEventsIdx = np.hstack((stepEventsIdx, stepPeak))
    stepEventsVal = np.hstack((stepEventsVal, localPeakValue))

print stepStartIdxArray

print stepStopIdxArray
#
print stepEnergy
stepEnergy = stepEnergy / (stepEnergy.max())
print stepEnergy
# stepEnergyWindow = np.ones(7)
#
# i = 0
# while i < 7:
#     stepEnergyWindow[i] = stepEnergy[i]+stepEnergy[i+1]
#     i = i + 1
#
# stepEnergyWindow = stepEnergyWindow / (stepEnergyWindow.max())
# print stepEnergyWindow

print "peak value:"
print stepPeakArray

# time_file = open('time0.txt')
# time = np.loadtxt(time_file)

time = np.asarray(all_time[0])

print time[0]
print time[1]
print time[2]
print time[len(time)-1]
print len(time)

print sig1[0]
print sig1[1]
print sig1[2]
print sig1[3]
print sig1[4]




print "time for peak value:"
for i in range(0, len(stepPeakArray)):
    print time[stepPeakArray[i]]

print "=============================="
print sig0[39036]
print sig0[39037]
print sig0[39038]
print sig0[39039]