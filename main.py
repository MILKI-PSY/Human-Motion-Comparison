import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
# Fixing random state for reproducibility
np.random.seed(19680801)
matplotlib.use('Qt5Agg')

def random_walk(num_steps, max_step=0.05):
    """Return a 3D random walk as (num_steps, 3) array."""
    start_pos = np.random.random(3)
    steps = np.random.uniform(-max_step, max_step, size=(num_steps, 3))
    walk = start_pos + np.cumsum(steps, axis=0)
    return walk


def update_lines(num, walk, lines):
    # NOTE: there is no .set_data() for 3 dim data...
    lines.set_data([num/10, num/10+0.1], [num/10, num/10+0.1])
    lines.set_3d_properties([num/10, num/10+0.1])
    return lines


# Data: 40 random walks as (num_steps, 3) arrays
num_steps = 30
walks = [random_walk(num_steps) for index in range(40)]

# Attaching 3D axis to the figure
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

# Create lines initially without data
lines = ax.plot([], [], [])[0]


# Creating the Animation object
ani = animation.FuncAnimation(
    fig, update_lines, num_steps, fargs=(, lines), interval=100)

plt.show()