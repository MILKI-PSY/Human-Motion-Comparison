import os
import json
import pandas as pd
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import library.animation as anm
import library.motion as mt
import library.comparison as cp
import library.IO as myio
from library.constants import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route("/", methods=['GET'])
def input_parameters():
    return render_template('input.html', recording_names=os.listdir(INPUT_FOLDER))


@app.route('/result', methods=['POST'])
def result():
    weights_groups = pd.DataFrame([json.loads(weights) for weights in request.form.getlist("weights_groups[]")])
    marks = [int(mark) for mark in request.form.getlist("marks[]")]
    selected_range = [int(selected_range) for selected_range in request.form.getlist("selected_range[]")]
    motion_name = request.form.get("motion_name")
    flag_visualized_vector = True if request.form.get("flag_visualized_velocity") == "yes" else False
    flag_heatmap = True if request.form.get("flag_heatmap") == "yes" else False
    recording_name = request.form.get("recording_name")

    selected_range = [9300, 9550]
    # selected_range = [9300, 9800]

    meta_data_0 = mt.MetaData("reference\\" + motion_name, -1, -1, "Expert")
    meta_data_1 = mt.MetaData(recording_name, selected_range[0], selected_range[-1], "Leaner")

    animation_settings = myio.AnimationSetting(
        flag_visualized_vector=flag_visualized_vector,
        flag_heatmap=flag_heatmap,
        flag_repeat=False,
        visualized_vector="Segment Velocity",
        heatmap_recording="Score"
    )

    io = myio.MyIO(
        flag_output_xlsx=False,
        flag_show_animation=True,
        flag_output_gif=False,
        xlsx_settings=None,
        animation_settings=animation_settings,
        motions_meta=[meta_data_0, meta_data_1]
    )

    motions = io.get_motions()
    default_weights = DEFAULT_WEIGHTS[motion_name]

    comparison = cp.Comparison(weights_groups, default_weights["marks"])

    # for motion in motions:
    #     motion.centre().confront()
    #
    # motions[1].synchronized_by(motions[0])
    with app.test_request_context('/'):
        socketio.emit('loading information', {'info': "comparing motions"}, namespace="/")
    result = comparison.compare(motions[0], motions[1], io.get_comparison_types())

    return io.output_web(motions, result)


@socketio.on('my event')
def mtest_message(message):
    print(message)
    emit('my response', {'data': message['data']})


@socketio.on('choose motion')
def send_default_information_about_chosen_motion(message):
    file_path = INPUT_FOLDER + 'reference\\' + message['data'] + '\\information.json'

    # Open the file in read mode
    with open(file_path, "r") as json_file:
        data_image = json.load(json_file)

    data = DEFAULT_WEIGHTS[message['data']]
    print(data_image['image'])
    emit('choose motion', {'weights': json.dumps(data["weights"]), "marks": json.dumps(data["marks"]),
                           "image": data_image['image']})


@socketio.on('choose lerner recording')
def send_default_information_about_lerner_recording(message):
    print(message['data'])
    file_path = INPUT_FOLDER + message['data'] + '\\information.json'

    # Open the file in read mode
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    emit('choose lerner recording', data)


@socketio.on('connect')
def connected_msg():
    print('client connected.')


@socketio.on('disconnect')
def connected_msg():
    print('client disconnected.')


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run()
