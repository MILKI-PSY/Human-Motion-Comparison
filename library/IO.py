import pandas as pd
import library.motion as mt
from library.animation import Animation, AnimationSetting
from library.constants import *
from typing import List, Dict, Optional, Union


class XlsxSetting:
    def __init__(self, output_types: List[str], xlsx_filename: str):
        self.output_types = output_types
        self.xlsx_filename = xlsx_filename


class InputSetting:
    def __init__(self, motions_meta: List[mt.MetaData], input_types: List[str]):
        self.motions_meta = motions_meta
        self.input_types = input_types


class MyIO:
    def __init__(self, flag_output_xlsx: bool, flag_show_animation: bool, flag_output_gif: bool,
                 xlsx_settings: Optional[XlsxSetting], animation_settings: Optional[AnimationSetting],
                 motions_meta: List[mt.MetaData]):
        self.flag_output_xlsx = flag_output_xlsx
        if self.flag_output_xlsx:
            if xlsx_settings is None:
                raise Exception("Without Xlsx Setting")
            else:
                self.xlsx_settings = xlsx_settings
        self.flag_output_gif = flag_output_gif
        self.flag_show_animation = flag_show_animation
        if self.flag_output_gif or self.flag_show_animation:
            if animation_settings is None:
                raise Exception("Without Gif Setting")
            else:
                self.animation_settings = animation_settings
        input_types = self.get_input_types()
        self.input_settings = InputSetting(motions_meta, input_types)
        self.animation: Optional[Animation] = None

    def get_input_types(self) -> List[str]:
        input_types: List[str] = []

        if self.flag_output_xlsx:
            output_types = self.xlsx_settings.output_types
            if "Score" in output_types:
                output_types.remove("Score")
                output_types.append(RECORDING_FOR_SCORE)
            input_types += output_types

        if self.flag_show_animation or self.flag_output_gif:
            input_types.append(RECORDING_FOR_SKELETON)
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

        if self.flag_output_xlsx:
            comparison_types += self.xlsx_settings.output_types

        if self.flag_show_animation or self.flag_output_gif:
            if self.animation_settings.flag_heatmap:
                comparison_types.append(self.animation_settings.heatmap_recording)

        comparison_types = list(set(comparison_types))
        return comparison_types

    def get_motions(self) -> List[mt.Motion]:
        motions: List[mt.Motion] = []
        current_file: str = ""
        motion_data: Union[Dict[str, pd.DataFrame], pd.DataFrame] = {}
        for meta_data in self.input_settings.motions_meta:
            export_process_information("generating " + meta_data.label + " from " + meta_data.file_name)
            if current_file != meta_data.file_name:
                current_file = meta_data.file_name
                if meta_data.file_path is not None:
                    all_path = meta_data.file_path
                else:
                    all_path: str = RECORDINGS_FOLDER + meta_data.file_name + "\\data.xlsx"
                motion_data = pd.read_excel(all_path, sheet_name=self.input_settings.input_types, usecols=USED_COLUMNS)

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
        if self.flag_output_xlsx:
            self.output_xlsx(result)
        if self.flag_show_animation or self.flag_output_gif:
            ani = Animation(motions, self.animation_settings, result[self.animation_settings.heatmap_recording])
            if self.flag_show_animation:
                ani.show()
            if self.flag_output_gif:
                ani.to_gif()

    def output_xlsx(self, result):
        export_process_information("writing the result to the out.xlsx")
        all_path: str = OUTPUT_FOLDER + self.xlsx_settings.xlsx_filename + ".xlsx"
        with pd.ExcelWriter(all_path) as writer:
            for output_type in self.xlsx_settings.output_types:
                result[output_type].to_excel(writer, sheet_name=output_type, index=False)

    def output_web(self, motions: List[mt.Motion], result: Dict[str, pd.DataFrame]):
        ani = Animation(motions, self.animation_settings, result[self.animation_settings.heatmap_recording])
        return ani.to_html5_video()


def export_process_information(info: str) -> None:
    if DEBUG_INFO:
        print(info)

