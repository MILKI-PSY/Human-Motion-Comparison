import numpy as np
import pandas as pd
import math
from dtw import *
from scipy.spatial.distance import euclidean
from constants import *


def centre(recording):
    columns_with_x = recording.columns[recording.columns.str.contains("x")]
    columns_with_y = recording.columns[recording.columns.str.contains("y")]
    columns_with_z = recording.columns[recording.columns.str.contains("z")]
    recording[columns_with_x] = recording[columns_with_x].sub(recording["Pelvis x"], axis='index')
    recording[columns_with_y] = recording[columns_with_y].sub(recording["Pelvis y"], axis='index')
    recording[columns_with_z] = recording[columns_with_z].sub(recording["Pelvis z"], axis='index')
    return recording


def calculate_sin_cos(position_frame):
    opposite = position_frame["Left Upper Arm y"] - position_frame["Right Upper Arm y"]
    adjacent = position_frame["Left Upper Arm x"] - position_frame["Right Upper Arm x"]
    hypotenuse = math.sqrt(adjacent ** 2 + opposite ** 2)
    return opposite / hypotenuse, adjacent / hypotenuse


def get_rotation_parameters(position_recording):
    rotation_parameters = pd.DataFrame()
    rotation_parameters[["sin", "cos"]] = position_recording.apply(calculate_sin_cos, axis=1, result_type="expand")
    return rotation_parameters


def rotate(frame, sin, cos):
    rotation_matrix = np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])
    for joint in SIMPLIFIED_JOINTS:
        frame[[joint + " x", joint + " y", joint + " z"]] = np.dot(rotation_matrix,
                                                                   frame[[joint + " x", joint + " y", joint + " z"]]).T
    return frame


def confront(recording, rotation_parameters):
    recording[recording.columns] = recording.apply(
        lambda x: rotate(x, rotation_parameters["sin"][x.name], rotation_parameters["cos"][x.name]), axis=1,
        result_type="expand")
    return recording


# not finished, not sure if it necessary
def get_body_size():
    body_size = {}
    for joint_connection in SKELETON_CONNECTION_MAP:
        endpoint_0 = joint_connection[0]
        endpoint_1 = joint_connection[1]
        #body_size[(endpoint_0, endpoint_1)]
        return body_size


def frame_distance(frame_0, frame_1):
    distance = 0
    for index in range(0, len(frame_0), 3):
        joint_in_frame_0 = [frame_0[index], frame_0[index + 1], frame_0[index + 2]]
        joint_in_frame_1 = [frame_1[index], frame_1[index + 1], frame_1[index + 2]]
        distance += euclidean(joint_in_frame_0, joint_in_frame_1)
    return distance


def synchronize_motions(recording_0, recording_1, position_recording):
    alignment = dtw(recording_0, recording_1, dist_method=frame_distance)
    synchronized_position_recording = pd.DataFrame(columns=position_recording.columns)
    synchronized_recording_1 = pd.DataFrame(columns=recording_1.columns)
    index = -1
    for step in range(len(alignment.index1)):
        if index != alignment.index1[step]:
            index = alignment.index1[step]
            synchronized_position_recording = pd.concat(
                [synchronized_position_recording, position_recording.iloc[alignment.index2[step]].to_frame().T],
                ignore_index=True)
    return synchronized_position_recording



