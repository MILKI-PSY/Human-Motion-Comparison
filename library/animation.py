import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation
from matplotlib.text import Text
import library.motion as mt
from library.constants import *
from typing import List, Generator, Tuple, Dict, Optional, Union
from matplotlib import colors as mcolors


Color = Tuple[float, float, float]
Color_generator = Generator[Color, None, None]


class AnimationSetting:
    def __init__(self, flag_visualized_vector: bool, flag_heatmap: bool, flag_repeat: bool,
                 visualized_vector: str, heatmap_recording: str, gif_filename: str = "example"):
        self.flag_visualized_vector = flag_visualized_vector
        if self.flag_visualized_vector:
            self.visualized_vector = visualized_vector
        else:
            self.visualized_vector = None
        self.flag_heatmap = flag_heatmap
        self.flag_repeat = flag_repeat
        self.heatmap_recording = heatmap_recording
        self.gif_filename = gif_filename


class Character:
    def __init__(self, motion: mt.Motion, axes: plt.Axes, color_generator: Color_generator,
                 visualized_vector: Optional[str] = None) -> None:

        self.position_recording = motion.recordings[RECORDING_FOR_SKELETON]
        if visualized_vector is None:
            self.visualized_vector = None
        elif visualized_vector in NEED_ANGULATION_BEFORE_VISUALIZATION:
            self.visualized_vector = motion.get_angular_vector(visualized_vector)
            self.visualized_vector_key_type = "Tuple"
        else:
            self.visualized_vector = motion.recordings[visualized_vector]
            self.visualized_vector_key_type = "str"
        self.label = motion.meta.label
        color: Color = next(color_generator)
        self.skeleton = [axes.plot([], [], [], c=color)[0] for _ in SKELETON_CONNECTION_MAP]
        self.skeleton[0].set_label(self.label)  # the whole skeleton is the same color, so one label is enough
        color = next(color_generator)
        self.visualized_vectors = [axes.plot([], [], [], c=color)[0] for _ in SIMPLIFIED_JOINTS]

    def __len__(self) -> int:
        return len(self.position_recording)


class Animation:
    def __init__(self, motions: List[mt.Motion], setting: AnimationSetting,
                 comparison_result: Optional[pd.DataFrame] = None) -> None:
        self.is_paused: bool = False
        self.setting = setting

        if DEBUG_INFO: print("generating the animation")
        self.color_generator = get_color_generator()
        self.fig = plt.figure()

        if comparison_result is not None and self.setting.flag_heatmap:
            self.comparison_result = comparison_result
            self.ax_heatmap = self.fig.add_subplot(1, 2, 2)
            self.ax_heatmap.set_aspect(1)
            self.ax_heatmap.set_axis_off()
            self.ax_heatmap.set_xlim(-1, 1)
            self.ax_heatmap.set_ylim(-1, 1)
            joint_positions: np.ndarray = np.array(list(HEATMAP_JOINT_POSITION.values()))
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

        self.texts: Dict[str, Text] = {}
        for index, motion in enumerate(motions):
            self.texts[motion.meta.label] = self.ax_motions.text2D(0.05, 0.85 - 0.1 * index, "", fontsize=10,
                                                                   transform=self.ax_motions.transAxes)

        self.texts["frame"] = self.ax_motions.text2D(0.05, 0.95, "", fontsize=10, transform=self.ax_motions.transAxes)

        self.characters = []
        for motion in motions:
            self.characters.append(
                Character(motion, self.ax_motions, self.color_generator, self.setting.visualized_vector))
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

                lines: Dict[str, List[int]] = {}
                for axis in AXIS:
                    lines[axis] = [position[endpoint_0 + axis], position[endpoint_1 + axis]]

                line.set_data([lines[" x"], lines[" y"]])
                line.set_3d_properties(lines[" z"])

        def update_visualized_vectors() -> None:
            vectors = character.visualized_vector.iloc[index]
            for joint_velocity, joint_connection in zip(character.visualized_vectors, SKELETON_CONNECTION_MAP):
                endpoint_0: str = joint_connection[0]
                endpoint_1: str = joint_connection[1]
                new_vectors: Dict[Union[Tuple[str, str, str], str], List[int]] = {}
                key: Union[Tuple[str, str, str], str]
                for axis in AXIS:
                    if character.visualized_vector_key_type == "Tuple":
                        key = (endpoint_0, endpoint_1, axis)
                    else:
                        key = endpoint_0 + axis
                    new_vectors[axis] = [position[endpoint_0 + axis],
                                         position[endpoint_0 + axis] - vectors[key]]

                joint_velocity.set_data([new_vectors[" x"], new_vectors[" y"]])
                joint_velocity.set_3d_properties(new_vectors[" z"])

        def update_heatmap() -> None:

            self.heatmap.set_array(self.comparison_result.iloc[index][:])

        self.texts["frame"].set_text("frame: " + str(index))
        for character in self.characters:
            if index < len(character):
                position: pd.DataFrame = character.position_recording.iloc[index]
                self.texts[character.label].set_text(character.label + ": " + str(int(position["Frame"])))
                update_skeleton()
                if self.setting.flag_visualized_vector:
                    update_visualized_vectors()
        if self.setting.flag_heatmap:
            update_heatmap()

    def toggle_pause(self, event):
        if self.is_paused:
            self.ani.resume()
        else:
            self.ani.pause()
        self.is_paused = not self.is_paused

    def to_html5_video(self):
        if DEBUG_INFO: print("converting the output to html5 video")
        return self.ani.to_html5_video()

    def to_gif(self):
        if DEBUG_INFO: print("saving animation as gif")
        all_path: str = OUTPUT_FOLDER + self.setting.gif_filename + ".gif"
        self.ani.save(all_path, writer=GIF_WRITER, fps=GIF_FPS)

    def show(self):
        plt.show()


def get_color_generator() -> Color_generator:
    for color in list(mcolors.BASE_COLORS.values()):
        yield color
