import numpy as np
import pandas as pd
import math


DATA_PATH = "C:\\Users\\gaoch\\MA\\Badminton weights\\P01_B\\"

SHEET_NAME = ["Segment Angular Velocity"]

SIMPLIFIED_JOINTS = ["Head", "Neck", "Left Upper Arm", "Right Upper Arm", "Left Forearm", "Right Forearm",
                     "Left Hand", "Right Hand", "Pelvis", "Left Upper Leg", "Right Upper Leg",
                     "Left Lower Leg", "Right Lower Leg", "Left Foot", "Right Foot"]

SKELETON_CONNECTION_MAP = [["Head", "Neck"],
                         ["Neck", "Left Upper Arm"],
                         ["Left Upper Arm", "Left Forearm"],
                         ["Left Forearm", "Left Hand"],
                         ["Neck", "Right Upper Arm"],
                         ["Right Upper Arm", "Right Forearm"],
                         ["Right Forearm", "Right Hand"],
                         ["Neck", "Pelvis"],
                         ["Pelvis", "Left Upper Leg"],
                         ["Left Upper Leg", "Left Lower Leg"],
                         ["Left Lower Leg", "Left Foot"],
                         ["Pelvis", "Right Upper Leg"],
                         ["Right Upper Leg", "Right Lower Leg"],
                         ["Right Lower Leg", "Right Foot"]]

used_cols = []
for joints in SIMPLIFIED_JOINTS:
    used_cols.append(joints+" x")
    used_cols.append(joints+" y")
    used_cols.append(joints+" z")

def read_data(file_name):
    return pd.read_excel(DATA_PATH + file_name,
                         sheet_name = SHEET_NAME,
                         usecols = used_cols)


motion_recording = read_data("P01_B_noweightwithgloves.xlsx")

motion_recording = motion_recording[5000:10000]
motion_recording.to_csv("angular velocity", index = False)