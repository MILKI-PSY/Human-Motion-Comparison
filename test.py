import base64
from io import BytesIO
import os
from constants import *
from flask import Flask, render_template, request
import json
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

from flask import Flask
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

app = Flask(__name__)

@app.route("/")
def hello():
    t = np.linspace(0, 2 * np.pi)
    x = np.sin(t)

    fig, ax = plt.subplots()
    ax.axis([0, 2 * np.pi, -1, 1])
    l, = ax.plot([], [])

    def animate(i):
        l.set_data(t[:i], x[:i])

    ani = FuncAnimation(fig, animate, frames=len(t))

    return ani.to_html5_video()

    # render_template("result.html", video="<p>12321</p>")


if __name__ == '__main__':
    app.run()
