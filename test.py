import base64
from io import BytesIO
import os
from constants import *
from flask import Flask, render_template, request
import json
import pandas as pd
from matplotlib.figure import Figure

app = Flask(__name__)


@app.route("/")
def input_parameters():
    return render_template('input.html', recording_names=os.listdir(DATA_PATH))


@app.route('/result', methods=['POST'])
def my_form_post():


    marks_motion_0 = request.form.get("marks_motion_0")
    marks_motion_1 = request.form.get("marks_motion_1")
    flag_visualized_velocity = request.form.get("flag_visualized_velocity")
    flag_heatmap = request.form.get("flag_heatmap")
    file_name_0 = request.form.get("file_name_0")
    file_name_1 = request.form.get("file_name_1")

    ls_weights_groups = []
    for weights in request.form.getlist("array_weights[]"):
        ls_weights_groups.append(json.loads(weights))
    weights_groups = pd.DataFrame(ls_weights_groups)

    print(weights_groups)

    print(marks_motion_0)
    print(marks_motion_1)
    print(weights_groups)

    print(flag_heatmap)
    print(file_name_0)
    print(file_name_1)

    print(flag_visualized_velocity)

    return render_template("result.html")


# def hello():
#     # Generate the figure **without using pyplot**.
#     fig = Figure()
#     ax = fig.subplots()
#     ax.plot([1, 2])
#     # Save it to a temporary buffer.
#     buf = BytesIO()
#     fig.savefig(buf, format="png")
#     # Embed the result in the html output.
#     data = base64.b64encode(buf.getbuffer()).decode("ascii")
#     return render_template('input.html',
#                            src=f'data:image/png;base64,{data}',
#                            my_str="aaa"
#                            )


if __name__ == '__main__':
    app.run()
