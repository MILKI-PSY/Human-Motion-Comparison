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


app = Flask(__name__)


@app.route("/")
def input_parameters():
    return render_template('input.html', recording_names=os.listdir(DATA_PATH))


@app.route('/result', methods=['POST'])
def my_form_post():
    weights_groups = [pd.DataFrame(json.loads(weights)) for weights in request.form.getlist("weights_groups[]")]
    marks_motion_0 = [0 if mark == "" else int(mark) for mark in request.form.getlist("marks_motion_0[]")]
    marks_motion_1 = [0 if mark == "" else int(mark) for mark in request.form.getlist("marks_motion_1[]")]
    flag_visualized_velocity = True if request.form.get("flag_visualized_velocity") == "yes" else False
    flag_heatmap = True if request.form.get("flag_heatmap") == "yes" else False
    file_name_0 = request.form.get("file_name_0")
    file_name_1 = request.form.get("file_name_1")






if __name__ == '__main__':
    app.run()
