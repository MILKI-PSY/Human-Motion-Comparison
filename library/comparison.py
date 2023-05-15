import numpy as np
import pandas as pd
import library.motion as mt
from library.constants import *
from typing import List, Dict


class Comparison:
    def __init__(self, weights_groups: pd.DataFrame, marks: List[int]):
        self.frame_wise_weights: pd.DataFrame = pd.DataFrame(columns=weights_groups.columns)
        for i in range(len(marks) - 1):
            start: int = marks[i]
            end: int = marks[i + 1]
            weights: pd.DataFrame = weights_groups[i:i + 1]
            for frame_number in range(start, end):
                self.frame_wise_weights: pd.DataFrame = pd.concat([self.frame_wise_weights, weights], ignore_index=True)

    def compare(self, motion_0: mt.Motion, motion_1: mt.Motion, comparison_types: str) -> Dict[str, pd.DataFrame]:
        if DEBUG_INFO: print("calculating the distances and score")
        result: Dict[str, pd.DataFrame] = {}
        for output_type in comparison_types:
            joints_distances: Dict[str, np.ndarray] = {}
            for index, joint in enumerate(SIMPLIFIED_JOINTS):
                low: int = index * 3
                upp: int = index * 3 + 3
                if output_type == "Score":
                    weights: pd.DataFrame = self.frame_wise_weights[joint].astype(float)
                    recording_0 = motion_0.recordings[RECORDING_FOR_SCORE]
                    recording_1 = motion_1.recordings[RECORDING_FOR_SCORE]
                    joint_distance: np.ndarray = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                                                  recording_1.iloc[:, low:upp].values)
                    module: np.ndarray = vector_module(recording_0.iloc[:, low:upp].values)
                    module[module < MINIMUM_VELOCITY] = MINIMUM_VELOCITY
                    joints_distances[joint] = joint_distance * weights / module
                else:
                    recording_0 = motion_0.recordings[output_type]
                    recording_1 = motion_1.recordings[output_type]
                    distance: np.ndarray = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                                            recording_1.iloc[:, low:upp].values)
                    joints_distances[joint] = distance
            result[output_type] = pd.DataFrame(joints_distances)
        return result


def vector_module(vec: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(np.square(vec), axis=1))


def vector_euclidean(vec_0: np.ndarray, vec_1: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(np.square(vec_0 - vec_1), axis=1))
