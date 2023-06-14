from environs import Env

env = Env()
env.read_env()

OUTPUT_FOLDER = env.str('OUTPUT_FOLDER')
INPUT_FOLDER = env.str('INPUT_FOLDER')

RECORDING_TYPES = env.json('RECORDING_TYPES')
NEED_CONFRONT_RECORDING_TYPES = env.json('NEED_CONFRONT_RECORDING_TYPES')
NEED_CENTRE_RECORDING_TYPES = env.json('NEED_CENTRE_RECORDING_TYPES')
NEED_ANGULATION_BEFORE_VISUALIZATION = env.json('NEED_ANGULATION_BEFORE_VISUALIZATION')

RECORDING_FOR_SKELETON = env.str('RECORDING_FOR_SKELETON')
RECORDING_FOR_SCORE = env.str('RECORDING_FOR_SCORE')

DEBUG_INFO = env.bool('DEBUG_INFO')
MINIMUM_VELOCITY = env.int('MINIMUM_VELOCITY')
MINIMUM_SCORE = env.int('MINIMUM_SCORE')
MAXIMUM_SCORE = env.int('MAXIMUM_SCORE')
COLOR_MAP = env.str('COLOR_MAP')

GIF_WRITER = env.str('GIF_WRITER')
GIF_FPS = env.int('GIF_FPS')

AXIS = env.json('AXIS')
VECTORS_ANGULATION_MAP = env.json('VECTORS_ANGULATION_MAP')
SIMPLIFIED_JOINTS = env.json('SIMPLIFIED_JOINTS')

USED_COLUMNS = ["Frame"]
for joints in SIMPLIFIED_JOINTS:
    for axis in AXIS:
        USED_COLUMNS.append(joints + axis)

SKELETON_CONNECTION_MAP = env.json('SKELETON_CONNECTION_MAP')

HEATMAP_JOINT_POSITION = env.json('HEATMAP_JOINT_POSITION')

weights_badminton_service = {}
for joint in SIMPLIFIED_JOINTS:
    weights_badminton_service[joint] = 0.3
weights_badminton_service["Right Hand"] = 1
weights_badminton_service["Right Upper Arm"] = 1
weights_badminton_service["Right Forearm"] = 1
marks_badminton_service = [0, 250]
dict_badminton_service = {
    "weights": [weights_badminton_service],
    "marks": marks_badminton_service
}

DEFAULT_WEIGHTS = {
    "Badminton Service": dict_badminton_service
}
