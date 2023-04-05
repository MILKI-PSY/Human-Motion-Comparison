import numpy as np
import pandas as pd
import math
from dtw import *
from scipy.spatial.distance import euclidean
from constants import *


class Motion:
    def __init__(self, position_recording, velocity_recording=None):
        self.position_recording = position_recording
        self.velocity_recording = velocity_recording
        self.rotation_parameters = self.get_rotation_parameters()

    def get_rotation_parameters(self):
        def calculate_sin_cos(position_frame):
            opposite = position_frame["Left Upper Arm y"] - position_frame["Right Upper Arm y"]
            adjacent = position_frame["Left Upper Arm x"] - position_frame["Right Upper Arm x"]
            hypotenuse = math.sqrt(adjacent ** 2 + opposite ** 2)
            return opposite / hypotenuse, adjacent / hypotenuse

        rotation_parameters = pd.DataFrame()
        rotation_parameters[["sin", "cos"]] = self.position_recording.apply(calculate_sin_cos, axis=1,
                                                                            result_type="expand")

        return rotation_parameters


def centre(motion):
    columns_with_x = motion.position_recording.columns[motion.position_recording.columns.str.contains("x")]
    columns_with_y = motion.position_recording.columns[motion.position_recording.columns.str.contains("y")]
    columns_with_z = motion.position_recording.columns[motion.position_recording.columns.str.contains("z")]
    motion.position_recording[columns_with_x] = motion.position_recording[columns_with_x].sub(
        motion.position_recording["Pelvis x"], axis='index')
    motion.position_recording[columns_with_y] = motion.position_recording[columns_with_y].sub(
        motion.position_recording["Pelvis y"], axis='index')
    motion.position_recording[columns_with_z] = motion.position_recording[columns_with_z].sub(
        motion.position_recording["Pelvis z"], axis='index')
    return motion


def confront(motion):
    def rotate(frame, sin, cos):
        rotation_matrix = np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])
        for joint in SIMPLIFIED_JOINTS:
            frame[[joint + " x", joint + " y", joint + " z"]] = np.dot(rotation_matrix,
                                                                       frame[[joint + " x", joint + " y",
                                                                              joint + " z"]]).T
        return frame

    series_sin = motion.rotation_parameters["sin"]
    series_cos = motion.rotation_parameters["cos"]
    motion.position_recording[motion.position_recording.columns] = motion.position_recording.apply(
        lambda x: rotate(x, series_sin[x.name], series_cos[x.name]), axis=1, result_type="expand")
    motion.velocity_recording[motion.velocity_recording.columns] = motion.velocity_recording.apply(
        lambda x: rotate(x, series_sin[x.name], series_cos[x.name]), axis=1, result_type="expand")
    return motion


def synchronize_motions(motion_0, motion_1):
    def frame_distance(frame_0, frame_1):
        distance = 0
        for i in range(0, len(frame_0), 3):
            joint_in_frame_0 = [frame_0[i], frame_0[i + 1], frame_0[i + 2]]
            joint_in_frame_1 = [frame_1[i], frame_1[i + 1], frame_1[i + 2]]
            distance += euclidean(joint_in_frame_0, joint_in_frame_1)
        return distance

    alignment = dtw(motion_0.velocity_recording, motion_1.velocity_recording, dist_method=frame_distance)
    synchronized_position_recording = pd.DataFrame(columns=motion_0.position_recording.columns)
    synchronized_recording_1 = pd.DataFrame(columns=motion_0.velocity_recording.columns)
    i = -1
    for step in range(len(alignment.index1)):
        if i != alignment.index1[step]:
            i = alignment.index1[step]
            synchronized_position_recording = pd.concat(
                [synchronized_position_recording,
                 motion_1.position_recording.iloc[alignment.index2[step]].to_frame().T],
                ignore_index=True)
    return Motion(synchronized_position_recording)


def get_scores(recording_0, recording_1):
    def vector_euclidean(arr_0, arr_1):
        return np.sqrt(np.sum(np.square(arr_0 - arr_1), axis=1))

    joints_distances = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low = index * 3
        upp = index * 3 + 3
        joints_distances[joint] = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                                   recording_1.iloc[:, low:upp].values)

    df_joints_distances = pd.DataFrame(joints_distances)
    df_joints_distances["overall"] = df_joints_distances.apply(lambda x: x.sum(), axis=1)
    return df_joints_distances
