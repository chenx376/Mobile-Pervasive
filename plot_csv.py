import numpy as np
import matplotlib.pyplot as plt

filename = "data_192.168.0.116_2018-Mar-09_00-25-21.csv"
data = np.genfromtxt(filename, delimiter=',', names=['timestamp', 'val'])

plt.plot(data["val"], linewidth = 0.2)
plt.show()
