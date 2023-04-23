import base64
from io import BytesIO
import os
from constants import *
from flask import Flask, render_template, request
import json
import pandas as pd
from library.animation import *
from library.motion import *
from library.input_output import *

app = Flask(__name__)


@app.route("/", methods=['GET'])
def input_parameters():
    return render_template('input.html', recording_names=os.listdir(DATA_PATH))


@app.route('/result', methods=['POST'])
def my_form_post():
    weights_groups = pd.DataFrame([json.loads(weights) for weights in request.form.getlist("weights_groups[]")])
    marks_motion_0 = [0 if mark == "" else int(mark) for mark in request.form.getlist("marks_motion_0[]")]
    marks_motion_1 = [0 if mark == "" else int(mark) for mark in request.form.getlist("marks_motion_1[]")]
    flag_visualized_velocity = True if request.form.get("flag_visualized_velocity") == "yes" else False
    flag_heatmap = True if request.form.get("flag_heatmap") == "yes" else False
    file_name_0 = request.form.get("file_name_0")
    file_name_1 = request.form.get("file_name_1")
    label_motion_0 = request.form.get("label_motion_0")
    label_motion_1 = request.form.get("label_motion_1")

    marks_motion_0 = [7600, 7850]
    marks_motion_1 = [9300, 9800]

    motion_0 = get_motion(file_name_0, marks_motion_0[0], marks_motion_0[-1], label=label_motion_0)
    motion_1 = get_motion(file_name_1, marks_motion_1[0], marks_motion_1[-1], label=label_motion_1)

    motion_0.centre().confront()
    motion_1.centre().confront()

    synced_motion_1 = motion_1.synchronized_by(motion_0, weights_groups, marks_motion_0)
    ani = Animation([motion_0, synced_motion_1], flag_visualized_velocity, True, flag_heatmap, )

    return ani.to_html5_video()


if __name__ == '__main__':
    app.run()
