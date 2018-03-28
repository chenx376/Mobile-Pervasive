
# coding: utf-8

# In[73]:

import numpy as np
from scipy.stats import norm


# In[74]:

windowSize = (int)(1000)
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
data = open('tenfeetninestep2_0.txt')
sig = np.loadtxt(data)
# # #
# noisedata = open('1114sensor0_4.txt')
# noise = np.loadtxt(noisedata)

noiseSig = sig[:10000]
rawSig = sig[:60000]

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
        if states == 0 and (idx - stepPeak > WIN1):
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

time_file = open('time0.txt')
time = np.loadtxt(time_file)

print "time for peak value:"
for i in range(0, len(stepPeakArray)):
    print time[stepPeakArray[i]+1]