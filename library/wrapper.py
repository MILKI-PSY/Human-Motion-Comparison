import pandas as pd
import library.motion as mt
import numpy as np
import matplotlib.pyplot as plt
from library.animation import Animation, AnimationSetting
from library.constants import *
from typing import List, Dict, Optional, Union
import io
import base64


class AverageScoreImageSetting:
    def __init__(self, flag_to_base64: bool, flag_show: bool):
        self.flag_to_base64 = flag_to_base64
        self.flag_show = flag_show
        self.flag_average_score_image = flag_to_base64 or flag_show


class XlsxSetting:
    def __init__(self, flag_save: bool, output_types: List[str], xlsx_filename: str, save_path: Optional[str] = None):
        self.flag_save = flag_save
        self.flag_xlsx = flag_save
        self.output_types = output_types
        self.xlsx_filename = xlsx_filename
        self.save_path = save_path


class InputSetting:
    def __init__(self, motions_meta: List[mt.MetaData], input_types: List[str]):
        self.motions_meta = motions_meta
        self.input_types = input_types


class Wrapper:
    def __init__(self, xlsx_settings: XlsxSetting, animation_settings: AnimationSetting,
                 average_score_image_settings: AverageScoreImageSetting, motions_meta: List[mt.MetaData]):

        self.xlsx_settings = xlsx_settings
        self.animation_settings = animation_settings
        self.average_score_image_settings = average_score_image_settings
        input_types = self.get_input_types()
        self.input_settings = InputSetting(motions_meta, input_types)
        self.animation: Optional[Animation] = None

    def get_input_types(self) -> List[str]:
        input_types: List[str] = []

        if self.xlsx_settings.flag_xlsx:
            output_types = self.xlsx_settings.output_types.copy()
            if "Score" in output_types:
                output_types.remove("Score")
                output_types.append(RECORDING_FOR_SCORE)
            input_types += output_types

        if self.animation_settings.flag_animation:
            input_types.append(RECORDING_FOR_SKELETON)
            input_types.append(RECORDING_FOR_DTW)
            if self.animation_settings.flag_visualized_vector:
                if self.animation_settings.visualized_vector == "Segment Angular Velocity":
                    input_types.append("Segment Velocity")
                elif self.animation_settings.visualized_vector == "Segment Angular Acceleration":
                    input_types.append("Segment Acceleration")
                else:
                    input_types.append(self.animation_settings.visualized_vector)
            if self.animation_settings.flag_heatmap:
                if self.animation_settings.heatmap_recording == "Score":
                    input_types.append(RECORDING_FOR_SCORE)
                else:
                    input_types.append(self.animation_settings.heatmap_recording)

        input_types = list(set(input_types))
        return input_types

    def get_comparison_types(self) -> List[str]:
        comparison_types: List[str] = []

        if self.xlsx_settings.flag_xlsx:
            comparison_types += self.xlsx_settings.output_types

        if self.animation_settings.flag_animation:
            if self.animation_settings.flag_heatmap:
                comparison_types.append(self.animation_settings.heatmap_recording)

        comparison_types = list(set(comparison_types))
        return comparison_types

    def get_motions(self) -> List[mt.Motion]:
        motions: List[mt.Motion] = []
        current_path: str = ""
        motion_data: Union[Dict[str, pd.DataFrame], pd.DataFrame] = {}
        for meta_data in self.input_settings.motions_meta:
            export_process_information("generating " + meta_data.label + " from " + meta_data.file_path)
            if current_path != meta_data.file_path:
                current_path = meta_data.file_path
                motion_data = pd.read_excel(current_path, sheet_name=self.input_settings.input_types,
                                            usecols=USED_COLUMNS)

            motion_data_cut: Dict[str, pd.DataFrame] = {}
            for recording_type in self.input_settings.input_types:
                if meta_data.start == -1 or meta_data.end == -1:
                    motion_data_cut[recording_type] = motion_data[recording_type]
                    meta_data.start = 0
                    meta_data.end = len(motion_data_cut[recording_type])
                else:
                    motion_data_cut[recording_type] = motion_data[recording_type][meta_data.start:meta_data.end]
            meta_data.recording_types = self.input_settings.input_types
            motions.append(mt.Motion(motion_data_cut, meta_data))

        return motions

    def output(self, motions: List[mt.Motion], result: Dict[str, pd.DataFrame]):
        video: str = ""
        image: str = ""

        if self.xlsx_settings.flag_xlsx:
            if self.xlsx_settings.flag_save:
                self.save_xlsx(result)
        if self.animation_settings.flag_animation:
            ani = Animation(motions, self.animation_settings, result[self.animation_settings.heatmap_recording])
            if self.animation_settings.flag_show:
                ani.show()
            if self.animation_settings.flag_save:
                ani.to_gif()
            if self.animation_settings.flag_to_html5_video:
                video = ani.to_html5_video()
        if self.average_score_image_settings.flag_average_score_image:
            image = self.output_average_score_image(result)
        return video, image

    def save_xlsx(self, result):
        export_process_information("writing the result to the .xlsx file")
        path: str
        if self.xlsx_settings.save_path is not None:
            path = self.xlsx_settings.save_path
        else:
            path = OUTPUT_FOLDER + self.xlsx_settings.xlsx_filename + ".xlsx"
        with pd.ExcelWriter(path) as writer:
            for output_type in self.xlsx_settings.output_types:
                result[output_type].to_excel(writer, sheet_name=output_type, index=False)

    def output_average_score_image(self, result):
        average_score = result["Score"].mean()

        fig, ax = plt.subplots()
        ax.set(xlim=(-0.6, 0.6))
        ax.set(ylim=(-1, 1))
        ax.set_axis_off()
        ax.set_aspect('equal')
        joint_positions: np.ndarray = np.array(list(HEATMAP_JOINT_POSITION.values()))
        average_score_image = ax.scatter(joint_positions[:, 0], joint_positions[:, 1], s=500,
                                         vmin=MINIMUM_SCORE, vmax=MAXIMUM_SCORE,
                                         c=np.zeros(len(HEATMAP_JOINT_POSITION)), cmap=COLOR_MAP)
        average_score_image.set_array(average_score)

        for joint in SIMPLIFIED_JOINTS:
            position = HEATMAP_JOINT_POSITION[joint]

            ax.text(position[0], position[1], s=round(average_score[joint], 2))

        if self.average_score_image_settings.flag_show:
            plt.show()
        if self.average_score_image_settings.flag_to_base64:
            io_bytes = io.BytesIO()
            fig.savefig(io_bytes, format='jpg')
            io_bytes.seek(0)
            return base64.b64encode(io_bytes.read()).decode()


def export_process_information(info: str) -> None:
    if DEBUG_INFO:
        print(info)
