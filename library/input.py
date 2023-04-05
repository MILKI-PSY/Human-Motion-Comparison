from constants import *


def get_joints_cols():
    used_cols = []
    for joints in SIMPLIFIED_JOINTS:
        used_cols.append(joints+" x")
        used_cols.append(joints+" y")
        used_cols.append(joints+" z")
    return used_cols


# motion_recording = pd.read_excel(DATA_PATH + "P01_B_noweightwithgloves.xlsx",
#                          sheet_name = SHEET_NAME,
#                          usecols = used_cols)