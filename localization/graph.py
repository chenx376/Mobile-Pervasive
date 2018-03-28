import numpy as np
import matplotlib.pyplot as plt

data = open('data60_0.txt')
sig = np.loadtxt(data)

# sig = sig[:160000]
length = len(sig)

fig = plt.figure(1)

X = np.linspace(0, length, length, endpoint=True)

plt.subplot(211)
plt.plot(X, sig, color='blue', linewidth=1.0, linestyle=':', label='123')
plt.xlabel("data point")
plt.ylabel("value")

plt.show()

# data = open('data60_1.txt')
# sig = np.loadtxt(data)
# # sig = sig[:160000]
# length = len(sig)
#
# X = np.linspace(0, length, length, endpoint=True)
# plt.subplot(212)
# plt.plot(X, sig, color='blue', linewidth=1.0, linestyle=':', label='123')
#
# plt.show()
#
# print length
