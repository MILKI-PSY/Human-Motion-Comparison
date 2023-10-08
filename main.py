import shutil
import json
import io
import os
import pandas as pd
from flask import Flask, render_template, request, send_file, send_from_directory
from flask_socketio import SocketIO, emit
from library.preprocessing import generate_velocity_line_graph, get_dataframe
import library.motion as mt
import library.comparison as cp
import library.wrapper as wrapper
from library.constants import *

app = Flask(__name__, static_folder="human-motion-comparison/static")
app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
socketio = SocketIO(app, engineio_logger=True, logger=True, max_http_buffer_size=1e9, ping_timeout=900,
                    ping_interval=300, resource='/human-motion-comparison/socket.io')


@app.route('/human-motion-comparison/static/<path:path>')
def send_js(path):
    return send_from_directory("human-motion-comparison/static/", path)


@app.route("/human-motion-comparison/help", methods=['GET', 'POST'])
def help():
    return render_template('help.html')


@app.route("/human-motion-comparison/main", methods=['GET', 'POST'])
def input_parameters():
    return render_template('main.html', reference_names=os.listdir(REFERENCES_FOLDER))


@app.route("/human-motion-comparison/management", methods=['GET', 'POST'])
def manage_references():
    return render_template('management.html', recording_names=os.listdir(RECORDINGS_FOLDER),
                           reference_names=os.listdir(REFERENCES_FOLDER))


@app.route('/human-motion-comparison/get-xlsx', methods=['GET', 'POST'])
def get_xlsx():
    return send_file(TEMP_FOLDER + "Result/result.xlsx")


@app.route('/human-motion-comparison/result', methods=['GET', 'POST'])
def result():
    weights_groups = pd.DataFrame([json.loads(weights) for weights in request.form.getlist("weights_groups[]")])
    marks = [int(mark) for mark in request.form.getlist("marks[]")]
    selected_range = [int(selected_range) for selected_range in request.form.getlist("selected_range[]")]
    reference_name = request.form.get("reference_name")
    flag_visualized_vector = True if request.form.get("flag_visualized_velocity") == "true" else False
    flag_heatmap = True if request.form.get("flag_heatmap") == "true" else False
    flag_dtw = True if request.form.get("flag_dtw") == "true" else False
    recording_name = request.form.get("recording_name")
    output_types = RECORDING_TYPES.copy()
    output_types.append("Score")

    if recording_name is None:
        return render_template('result.html')
    # selected_range = [9300, 9550]
    # selected_range = [9300, 9800]

    file_path_0 = REFERENCES_FOLDER + reference_name + "/data.xlsx"
    meta_data_0 = mt.MetaData(file_path_0, -1, -1, "Expert")

    file_path_1 = TEMP_FOLDER + recording_name + ".xlsx"
    meta_data_1 = mt.MetaData(file_path_1, selected_range[0], selected_range[-1], "Leaner")

    animation_settings = wrapper.AnimationSetting(
        flag_show=False,
        flag_save=False,
        flag_to_html5_video=True,
        flag_visualized_vector=flag_visualized_vector,
        flag_heatmap=flag_heatmap,
        flag_repeat=False,
        visualized_vector="Segment Velocity",
        heatmap_recording="Score"
    )

    xlsx_settings = wrapper.XlsxSetting(
        flag_save=True,
        xlsx_filename="result",
        output_types=output_types,
        save_path=TEMP_FOLDER + '/Result/result.xlsx'
    )

    average_score_image_settings = wrapper.AverageScoreImageSetting(
        flag_to_base64=True,
        flag_show=False
    )

    learning_wrapper = wrapper.Wrapper(
        xlsx_settings=xlsx_settings,
        animation_settings=animation_settings,
        average_score_image_settings = average_score_image_settings,
        motions_meta=[meta_data_0, meta_data_1]
    )

    motions = learning_wrapper.get_motions()
    comparison = cp.Comparison(weights_groups, marks)

    for motion in motions:
        motion.centre().confront()

    if flag_dtw:
        motions[1].synchronized_by(motions[0])

    result = comparison.compare(motions[0], motions[1], learning_wrapper.get_comparison_types())

    video, image = learning_wrapper.output(motions, result)
    return render_template('result.html', video=video, image=image)


@socketio.on('connect')
def connected_msg():
    print('client connected.')


@socketio.on('disconnect')
def connected_msg():
    print('client disconnected.')


@socketio.on('choose reference')
def send_default_information_about_chosen_reference(message):
    reference_name = message['reference_name']
    file_path = REFERENCES_FOLDER + reference_name + '/information.json'

    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    emit('update reference', data)


@socketio.on('choose recording')
def send_default_information_about_lerner_recording(message):
    file_path = RECORDINGS_FOLDER + message['recording_name'] + '/information.json'

    # Open the file in read mode
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    emit('update recording', data)


@socketio.on('save reference')
def save_reference(message):
    folder_path = REFERENCES_FOLDER + message['name']
    old_folder_path = REFERENCES_FOLDER + message['old_name']
    if os.path.exists(old_folder_path) and message['old_name'] != "":
        os.rename(old_folder_path, folder_path)
    else:
        os.makedirs(folder_path)

    for i, weights_group in enumerate(message["weights_groups"]):
        message["weights_groups"][i] = json.loads(weights_group)

    del message["old_name"]
    with open(folder_path + '/information.json', 'w+') as file:
        json.dump(message, file)

    if not os.path.exists(folder_path + '/data.xlsx'):
        shutil.move(TEMP_FOLDER + "Selected/data.xlsx", folder_path)

    emit('update reference list', {'reference_names': os.listdir(REFERENCES_FOLDER)})


@socketio.on('delete reference')
def delete_reference(message):
    folder_path = REFERENCES_FOLDER + message['name']
    shutil.rmtree(folder_path)
    emit('update reference list', {'reference_names': os.listdir(REFERENCES_FOLDER)})


@socketio.on('preprocess reference')
def preprocess_recording(message):
    file_name = message["recording_name"]
    start = message["selected_range_start"]
    end = message["selected_range_end"]
    data = get_dataframe(file_name, start, end)
    image = generate_velocity_line_graph(data)

    weights = {}
    for joint in SIMPLIFIED_JOINTS:
        weights[joint] = 1

    all_path = TEMP_FOLDER + "Selected/data.xlsx"
    with pd.ExcelWriter(all_path) as writer:
        for recoding_type in RECORDING_TYPES:
            data.to_excel(writer, sheet_name=recoding_type, index=False)

    emit('update reference',
         {'weights_groups': [weights], "marks": [], "image": image, "name": "New Reference", "start": start,
          "end": end})


@socketio.on('new recording')
def preprocess_and_save_new_recording(message):
    data = io.BytesIO(message['file'])
    dataframe = pd.read_excel(data, sheet_name="Segment Velocity")
    # velocity_recording = dataframe["Segement Velocity"]

    file_name = message["name"]

    information = {
        "start": 0,
        "end": len(dataframe) - 1,
        "image": generate_velocity_line_graph(dataframe),
    }

    folder_path = RECORDINGS_FOLDER + file_name
    while os.path.exists(folder_path):
        file_name = "new_" + file_name
        folder_path = RECORDINGS_FOLDER + file_name

    os.makedirs(folder_path)

    information_path = folder_path + '/information.json'

    with open(information_path, 'w+') as file:
        json.dump(information, file)

    all_path = folder_path + "/data.xlsx"
    with pd.ExcelWriter(all_path) as writer:
        for recoding_type in RECORDING_TYPES:
            dataframe.to_excel(writer, sheet_name=recoding_type, index=False)

    emit('update recording list', {'recording_names': os.listdir(RECORDINGS_FOLDER)})


@socketio.on('delete recording')
def delete_recording(message):
    print(message["name"])
    folder_path = RECORDINGS_FOLDER + message['name']
    shutil.rmtree(folder_path)
    emit('update recording list', {'recording_names': os.listdir(RECORDINGS_FOLDER)})


@socketio.on('upload learner recording')
def preprocess_learner_recording(message):
    print("in upload learner recording")
    data = io.BytesIO(message['file'])

    velocity_recording = pd.read_excel(data, sheet_name="Segment Velocity")

    information = {
        "image": generate_velocity_line_graph(velocity_recording),
        "start": 0,
        "end": len(velocity_recording) - 1
    }

    emit('update recording', information)

    temp_path = TEMP_FOLDER + "/" + message["name"] + ".xlsx"
    with open(temp_path, "wb") as file:
        file.write(data.getbuffer())


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
    # app.run()
