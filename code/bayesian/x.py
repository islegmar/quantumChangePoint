import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

fCSVSquareRoot="data/CSquareRoot-20-0-global0.csv"
dSquareRoot=np.genfromtxt(fCSVSquareRoot,delimiter=",", names=["x", "y"])
plt.scatter(dSquareRoot['x'], dSquareRoot['y'], label='Square Root Measurement')

x_new = np.arange(0.001, 1.0, 0.001)
a_BSpline = interpolate.make_interp_spline(dSquareRoot['x'], dSquareRoot['y'])
y_new = a_BSpline(x_new)
plt.plot(x_new, y_new)
plt.show()
