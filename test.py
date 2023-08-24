import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import LineCollection


n = 10
x = np.arange(0, n, step=.5)
y = x ** 2

norm = plt.Normalize(y.min(), y.max())

norm_y = norm(y)
print(norm_y)
plt.scatter(x, y, c=norm_y, cmap='viridis')

