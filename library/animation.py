import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from constants import *

from matplotlib.widgets import Button
import numpy as np


class Character:
    def __init__(self, motion, axes, color_generator):
        self.position_recording = motion.position_recording
        self.velocity_recording = motion.velocity_recording
        color = next(color_generator)
        self.skeleton = [axes.plot([], [], [], c=color)[0] for _ in SKELETON_CONNECTION_MAP]
        self.skeleton[0].set_label(motion.label)  # the whole skeleton is the same color, so one label is enough
        color = next(color_generator)
        self.visualized_velocities = [axes.plot([], [], [], c=color)[0] for _ in SIMPLIFIED_JOINTS]

    def __len__(self):
        return len(self.position_recording)


class Animation:
    def __init__(self, motions, scores=None, flag_visualized_velocities=False, flag_repeat=False, flag_heatmap=False):
        self.is_paused = False
        self.flag_visualized_velocities = flag_visualized_velocities
        self.flag_repeat = flag_repeat
        self.flag_heatmap = flag_heatmap
        self.scores = scores
        self.color_generator = self.get_color_generator()

        self.fig = plt.figure()
        self.fig.subplots_adjust(bottom=0.2)

        if self.flag_heatmap:
            self.ax_heatmap = self.fig.add_subplot(1, 2, 2)
            self.ax_heatmap.set_aspect(1)
            self.ax_heatmap.set_axis_off()
            self.ax_heatmap.set_xlim(-1, 1)
            self.ax_heatmap.set_ylim(-1, 1)
            joint_positions = np.array(HEATMAP_JOINT_POSITION)
            self.heatmap = self.ax_heatmap.scatter(joint_positions[:, 0], joint_positions[:, 1], s=200, vmin=0, vmax=1,
                                                   c=np.zeros(len(HEATMAP_JOINT_POSITION)), cmap="Reds")

            self.ax_motions = self.fig.add_subplot(1, 2, 1, projection="3d")
        else:
            self.ax_motions = self.fig.add_subplot(1, 1, 1, projection="3d")

        self.ax_motions.set(xlim3d=(-1, 1), xlabel='X')
        self.ax_motions.set(ylim3d=(-1, 1), ylabel='Y')
        self.ax_motions.set(zlim3d=(-1, 1), zlabel='Z')

        self.characters = []
        for motion in motions:
            self.characters.append(Character(motion, self.ax_motions, self.color_generator))
        self.ax_motions.legend()

        self.ani = FuncAnimation(self.fig, self.update, frames=len(max(motions)), interval=40, repeat=self.flag_repeat)

        self.button = Button(self.fig.add_axes([0.81, 0.05, 0.1, 0.075]), 'stop')
        self.button.on_clicked(self.toggle_pause)

    def set_flag_visualized_velocities(self, value):
        self.flag_visualized_velocities = value

    def update(self, index):
        def update_skeleton():
            for line, joint_connection in zip(character.skeleton, SKELETON_CONNECTION_MAP):
                endpoint_0 = joint_connection[0]
                endpoint_1 = joint_connection[1]
                line_x = [position[endpoint_0 + " x"], position[endpoint_1 + " x"]]
                line_y = [position[endpoint_0 + " y"], position[endpoint_1 + " y"]]
                line_z = [position[endpoint_0 + " z"], position[endpoint_1 + " z"]]

                line.set_data([line_x, line_y])
                line.set_3d_properties(line_z)

        def update_visualized_velocities():
            for joint_velocity, joint_connection in zip(character.visualized_velocities, SKELETON_CONNECTION_MAP):
                velocity = character.velocity_recording.iloc[index]
                endpoint_1 = joint_connection[1]

                joint_velocity_x = [position[endpoint_1 + " x"],
                                    position[endpoint_1 + " x"] - velocity[endpoint_1 + " x"]]
                joint_velocity_y = [position[endpoint_1 + " y"],
                                    position[endpoint_1 + " y"] - velocity[endpoint_1 + " y"]]
                joint_velocity_z = [position[endpoint_1 + " z"],
                                    position[endpoint_1 + " z"] - velocity[endpoint_1 + " z"]]

                joint_velocity.set_data([joint_velocity_x, joint_velocity_y])
                joint_velocity.set_3d_properties(joint_velocity_z)

        def update_heatmap():
            self.heatmap.set_array(self.scores.iloc[index][:-1])  # -1 because the last element is overall

        for character in self.characters:
            if index < len(character):
                position = character.position_recording.iloc[index]
                update_skeleton()
                if self.flag_heatmap:
                    update_heatmap()
                if self.flag_visualized_velocities:
                    update_visualized_velocities()

    def toggle_pause(self, event):
        if self.is_paused:
            self.ani.resume()
        else:
            self.ani.pause()
        self.is_paused = not self.is_paused

    def save_as_gif(self, name):
        writer = PillowWriter(fps=30)
        self.ani.save(ANIMATION_SAVE_PATH + name + ".gif", writer=writer)

    def get_color_generator(self):
        for color in COLOR_POOL:
            yield color
