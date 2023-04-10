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

HEATMAP_JOINT_POSITION = [[0.7, 0.7, 0.8],  # Head
                          [0.5, 0.7, 0.6],  # Right Upper Arm
                          [0.7, 0.7, 0.6],  # Neck
                          [0.9, 0.7, 0.6],  # Left Upper Arm
                          [0.5, 0.7, 0.3],  # Right Forearm
                          [0.9, 0.7, 0.3],  # Left Forearm
                          [0.6, 0.7, 0.1],  # Right Upper Leg
                          [0.7, 0.7, 0.1],  # Pelvis
                          [0.8, 0.7, 0.1],  # Left Upper Leg
                          [0.5, 0.7, 0.0],  # Right Hand
                          [0.9, 0.7, 0.0],  # Left Hand
                          [0.6, 0.7, -0.4],  # Right Lower Leg
                          [0.8, 0.7, -0.4],  # Left Lower Leg
                          [0.6, 0.7, -0.8],  # Right Foot
                          [0.8, 0.7, -0.8],  # Left Foot
                          ]
