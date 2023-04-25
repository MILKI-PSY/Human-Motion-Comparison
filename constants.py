import matplotlib.colors as mcolors

ANIMATION_SAVE_PATH = "C:\\Users\\gaoch\\MA\\Saved\\"
DATA_PATH = "C:\\Users\\gaoch\\MA\\Data\\"

POSITION_RECORDING_NAME = "Segment Position"
VELOCITY_RECORDING_NAME = "Segment Angular Velocity"
SHEET_NAMES = [POSITION_RECORDING_NAME, VELOCITY_RECORDING_NAME]

DEBUG_INFO = True
MINIMUM_VELOCITY = 1
MINIMUM_SCORE = 0
MAXIMUM_SCORE = 2
COLOR_MAP = "Reds"

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

HEATMAP_JOINT_POSITION = [[0.0, 0.1],  # Pelvis
                          [0.0, 0.6],  # Neck
                          [0.0, 0.8],  # Head
                          [-0.2, 0.6],  # Right Upper Arm
                          [-0.3, 0.3],  # Right Forearm
                          [-0.4, 0.0],  # Right Hand
                          [0.2, 0.6],  # Left Upper Arm
                          [0.3, 0.3],  # Left Forearm
                          [0.4, 0.0],  # Left Hand
                          [-0.1, 0.1],  # Right Upper Leg
                          [-0.1, -0.4],  # Right Lower Leg
                          [-0.1, -0.8],  # Right Foot
                          [0.1, 0.1],  # Left Upper Leg
                          [0.1, -0.4],  # Left Lower Leg
                          [0.1, -0.8],  # Left Foot
                          ]

COLOR_POOL = list(mcolors.BASE_COLORS.values())
