import os
import Queue
import struct
import math
import threading
from time import sleep


class Data(threading.Thread):
    def __init__(self, base_dir, sensor_id):
        threading.Thread.__init__(self, name=sensor_id)
        self.base_dir = base_dir
        self.sensor_id = sensor_id
        self.file_prefix = 'data_'
        self.file_size = 5 * 1024
        self.file_read = 0
        self.pre_buffer = ''
        self.separator1 = '\xff\xff'
        self.separator2 = '\xfe\xfe'
        self.buffer_size = 256
        self.time_size = 6
        self.TIME_OVERFLOW = 1099511627776
        self.TIME_RES = 0.000015650040064103
        self.queue = Queue.Queue(0)
        self.vib = []

    def run(self):
        print 'sensor ' + self.sensor_id + ' start'
        while True:
            file_name = self.file_prefix + str(self.file_read)
            file_path = os.path.join(self.base_dir, self.sensor_id, file_name)
            if not os.path.exists(file_path) or os.path.getsize(file_path) != self.file_size:
                print 'sensor ' + self.sensor_id + ' no file'
                sleep(1)
                continue
            print 'sensor ' + self.sensor_id + ' reading file: ' + file_path
            with open(file_path, 'rb') as f:
                content = self.pre_buffer + f.read()
                buffers = content.split(self.separator1)
                if len(buffers[0]) == 0:
                    del buffers[0]
                buffer_count = len(buffers)
                if len(buffers[buffer_count - 1]) != self.time_size and len(buffers[buffer_count - 1]) != self.buffer_size:
                    self.pre_buffer = buffers[buffer_count - 1]
                    del buffers[buffer_count - 1]
                else:
                    if len(buffers[buffer_count - 1]) == self.time_size:
                        time_check = buffers[buffer_count - 1]
                        if time_check[0:2] != self.separator2:
                            self.pre_buffer = buffers[buffer_count - 1]
                            del buffers[buffer_count - 1]
                        else:
                            self.pre_buffer = ''
                    else:
                        self.pre_buffer = ''
                for buf in buffers:
                    if len(buf) == self.buffer_size:
                        for i in range(0, self.buffer_size - 1, 2):
                            vib = ord(buf[i]) + ord(buf[i + 1]) * 256
                            self.vib.append(vib)
                        print 'sensor ' + self.sensor_id + ' add vib: ' + str(len(self.vib))
                    elif len(buf) == self.time_size:
                        buf = buf[2:]
                        time = bytearray()
                        for i in buf:
                            time.append(i)
                        for i in range(4):
                            time.append('\x00')
                        time = struct.unpack('L', time)[0]
                        if time < 0:
                            time = math.fmod(float(time), self.TIME_OVERFLOW) * self.TIME_RES
                        self.queue.put({time: self.vib}, block=False)
                        print 'sensor ' + self.sensor_id + ' add queue: ' + str(time) + " : " + str(len(self.vib))
                        self.vib = []
                    else:
                        print 'sensor ' + self.sensor_id + ' error: ' + str(len(buf))
            self.file_read += 1