ANIMATION_SAVE_PATH = "C:\\Users\\gaoch\\MA\\Badminton weights\\gifs\\"

SIMPLIFIED_JOINTS = ["Pelvis", "Neck", "Head", "Right Upper Arm", "Right Forearm",
                     "Right Hand", "Left Upper Arm", "Left Forearm", "Left Hand",
                     "Right Upper Leg", "Right Lower Leg", "Right Foot", "Left Upper Leg",
                     "Left Lower Leg", "Left Foot"]


SKELETON_CONNECTION_MAP = [["Neck", "Head"],
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
