import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation
import comparison as cp
import motion as mt
from constants import *
from typing import List, Generator, Tuple, Dict, Optional, Union

Color = Tuple[float, float, float]
Color_generator = Generator[Color, None, None]


class Character:
    def __init__(self, motion: mt.Motion, axes: plt.Axes, visualized_vector: str,
                 color_generator: Color_generator) -> None:

        self.position_recording = motion.recordings[RECORDING_FOR_SKELETON]
        if visualized_vector in NEED_ANGULATION_BEFORE_VISUALIZATION:
            self.visualized_vector = motion.get_angular_vector(visualized_vector)
            self.visualized_vector_key_type = "Tuple"
        else:
            self.visualized_vector = motion.recordings[visualized_vector]
            self.visualized_vector_key_type = "str"
        color: Color
        color = next(color_generator)
        self.skeleton = [axes.plot([], [], [], c=color)[0] for _ in SKELETON_CONNECTION_MAP]
        self.skeleton[0].set_label(motion.meta.label)  # the whole skeleton is the same color, so one label is enough
        color = next(color_generator)
        self.visualized_vectors = [axes.plot([], [], [], c=color)[0] for _ in SIMPLIFIED_JOINTS]

    def __len__(self) -> int:
        return len(self.position_recording)


class Setting:
    def __init__(self, flag_visualized_vector: bool = False, flag_heatmap: bool = False, flag_repeat: bool = True,
                 visualized_vector: str = "Segment Velocity", heatmap_recording: str = "Score",
                 frame_wise_weights: Optional[pd.DataFrame] = None):
        self.flag_visualized_vector = flag_visualized_vector
        self.flag_heatmap = flag_heatmap
        self.flag_repeat = flag_repeat
        self.visualized_vector = visualized_vector
        self.heatmap_recording = heatmap_recording
        self.frame_wise_weights = frame_wise_weights


class Animation:
    def __init__(self, motions: List[mt.Motion], setting: Setting) -> None:
        self.is_paused = False
        self.setting = setting

        if DEBUG_INFO: print("generating the animation")
        self.color_generator = get_color_generator()
        self.fig = plt.figure()

        if len(motions) == 2 and self.setting.flag_heatmap:
            self.scores = cp.get_scores(motions[0].recordings[RECORDING_FOR_SCORE],
                                        motions[1].recordings[RECORDING_FOR_SCORE],
                                        setting.frame_wise_weights)
            self.ax_heatmap = self.fig.add_subplot(1, 2, 2)
            self.ax_heatmap.set_aspect(1)
            self.ax_heatmap.set_axis_off()
            self.ax_heatmap.set_xlim(-1, 1)
            self.ax_heatmap.set_ylim(-1, 1)
            joint_positions: np.ndarray = np.array(HEATMAP_JOINT_POSITION)
            self.heatmap = self.ax_heatmap.scatter(joint_positions[:, 0], joint_positions[:, 1], s=200,
                                                   vmin=MINIMUM_SCORE, vmax=MAXIMUM_SCORE,
                                                   c=np.zeros(len(HEATMAP_JOINT_POSITION)), cmap=COLOR_MAP)
            self.ax_motions = self.fig.add_subplot(1, 2, 1, projection="3d")
        else:
            self.setting.flag_heatmap = False
            self.ax_motions = self.fig.add_subplot(1, 1, 1, projection="3d")

        self.ax_motions.set(xlim3d=(-1, 1), xlabel='X')
        self.ax_motions.set(ylim3d=(-1, 1), ylabel='Y')
        self.ax_motions.set(zlim3d=(-1, 1), zlabel='Z')

        self.characters = []
        for motion in motions:
            self.characters.append(
                Character(motion, self.ax_motions, self.setting.visualized_vector, self.color_generator))
        self.ax_motions.legend()

        self.ani = FuncAnimation(self.fig, self.update, frames=len(max(motions, key=len)), interval=40,
                                 repeat=self.setting.flag_repeat)

        # To add a stop button for the animation, about only available for python
        # self.fig.subplots_adjust(bottom=0.2)
        # self.button = Button(self.fig.add_axes([0.81, 0.05, 0.1, 0.075]), 'stop')
        # self.button.on_clicked(self.toggle_pause)

    def update(self, index: int):
        def update_skeleton() -> None:
            for line, joint_connection in zip(character.skeleton, SKELETON_CONNECTION_MAP):
                endpoint_0: str = joint_connection[0]
                endpoint_1: str = joint_connection[1]
                line_x: List[int] = [position[endpoint_0 + " x"], position[endpoint_1 + " x"]]
                line_y: List[int] = [position[endpoint_0 + " y"], position[endpoint_1 + " y"]]
                line_z: List[int] = [position[endpoint_0 + " z"], position[endpoint_1 + " z"]]

                line.set_data([line_x, line_y])
                line.set_3d_properties(line_z)

        def update_visualized_vectors() -> None:
            vectors = character.visualized_vector.iloc[index]
            for joint_velocity, joint_connection in zip(character.visualized_vectors, SKELETON_CONNECTION_MAP):
                endpoint_0: str = joint_connection[0]
                endpoint_1: str = joint_connection[1]
                new_vectors: Dict[Union(Tuple[str, str, str], str), List[int]] = {}
                key = ""
                for axis in AXIS:
                    if character.visualized_vector_key_type == "Tuple":
                        key = (endpoint_0, endpoint_1, axis)
                    elif character.visualized_vector_key_type == "str":
                        key = endpoint_0 + axis
                    new_vectors[axis] = [position[endpoint_0 + axis],
                                         position[endpoint_0 + axis] - vectors[key]]

                joint_velocity.set_data([new_vectors[" x"], new_vectors[" y"]])
                joint_velocity.set_3d_properties(new_vectors[" z"])

        def update_heatmap() -> None:
            self.heatmap.set_array(self.scores.iloc[index][:-1])

        for character in self.characters:
            if index < len(character):
                position: pd.DataFrame = character.position_recording.iloc[index]
                update_skeleton()
                if self.setting.flag_heatmap:
                    update_heatmap()
                if self.setting.flag_visualized_vector:
                    update_visualized_vectors()

    def toggle_pause(self, event):
        if self.is_paused:
            self.ani.resume()
        else:
            self.ani.pause()
        self.is_paused = not self.is_paused

    def to_html5_video(self):
        if DEBUG_INFO: print("converting the output to html5 video")
        return self.ani.to_html5_video()

    def to_gif(self, file_name: str):
        if DEBUG_INFO: print("saving animation as gif")
        all_path: str = OUTPUT_FOLDER + file_name + ".gif"
        self.ani.save(all_path, writer=GIF_WRITER, fps=GIF_FPS)

    def show(self):
        plt.show()


def get_color_generator() -> Color_generator:
    for color in COLOR_POOL:
        yield color
