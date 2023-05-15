import numpy as np
import pandas as pd
from library.constants import *
from typing import List, Dict, Optional, Union


def vector_module(vec: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(np.square(vec), axis=1))


def vector_euclidean(vec_0: np.ndarray, vec_1: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(np.square(vec_0 - vec_1), axis=1))


def get_distances(recording_0: pd.DataFrame, recording_1: pd.DataFrame) -> pd.DataFrame:
    joints_distances: Dict[str, np.ndarray] = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low: int = index * 3
        upp: int = index * 3 + 3
        distance: np.ndarray = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                                recording_1.iloc[:, low:upp].values)
        joints_distances[joint] = distance
    df_joints_distances: pd.DataFrame = pd.DataFrame(joints_distances)
    return df_joints_distances


def get_scores(recording_0: pd.DataFrame, recording_1: pd.DataFrame, frame_wise_weights: Optional[pd.DataFrame] = None):
    joints_scores: Dict[str, np.ndarray] = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low: int = index * 3
        upp: int = index * 3 + 3
        weights: Union[int, pd.DataFrame]
        if frame_wise_weights is None:
            weights: int = 1
        else:
            weights = frame_wise_weights[joint].astype(float)
        joint_distance: np.ndarray = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                                      recording_1.iloc[:, low:upp].values)
        module: np.ndarray = vector_module(recording_0.iloc[:, low:upp].values)
        module[module < MINIMUM_VELOCITY] = MINIMUM_VELOCITY
        joints_scores[joint] = joint_distance * weights / module

    df_joints_scores = pd.DataFrame(joints_scores)
    df_joints_scores["Overall"] = df_joints_scores.apply(lambda x: x.sum(), axis=1)
    return df_joints_scores


def get_frame_wise_weights(weights_groups: pd.DataFrame, marks: List[int]) -> pd.DataFrame:
    frame_wise_weights:pd.DataFrame = pd.DataFrame(columns=weights_groups.columns)
    for i in range(len(marks) - 1):
        start:int = marks[i]
        end:int = marks[i + 1]
        weights:pd.DataFrame = weights_groups[i:i + 1]
        for frame_number in range(start, end):
            frame_wise_weights:pd.DataFrame = pd.concat([frame_wise_weights, weights], ignore_index=True)
    return frame_wise_weights
