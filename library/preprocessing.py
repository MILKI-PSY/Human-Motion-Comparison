import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from library.constants import *


def get_dataframe(file_name, start, end):
    used_cols = []
    for joints in SIMPLIFIED_JOINTS:
        used_cols.append(joints + " x")
        used_cols.append(joints + " y")
        used_cols.append(joints + " z")
    used_cols += ["Frame"]

    all_path = RECORDINGS_FOLDER + file_name + "\\data.xlsx"
    velocity_recording = pd.read_excel(all_path, sheet_name="Segment Velocity", usecols=used_cols)
    return velocity_recording[start: end]


def generate_velocity_line_graph(velocity_recording):
    def calculate_norm(row):
        return np.linalg.norm(row.values)

    recording_chart = pd.DataFrame()
    recording_without_frame = velocity_recording.loc[:, velocity_recording.columns != "Frame"]

    recording_chart_sum = pd.DataFrame()
    for i in range(0, recording_without_frame.shape[1], 3):
        columns = recording_without_frame.iloc[:, i:i + 3]
        recording_chart_sum[f'Norm_{i // 3 + 1}'] = columns.apply(calculate_norm, axis=1)

    recording_chart["Sum"] = recording_chart_sum.sum(axis=1)
    recording_chart["Frame"] = velocity_recording["Frame"]
    plt.figure(figsize=(10, 1))
    plt.axis('off')
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.plot(recording_chart["Frame"], recording_chart["Sum"])

    string_io_bytes = io.BytesIO()
    plt.savefig(string_io_bytes, format='jpg')
    string_io_bytes.seek(0)
    return base64.b64encode(string_io_bytes.read()).decode()
