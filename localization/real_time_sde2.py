import Data
from time import sleep
import Queue as queue

import numpy as np
from scipy.stats import norm

base_dir = '10feet_9step_2'
sensor_cnt = 2
data_arr = []

# sensor id range from 0 -> sensor_cnt - 1
for i in range(0, sensor_cnt):
    data = Data.Data(base_dir, str(i))
    data.setDaemon(True)
    data_arr.append(data)

for i in range(0, sensor_cnt):
    data_arr[i].start()

timestamp = 0
pre_timestamp = 0
timestamp_1 = 0
pre_timestamp_1 = 0
noiseFlag0 = 0
noiseFlag1 = 0
noiseSig = np.array([])
buffer_signal_0 = np.array([])
buffer_signal_1 = np.array([])
buffer_time_0 = np.array([])
buffer_time_1 = np.array([])
buffer_start_0 = 0
buffer_start_1 = 0
noiseSig_0 = np.array([])
noiseSig_1 = np.array([])
q0 = queue.Queue(maxsize = 10)
q1 = queue.Queue(maxsize = 10)

while True:

    time0 = np.array([])
    time1 = np.array([])
    for i in range(0, sensor_cnt):
        # every element in queue is {timestamp:[vibration integer, vibration integer, ..., vibration integer]}
        queue = data_arr[i].queue
        qsize = queue.qsize()

        while qsize < 7:
            sleep(1)
            qsize = queue.qsize()

        size = min(10, qsize)

        if i == 0:
            file_object = open('data0.txt', 'w')
            time_object = open('time0.txt', 'w')

            if len(buffer_signal_0) > 0:
                for p in range(0, len(buffer_signal_0)):
                    file_object.write(str(buffer_signal_0[p]))
                    file_object.write("\n")

                for p in range(0, len(buffer_time_0)):
                    time_object.write(str(buffer_time_0[p]))
                    time_object.write("\n")

                buffer_signal_0 = np.array([])
                buffer_time_0 = np.array([])

            for j in range(0, size):
                item = queue.get(j)
                num = len(item.values()[0])

                if pre_timestamp == 0:
                    pre_timestamp = item.keys()[0]
                elif timestamp == 0:
                    timestamp = item.keys()[0]
                else:
                    pre_timestamp = timestamp
                    timestamp = item.keys()[0]

                if pre_timestamp != 0 and timestamp != 0 and num != 0:
                    td = (timestamp - pre_timestamp) / num
                    time_object.write(str(pre_timestamp))
                    time_object.write("\n")
                    for p in range(1, num):
                        time_object.write(str(pre_timestamp+p*td))
                        time_object.write("\n")

                if timestamp != 0:
                    for m in range(0, len(item.values()[0])):
                        file_object.write(str((item.values()[0][m])))
                        file_object.write("\n")

            file_object.close()
            time_object.close()

            print "=================0 done================="

        elif i == 1:
            file_object = open('data1.txt', 'w')
            time_object = open('time1.txt', 'w')

            if len(buffer_signal_1) > 0:
                for p in range(0, len(buffer_signal_1)):
                    file_object.write(str(buffer_signal_1[p]))
                    file_object.write("\n")

                for p in range(0, len(buffer_time_1)):
                    time_object.write(str(buffer_time_1[p]))
                    time_object.write("\n")

                buffer_signal_1 = np.array([])
                buffer_time_1 = np.array([])

            for j in range(0, size):
                item = queue.get(j)
                num = len(item.values()[0])

                if pre_timestamp_1 == 0:
                    pre_timestamp_1 = item.keys()[0]
                elif timestamp_1 == 0:
                    timestamp_1 = item.keys()[0]
                else:
                    pre_timestamp_1 = timestamp_1
                    timestamp_1 = item.keys()[0]

                if pre_timestamp_1 != 0 and timestamp_1 != 0 and num != 0:
                    td = (timestamp_1 - pre_timestamp_1) / num
                    time_object.write(str(pre_timestamp_1))
                    time_object.write("\n")
                    for p in range(1, num):
                        time_object.write(str(pre_timestamp_1 + p * td))
                        time_object.write("\n")

                if timestamp_1 != 0:
                    for m in range(0, len(item.values()[0])):
                        file_object.write(str((item.values()[0][m])))
                        file_object.write("\n")

            file_object.close()
            time_object.close()


        #start to detect

        windowSize = (int)(1000)
        WIN1 = windowSize / 2
        WIN2 = windowSize
        offSet = windowSize / 2
        eventSize = WIN1 + WIN2
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

        if i == 0:
            data = open('data0.txt')
            sig = np.loadtxt(data)

        elif i == 1:
            data = open('data1.txt')
            sig = np.loadtxt(data)

        length = len(sig)
        rawSig = sig[:length]
        # noiseSig = sig[:5000]
        if noiseFlag0 == 0 or noiseFlag1 == 0:
            if i == 0:
                noiseSig_0 = sig[:10000]
                noiseFlag0 = 1
                noiseSig = noiseSig_0
            elif i == 1:
                noiseSig_1 = sig[:10000]
                noiseFlag1 = 1
                noiseSig = noiseSig_1
        else:
            if i == 0:
                noiseSig = noiseSig_0
            elif i == 1:
                noiseSig = noiseSig_1

        idx = 1
        while idx < len(noiseSig) - max(windowSize, eventSize) - 10:
            windowData = noiseSig[idx:idx + windowSize - 1]
            windowDataEnergy = np.dot(windowData.T, windowData)
            windowDataEnergyArray = np.hstack((windowDataEnergyArray, windowDataEnergy))
            idx = idx + offSet

        (noiseMu, noiseSigma) = norm.fit(windowDataEnergyArray)
        print (noiseMu, noiseSigma)

        idx = 1
        signal = rawSig

        while idx < len(signal) - 2 * max(windowSize, eventSize):
            # if one sensor detected, we count all sensor detected it
            windowData = signal[idx:idx + windowSize - 1]
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

        # unfinished Step
        if states == 1:
            stepEnd = len(signal)
            stepstop = stepStopIdxArray[len(stepStopIdxArray)-1]
            stepRange = rawSig[stepstop:stepEnd]

            if i == 0:
                buffer_signal_0 = stepRange
                buffer_start_0 = stepstop

            elif i == 1:
                buffer_signal_1 = stepRange
                buffer_start_1 = stepstop

        print stepStartIdxArray

        print stepStopIdxArray

        print stepPeakArray

        if i == 0:
            time_file = open('time0.txt')
            time = np.loadtxt(time_file)

            for n in range(0, len(stepPeakArray)):
                time0 = np.append(time0, time[stepPeakArray[n]])
                q0.put(time[stepPeakArray[n]])
                print time[stepPeakArray[n]]

            buffer_time_0 = time[buffer_start_0:len(time)]

        elif i == 1:
            time_file = open('time1.txt')
            time = np.loadtxt(time_file)

            for n in range(0, len(stepPeakArray)):
                time1 = np.append(time1, time[stepPeakArray[n]])
                q1.put(time[stepPeakArray[n]])
                print time[stepPeakArray[n]]

            buffer_time_1 = time[buffer_start_1:len(time)]

    # calculate time difference:
    if q0.qsize() > 0 and q1.qsize() > 0:
        file_result = open('result.txt', 'w')
        minsize = min(q0.qsize(), q1.qsize())
        for m in range(0, minsize):
            timestamp_sensor0 = q0.get()
            timestamp_sensor1 = q1.get()
            if np.abs(timestamp_sensor0 - timestamp_sensor1) < 50000:
                time_diff = timestamp_sensor1 - timestamp_sensor0
                estimate_diff = time_diff * 0.000230039
                estimate_dis = (3 + estimate_diff) / 2.0
                print "============================================"
                print estimate_dis
                file_result.write(str(estimate_dis))
                file_result.write("\n")
            else:
                if timestamp_sensor0 < timestamp_sensor1:
                    timestamp_sensor0 = q0.get()
                else:
                    timestamp_sensor1 = q1.get()
                if np.abs(timestamp_sensor0 - timestamp_sensor1) < 12000:
                    time_diff = timestamp_sensor1 - timestamp_sensor0
                    estimate_diff = time_diff * 0.000230039
                    estimate_dis = (3 + estimate_diff) / 2.0
                    print "============================================"
                    print estimate_dis
                    file_result.write(str(estimate_dis))
                    file_result.write("\n")

        file_result.close()

    sleep(1)