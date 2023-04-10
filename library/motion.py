import numpy as np
import pandas as pd
import math
from dtw import *
from scipy.spatial.distance import euclidean
from constants import *


class Motion:
    def __init__(self, position_recording, velocity_recording=None, label="No Label"):
        self.position_recording = position_recording
        self.velocity_recording = velocity_recording
        self.label = label
        self.rotation_parameters = self.get_rotation_parameters()
        self.weights = {}
        for joint in SIMPLIFIED_JOINTS:
            self.weights[joint] = 1

    def __len__(self):
        return len(self.position_recording)

    def __gt__(self, other):
        return len(self) > len(other)

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

    def centre(self):
        columns_with_x = self.position_recording.columns[self.position_recording.columns.str.contains("x")]
        columns_with_y = self.position_recording.columns[self.position_recording.columns.str.contains("y")]
        columns_with_z = self.position_recording.columns[self.position_recording.columns.str.contains("z")]
        self.position_recording[columns_with_x] = self.position_recording[columns_with_x].sub(
            self.position_recording["Pelvis x"], axis='index')
        self.position_recording[columns_with_y] = self.position_recording[columns_with_y].sub(
            self.position_recording["Pelvis y"], axis='index')
        self.position_recording[columns_with_z] = self.position_recording[columns_with_z].sub(
            self.position_recording["Pelvis z"], axis='index')
        return self

    def confront(self):
        def rotate(frame, sin, cos):
            rotation_matrix = np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])
            for joint in SIMPLIFIED_JOINTS:
                frame[[joint + " x", joint + " y", joint + " z"]] \
                    = np.dot(rotation_matrix, frame[[joint + " x", joint + " y", joint + " z"]]).T
            return frame

        series_sin = self.rotation_parameters["sin"]
        series_cos = self.rotation_parameters["cos"]
        self.position_recording[self.position_recording.columns] = self.position_recording.apply(
            lambda x: rotate(x, series_sin[x.name], series_cos[x.name]), axis=1, result_type="expand")

    def synchronized_by(self, reference_motion):
        def frame_distance(frame_0, frame_1):
            distance = 0
            for i in range(0, len(frame_0), 3):  # step = 3, because 3 columns (x, y, z) for a joint
                distance += self.weights[SIMPLIFIED_JOINTS[int(i / 3)]] * euclidean(frame_0[i:i + 3], frame_1[i:i + 3])
            return distance

        alignment = dtw(reference_motion.position_recording, self.position_recording, dist_method=frame_distance)
        synchronized_position_recording = pd.DataFrame(columns=self.position_recording.columns)
        synchronized_velocity_recording = pd.DataFrame(columns=self.velocity_recording.columns)
        i = -1
        for step in range(len(alignment.index1)):
            if i != alignment.index1[step]:
                i = alignment.index1[step]
                synchronized_position_recording = pd.concat(
                    [synchronized_position_recording,
                     self.position_recording.iloc[alignment.index2[step]].to_frame().T], ignore_index=True)
                synchronized_velocity_recording = pd.concat(
                    [synchronized_velocity_recording,
                     self.velocity_recording.iloc[alignment.index2[step]].to_frame().T], ignore_index=True)
        return Motion(synchronized_position_recording, velocity_recording=synchronized_velocity_recording)


def get_scores(motion_0, motion_1):
    def vector_euclidean(arr_0, arr_1):
        return np.sqrt(np.sum(np.square(arr_0 - arr_1), axis=1))

    recording_0 = motion_0.velocity_recording
    recording_1 = motion_1.velocity_recording

    joints_distances = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low = index * 3
        upp = index * 3 + 3
        joints_distances[joint] = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                                   recording_1.iloc[:, low:upp].values)

    df_joints_distances = pd.DataFrame(joints_distances)
    df_joints_distances["overall"] = df_joints_distances.apply(lambda x: x.sum(), axis=1)
    return df_joints_distances
