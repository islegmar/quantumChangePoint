from matplotlib import pyplot as plt
import numpy as np

data = np.genfromtxt("test_file.csv", delimiter=",", names=["x", "y"])
plt.plot(data['x'], data['y'])
plt.show()

