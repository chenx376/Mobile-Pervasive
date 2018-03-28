import os
import struct
import math
import matplotlib.pyplot as plt

base_dir = '10feet_9step_2'
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

plt.figure(1)
for index in range(sensor_cnt):
    plt.subplot(sensor_cnt, 1, index + 1)
    plt.plot(all_time[index], all_vib[index])
plt.show()
