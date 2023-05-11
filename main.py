import os
import pandas as pd
import json
from flask import Flask, render_template, request
import library.animation as anmtn
import library.motion as mtn
from library.IO import *
from library.constants import *

app = Flask(__name__)


@app.route("/", methods=['GET'])
def input_parameters():
    return render_template('input.html', recording_names=os.listdir(INPUT_FOLDER))


@app.route('/result', methods=['POST'])
def result():
    weights_groups = pd.DataFrame([json.loads(weights) for weights in request.form.getlist("weights_groups[]")])
    marks_motion_0 = [0 if mark == "" else int(mark) for mark in request.form.getlist("marks_motion_0[]")]
    marks_motion_1 = [0 if mark == "" else int(mark) for mark in request.form.getlist("marks_motion_1[]")]
    flag_visualized_vector = True if request.form.get("flag_visualized_velocity") == "yes" else False
    flag_heatmap = True if request.form.get("flag_heatmap") == "yes" else False
    file_name_0 = request.form.get("file_name_0")
    file_name_1 = request.form.get("file_name_1")
    label_motion_0 = request.form.get("label_motion_0")
    label_motion_1 = request.form.get("label_motion_1")

    # marks_motion_0 = [7600, 7850]
    # marks_motion_1 = [9300, 9800]

    animation_settings = anmtn.Setting(
        flag_visualized_vector=flag_visualized_vector,
        flag_heatmap=flag_heatmap
    )

    # input_types = get_recording_types([], animation_settings)
    #
    # print(input_types)

    meta_data_0 = mtn.MetaData(file_name_0, marks_motion_0[0], marks_motion_0[-1], label_motion_0)
    meta_data_1 = mtn.MetaData(file_name_1, marks_motion_1[0], marks_motion_1[-1], label_motion_1)

    motions = get_motions([meta_data_0, meta_data_1], RECORDING_TYPES)

    for motion in motions:
        motion.centre().confront()

    motions[1].synchronized_by(motions[0], weights_groups, marks_motion_0)

    animation = anmtn.Animation(motions, animation_settings)

    return animation.to_html5_video()


if __name__ == '__main__':
    app.run()
