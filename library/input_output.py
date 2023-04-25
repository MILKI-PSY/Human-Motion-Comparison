from constants import *
import pandas as pd
from library.motion import Motion


def get_joints_cols():
    used_cols = []
    for joints in SIMPLIFIED_JOINTS:
        used_cols.append(joints + " x")
        used_cols.append(joints + " y")
        used_cols.append(joints + " z")
    return used_cols


def get_all_path(file_name):
    return DATA_PATH + file_name + "\\data.xlsx"


def get_motion(file_name, start, end, label="No Label"):
    if DEBUG_INFO: print("start generating " + label + " from " + file_name)

    used_cols = get_joints_cols()
    motion_data = pd.read_excel(get_all_path(file_name), sheet_name=SHEET_NAMES, usecols=used_cols)
    position_recording = motion_data[POSITION_RECORDING_NAME][start:end]
    velocity_recording = motion_data[VELOCITY_RECORDING_NAME][start:end]
    return Motion(position_recording, velocity_recording, label)
