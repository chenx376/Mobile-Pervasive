import Data
from time import sleep

base_dir = '10feet_15step_1'
sensor_cnt = 2
data_arr = []

# sensor id range from 0 -> sensor_cnt - 1
for i in range(0, sensor_cnt):
    data = Data.Data(base_dir, str(i))
    data.setDaemon(True)
    data_arr.append(data)

for i in range(0, sensor_cnt):
    data_arr[i].start()

while True:
    for i in range(0, sensor_cnt):
        flag0 = 0
        flag1 = 0
        # every element in queue is {timestamp:[vibration integer, vibration integer, ..., vibration integer]}
        queue = data_arr[i].queue
        qsize1 = queue.qsize()
        sleep(5)
        qsize2 = queue.qsize()
        if qsize1 == qsize2:
            if i == 0:
                if flag0 == 1:
                    continue
                file_object = open('data0.txt', 'w')
                time_object = open('time0.txt', 'w')

                t1 = 0
                t2 = 0
                for j in range(0, qsize2):
                    item = queue.get(j)

                    num = len(item.values()[0])

                    if t1 == 0:
                        t1 = item.keys()[0]
                    elif t2 == 0:
                        t2 = item.keys()[0]
                    else:
                        t1 = t2
                        t2 = item.keys()[0]


                    if t2 == 0:
                        for p in range(0, num):
                            time_object.write(str(0))
                            time_object.write("\n")

                    if t1 != 0 and t2 != 0 and num != 0:
                        td = (t2 - t1) / num
                        time_object.write(str(t1))
                        time_object.write("\n")
                        for p in range(1, num):
                            time_object.write(str(t1+p*td))
                            time_object.write("\n")

                    for m in range(0, len(item.values()[0])):
                        file_object.write(str((item.values()[0][m])))
                        file_object.write("\n")


                file_object.close()
                time_object.close()
                flag0 = 1
                print "=========sensor 0 done============"
            elif i == 1:
                if flag1 == 1:
                    continue
                file_object_1 = open('data1.txt', 'w')
                time_object_1 = open('time1.txt', 'w')

                t1 = 0
                t2 = 0
                for j in range(0, qsize2):
                    item = queue.get(j)

                    num = len(item.values()[0])
                    if t1 == 0:
                        t1 = item.keys()[0]
                    elif t2 == 0:
                        t2 = item.keys()[0]
                    else:
                        t1 = t2
                        t2 = item.keys()[0]

                    if t2 == 0:
                        for p in range(0, num):
                            time_object_1.write(str(0))
                            time_object_1.write("\n")

                    if t1 != 0 and t2 != 0 and num != 0:
                        td = (t2 - t1) / num
                        time_object_1.write(str(t1))
                        time_object_1.write("\n")
                        for p in range(1, num):
                            time_object_1.write(str(t1+p*td))
                            time_object_1.write("\n")

                    for m in range(0, len(item.values()[0])):
                        file_object_1.write(str((item.values()[0][m])))
                        file_object_1.write("\n")

                file_object_1.close()
                time_object_1.close()

                flag1 = 1
                print "=========sensor 1 done============"

        if flag0 == 1 and flag1 == 1:
            print "===========finish============"
            break

    sleep(1)