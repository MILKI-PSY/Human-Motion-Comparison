import numpy as np
import pandas as pd
from dtw import *
from scipy.spatial.distance import euclidean
from constants import *


class Motion:
    def __init__(self, position_recording, velocity_recording=None, label="No Label"):
        self.position_recording = position_recording
        self.velocity_recording = velocity_recording
        self.label = label

    def __len__(self):
        return len(self.position_recording)

    def __gt__(self, other):
        return len(self) > len(other)

    def centre(self):
        if DEBUG_INFO: print("start placing " + self.label + " in the centre")
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

        if DEBUG_INFO: print("start rotating " + self.label + " to positive direction")
        opposite = self.position_recording["Left Upper Arm y"] - self.position_recording["Right Upper Arm y"]
        adjacent = self.position_recording["Left Upper Arm x"] - self.position_recording["Right Upper Arm x"]
        hypotenuse = np.sqrt(np.square(opposite) + np.square(adjacent))
        series_sin = opposite / hypotenuse
        series_cos = adjacent / hypotenuse

        self.position_recording[self.position_recording.columns] = self.position_recording.apply(
            lambda x: rotate(x, series_sin[x.name], series_cos[x.name]), axis=1, result_type="expand")

        return self

    def synchronized_by(self, reference_motion, weights_groups, marks):
        def frame_distance(frame_0, frame_1):
            # choose the right weights from weights_groups
            weights = None
            frame_number = frame_0[-1]  # the "frame_number" column is new added
            for i in range(len(marks)):
                if marks[i] >= frame_number:
                    weights = weights_groups.iloc[i - 1]  # -1 because weights have the same index with the start mark
                    break

            # calculate the distance
            distance = 0
            # step = 3, because 3 columns (x, y, z) for a joint, -1 because the new "frame_number" column
            for i in range(0, len(frame_0) - 1, 3):
                distance += weights[SIMPLIFIED_JOINTS[int(i / 3)]] * euclidean(frame_0[i:i + 3], frame_1[i:i + 3])
            return distance

        if DEBUG_INFO: print("start synchronizing " + self.label + " by " + reference_motion.label)

        reference_motion.position_recording["frame_number"] = reference_motion.position_recording.index
        self.position_recording["frame_number"] = self.position_recording.index
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
        return Motion(synchronized_position_recording, synchronized_velocity_recording, self.label)


def get_scores(motion_0, motion_1):
    def vector_euclidean(vec_0, vec_1):
        return np.sqrt(np.sum(np.square(vec_0 - vec_1), axis=1))

    def vector_module(vec):
        return np.sqrt(np.sum(np.square(vec), axis=1))

    if DEBUG_INFO: print("start calculating the score of " + motion_0.label + " and " + motion_1.label)

    recording_0 = motion_0.velocity_recording
    recording_1 = motion_1.velocity_recording
    joints_scores = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low = index * 3
        upp = index * 3 + 3
        joint_distance = vector_euclidean(recording_0.iloc[:, low:upp].values, recording_1.iloc[:, low:upp].values)
        module = vector_module(recording_0.iloc[:, low:upp].values)
        module[module < MINIMUM_VELOCITY] = MINIMUM_VELOCITY
        joints_scores[joint] = joint_distance / module

    df_joints_scores = pd.DataFrame(joints_scores)
    df_joints_scores["overall"] = df_joints_scores.apply(lambda x: x.sum(), axis=1)
    return df_joints_scores
