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

from library.input_output import *
from library.animation import *

if __name__ == '__main__':
    marks_motion_0 = [7600, 7850]
    marks_motion_1 = [9300, 9800]

    file_name_0 = "P01_B_cut"
    file_name_1 = "P01_B_cut"

    motion_0 = get_motion(file_name_0, marks_motion_0[0], marks_motion_0[-1])
    motion_1 = get_motion(file_name_1, marks_motion_1[0], marks_motion_1[-1])

    motion_0.centre().confront()
    motion_1.centre().confront()

    weight = {}
    for joint in SIMPLIFIED_JOINTS:
        weight[joint] = 1

    weights_groups = pd.DataFrame([weight])

    synced_motion_1 = motion_1.synchronized_by(motion_0, weights_groups, marks_motion_0)
    ani = Animation([motion_0, synced_motion_1], False, True, True, )
