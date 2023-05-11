import numpy as np
import pandas as pd
from library.constants import *


def vector_module(vec):
    return np.sqrt(np.sum(np.square(vec), axis=1))


def vector_euclidean(vec_0, vec_1):
    return np.sqrt(np.sum(np.square(vec_0 - vec_1), axis=1))


def get_distances(recording_0, recording_1):
    joints_distances = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low = index * 3
        upp = index * 3 + 3
        distance = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                    recording_1.iloc[:, low:upp].values)
        joints_distances[joint] = distance
    df_joints_distances = pd.DataFrame(joints_distances)
    return df_joints_distances


def get_scores(recording_0, recording_1):
    joints_scores = {}
    for index, joint in enumerate(SIMPLIFIED_JOINTS):
        low = index * 3
        upp = index * 3 + 3
        joint_distance = vector_euclidean(recording_0.iloc[:, low:upp].values,
                                          recording_1.iloc[:, low:upp].values)
        module = vector_module(recording_0.iloc[:, low:upp].values)
        module[module < MINIMUM_VELOCITY] = MINIMUM_VELOCITY
        joints_scores[joint] = joint_distance / module

    df_joints_scores = pd.DataFrame(joints_scores)
    df_joints_scores["Overall"] = df_joints_scores.apply(lambda x: x.sum(), axis=1)
    return df_joints_scores
