import numpy as np
import pandas as pd
from library.constants import *
from dtw import dtw, DTW
from scipy.spatial.distance import euclidean
from typing import List, Dict, Set, Optional


class MetaData:
    def __init__(self, file_name: str, start: int, end: int, label: str, file_path: Optional[str] = None) -> None:
        self.file_name = file_name
        self.start = start
        self.end = end
        self.label = label
        self.file_path = file_path
        self.recording_types: List[str]


class Motion:
    def __init__(self, recordings: Dict[str, pd.DataFrame], meta: MetaData) -> None:
        self.recordings = recordings
        self.meta = meta

    def __len__(self) -> int:
        return len(self.recordings[RECORDING_FOR_SKELETON])

    def __gt__(self, other) -> bool:
        return len(self) > len(other)

    def centre(self) -> 'Motion':
        need_centre_recordings: Set[str] = set(self.meta.recording_types).intersection(
            NEED_CENTRE_RECORDING_TYPES)
        for recording_name in need_centre_recordings:
            if DEBUG_INFO: print("placing " + self.meta.label + " in the centre")
            recording: pd.DataFrame = self.recordings[recording_name]
            columns: pd.Index = recording.columns
            columns_with_x: pd.Index = columns[columns.str.contains("x")]
            columns_with_y: pd.Index = columns[columns.str.contains("y")]
            columns_with_z: pd.Index = columns[columns.str.contains("z")]
            recording[columns_with_x]: pd.DataFrame = recording[columns_with_x].sub(recording["Pelvis x"], axis='index')
            recording[columns_with_y]: pd.DataFrame = recording[columns_with_y].sub(recording["Pelvis y"], axis='index')
            recording[columns_with_z]: pd.DataFrame = recording[columns_with_z].sub(recording["Pelvis z"], axis='index')

        return self

    def confront(self) -> 'Motion':
        def rotate(frame: pd.Series, sin: float, cos: float) -> pd.Series:
            rotation_matrix: np.ndarray = np.array([[cos, sin, 0], [-sin, cos, 0], [0, 0, 1]])
            for joint in SIMPLIFIED_JOINTS:
                frame[[joint + " x", joint + " y", joint + " z"]] \
                    = np.dot(rotation_matrix, frame[[joint + " x", joint + " y", joint + " z"]]).T
            return frame

        if DEBUG_INFO: print("rotating " + self.meta.label + " to positive direction")

        need_confront_recordings: Set[str] = set(self.recordings.keys()).intersection(NEED_CONFRONT_RECORDING_TYPES)
        if need_confront_recordings:
            position_recording: pd.DataFrame = self.recordings[RECORDING_FOR_SKELETON]
            opposite: pd.DataFrame = position_recording["Left Upper Arm y"] - position_recording["Right Upper Arm y"]
            adjacent: pd.DataFrame = position_recording["Left Upper Arm x"] - position_recording["Right Upper Arm x"]
            hypotenuse: pd.DataFrame = np.sqrt(np.square(opposite) + np.square(adjacent))
            series_sin: pd.DataFrame = opposite / hypotenuse
            series_cos: pd.DataFrame = adjacent / hypotenuse

        for recording_name in need_confront_recordings:
            recording: pd.DataFrame = self.recordings[recording_name]
            recording[recording.columns] = recording.apply(lambda x: rotate(x, series_sin[x.name], series_cos[x.name]),
                                                           axis=1, result_type="expand")
        return self

    def synchronized_by(self, reference_motion: "Motion") -> 'Motion':
        def frame_distance(frame_0: np.ndarray, frame_1: np.ndarray) -> float:
            distance: float = 0.0
            for i in range(1, len(frame_0), len(AXIS)):  # first column is "Frame"
                distance += euclidean(frame_0[i:i + 3], frame_1[i:i + 3])
            return distance

        if DEBUG_INFO: print("synchronizing " + self.meta.label + " by " + reference_motion.meta.label)

        reference_recording: pd.DataFrame = reference_motion.recordings[RECORDING_FOR_SKELETON]
        self_recording: pd.DataFrame = self.recordings[RECORDING_FOR_SKELETON]

        alignment: DTW = dtw(reference_recording, self_recording, dist_method=frame_distance)

        synchronized_recordings = {}
        columns = self_recording.columns
        for recording_name in self.recordings.keys():
            synchronized_recordings[recording_name] = pd.DataFrame(columns=columns)

        reference_time: int = -1
        for step in range(len(alignment.index1)):
            index_1: int = alignment.index1[step]
            index_2: int = alignment.index2[step]
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
        frame: pd.Series = self.recordings[RECORDING_FOR_SKELETON].iloc[0]  # because the body size wouldn't change
        body_size: Dict[str, float] = {}
        for joint_connection in SKELETON_CONNECTION_MAP:
            columns: List[List[str]] = []
            for joint in joint_connection:
                columns_for_joint: List[str] = []
                for axis in AXIS:
                    columns_for_joint.append(joint + axis)
                columns.append(columns_for_joint)
            body_size[joint_connection[0]] = euclidean(frame[columns[0]], frame[columns[1]])
        return body_size

    def get_angular_vector(self, recording_name: str) -> pd.DataFrame:
        body_size: Dict[str, float] = self.get_body_size()
        original_recording: str = VECTORS_ANGULATION_MAP[recording_name]
        vector: pd.DataFrame = self.recordings[original_recording]
        angular_vector: pd.DataFrame = pd.DataFrame()
        for joint_connection in SKELETON_CONNECTION_MAP:
            endpoint_0: str = joint_connection[0]
            endpoint_1: str = joint_connection[1]
            for axis in AXIS:
                key: tuple[str, str, str] = (joint_connection[0], joint_connection[1], axis)
                angular_vector[key] = (vector[endpoint_1 + axis] - vector[endpoint_0 + axis]) / body_size[endpoint_0]
        return angular_vector
