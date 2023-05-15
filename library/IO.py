import pandas as pd
import library.motion as mt
import comparison as cp
from constants import *
from typing import List, Dict


def get_motions(motions_meta: List[mt.MetaData], input_types: List[str]) -> List[mt.Motion]:
    motions: List[mt.Motion] = []
    current_file: str = ""
    motion_data: Dict[str, pd.DataFrame] = {}
    for meta_data in motions_meta:
        if DEBUG_INFO: print("generating " + meta_data.label + " from " + meta_data.file_name)
        if current_file != meta_data.file_name:
            current_file = meta_data.file_name
            all_path: str = INPUT_FOLDER + meta_data.file_name + "\\data.xlsx"
            motion_data = pd.read_excel(all_path, sheet_name=input_types, usecols=USED_COLUMNS)

        motion_data_cut: Dict[str, pd.DataFrame] = {}
        for recording_type in input_types:
            motion_data_cut[recording_type] = motion_data[recording_type][meta_data.start:meta_data.end]
        motions.append(mt.Motion(motion_data_cut, meta_data))

    return motions


def export_distances(motions: List[mt.Motion], output_types: List[str], frame_wise_wights: pd.DataFrame) -> None:
    if len(motions) != 2:
        raise Exception("In order to calculate the distance to the output, the motions length must be 2")
    result: Dict[str, pd.DataFrame] = {}
    for output_type in output_types:
        if output_type == "Score":
            if DEBUG_INFO: print("calculating the Score")
            result["Score"] = cp.get_scores(motions[0].recordings[RECORDING_FOR_SCORE],
                                         motions[1].recordings[RECORDING_FOR_SCORE], frame_wise_wights)
        else:
            if DEBUG_INFO: print("calculating the distance of " + output_type)
            result[output_type] = cp.get_distances(motions[0].recordings[output_type],
                                                motions[1].recordings[output_type])

    if DEBUG_INFO: print("writing the result to the out.xlsx")
    all_path: str = OUTPUT_FOLDER + motions[0].meta.label + "_" + motions[1].meta.label + ".xlsx"
    with pd.ExcelWriter(all_path) as writer:
        for output_type in output_types:
            result[output_type].to_excel(writer, sheet_name=output_type, index=False)

# def get_recording_types(output_types: List[str], animation_settings: anmtn.Setting) -> List[str]:
#     input_types: List[str] = []
#
#     if output_types is not None:
#         input_types = output_types
#         if "Score" in output_types:
#             input_types.remove("Score")
#             if RECORDING_FOR_SCORE not in input_types:
#                 input_types.append(RECORDING_FOR_SCORE)
#
#     if animation_settings is not None:
#         if animation_settings.flag_visualized_vector and animation_settings.visualized_vector not in input_types:
#             input_types.append(animation_settings.visualized_vector)
#         if animation_settings.flag_heatmap and animation_settings.heatmap_recording not in input_types:
#             if animation_settings.heatmap_recording == "Score":
#                 input_types.append(RECORDING_FOR_SCORE)
#             else:
#                 input_types.append(animation_settings.heatmap_recording)
#
#     if RECORDING_FOR_SKELETON not in input_types:
#         input_types.append(RECORDING_FOR_SKELETON)
#
#     return input_types
