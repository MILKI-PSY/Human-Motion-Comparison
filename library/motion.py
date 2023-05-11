import numpy as np
import pandas as pd
from dtw import *
from scipy.spatial.distance import euclidean
from library.constants import *
from library.comparison import *
from typing import List, Dict


class MetaData:
    def __init__(self, file_name: str, start: int, end: int, label: str,
                 recording_types: List[str] = RECORDING_TYPES) -> None:
        self.file_name = file_name
        self.start = start
        self.end = end
        self.label = label
        self.recording_types = recording_types


class Motion:
    recordings: Dict[str, pd.DataFrame]
    meta: MetaData

    def __init__(self, recordings: Dict[str, pd.DataFrame], meta: MetaData) -> None:
        self.recordings = recordings
        self.meta = meta

    def __len__(self) -> int:
        return self.meta.end - self.meta.start

    def __gt__(self, other) -> bool:
        return len(self) > len(other)

    def centre(self) -> "Motion":
        need_centre_recordings = set(self.meta.recording_types).intersection(NEED_CENTRE_RECORDING_TYPES)
        for recording_name in need_centre_recordings:
            if DEBUG_INFO: print("placing " + self.meta.label + " in the centre")
            recording = self.recordings[recording_name]
            columns = recording.columns
            columns_with_x = columns[columns.str.contains("x")]
            columns_with_y = columns[columns.str.contains("y")]
            columns_with_z = columns[columns.str.contains("z")]
            recording[columns_with_x] = recording[columns_with_x].sub(recording["Pelvis x"], axis='index')
            recording[columns_with_y] = recording[columns_with_y].sub(recording["Pelvis y"], axis='index')
            recording[columns_with_z] = recording[columns_with_z].sub(recording["Pelvis z"], axis='index')

        return self

    def confront(self) -> "Motion":
        def rotate(frame: pd.Series, sin: float, cos: float):
            rotation_matrix = np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])
            for joint in SIMPLIFIED_JOINTS:
                frame[[joint + " x", joint + " y", joint + " z"]] \
                    = np.dot(rotation_matrix, frame[[joint + " x", joint + " y", joint + " z"]]).T
            return frame

        if DEBUG_INFO: print("rotating " + self.meta.label + " to positive direction")

        need_confront_recordings = set(self.recordings.keys()).intersection(NEED_CONFRONT_RECORDING_TYPES)
        if need_confront_recordings:
            position_recording = self.recordings[RECORDING_FOR_SKELETON]
            opposite = position_recording["Left Upper Arm y"] - position_recording["Right Upper Arm y"]
            adjacent = position_recording["Left Upper Arm x"] - position_recording["Right Upper Arm x"]
            hypotenuse = np.sqrt(np.square(opposite) + np.square(adjacent))
            series_sin = opposite / hypotenuse
            series_cos = adjacent / hypotenuse

        for recording_name in need_confront_recordings:
            recording = self.recordings[recording_name]
            recording[recording.columns] = recording.apply(lambda x: rotate(x, series_sin[x.name], series_cos[x.name]),
                                                           axis=1, result_type="expand")
        return self

    def synchronized_by(self, reference_motion: "Motion", weights_groups: pd.DataFrame, marks: List[int]) -> "Motion":
        def frame_distance(frame_0: np.ndarray, frame_1: np.ndarray) -> float:
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

        if DEBUG_INFO: print("synchronizing " + self.meta.label + " by " + reference_motion.meta.label)

        reference_recording = reference_motion.recordings[RECORDING_FOR_SKELETON]
        self_recording = self.recordings[RECORDING_FOR_SKELETON]

        reference_recording["frame_number"] = reference_recording.index
        self_recording["frame_number"] = self_recording.index
        alignment = dtw(reference_recording, self_recording, dist_method=frame_distance)

        synchronized_recordings = {}
        columns = self_recording.columns
        for recording_name in self.recordings.keys():
            synchronized_recordings[recording_name] = pd.DataFrame(columns=columns)

        reference_time = -1
        for step in range(len(alignment.index1)):
            index_1 = alignment.index1[step]
            index_2 = alignment.index2[step]
            if reference_time != index_1:
                reference_time = index_1
                for recording_name in self.recordings.keys():
                    synchronized_recordings[recording_name] = pd.concat(
                        [synchronized_recordings[recording_name],
                         self.recordings[recording_name][index_2: index_2 + 1][:]
                         ], ignore_index=True)
        self.recordings = synchronized_recordings

        return self

    def get_body_size(self) -> Dict[str, float]:
        frame = self.recordings[RECORDING_FOR_SKELETON][0:1]  # because the body size wouldn't change
        body_size = {}
        for joint_connection in SKELETON_CONNECTION_MAP:
            columns = []
            for joint in joint_connection:
                columns_for_joint = []
                for axis in AXIS:
                    columns_for_joint.append(joint + axis)
                columns.append(columns_for_joint)
            body_size[joint_connection[0]] = vector_euclidean(frame[columns[0]].values, frame[columns[1]].values)
        return body_size

    def get_angular_vector(self, recording_name: str) -> pd.DataFrame:
        body_size = self.get_body_size()
        original_recording = VECTORS_ANGULATION_MAP[recording_name]
        vector = self.recordings[original_recording]
        angular_vector = pd.DataFrame()
        for joint_connection in SKELETON_CONNECTION_MAP:
            endpoint_0 = joint_connection[0]
            endpoint_1 = joint_connection[1]
            for axis in AXIS:
                key = (joint_connection[0], joint_connection[1], axis)
                angular_vector[key] = (vector[endpoint_1 + axis] - vector[endpoint_0 + axis]) / body_size[endpoint_0]
        return angular_vector
