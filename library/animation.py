import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from constants import *
import matplotlib.colors as mcolors
from matplotlib.widgets import Button
import numpy as np


class Character:
    def __init__(self, motion, skeleton, visualized_velocities):
        self.position_recording = motion.position_recording
        self.velocity_recording = motion.velocity_recording
        self.label = motion.label
        self.skeleton = skeleton
        self.visualized_velocities = visualized_velocities

    def __len__(self):
        return len(self.position_recording)


class Animation:

    def __init__(self, motions, scores, flag_visualized_velocities=False, is_repeat=False):
        self.is_paused = False
        self.flag_visualized_velocities = flag_visualized_velocities
        self.is_repeat = is_repeat
        self.scores = scores
        self.colors = list(mcolors.BASE_COLORS.values())

        self.fig = plt.figure()
        self.fig.subplots_adjust(bottom=0.2)
        self.ax = self.fig.add_subplot(projection="3d")

        self.ax.set(xlim3d=(-1, 1), xlabel='X')
        self.ax.set(ylim3d=(-1, 1), ylabel='Y')
        self.ax.set(zlim3d=(-1, 1), zlabel='Z')

        self.characters = []
        for index, motion in enumerate(motions):
            skeleton = [self.ax.plot([], [], [], c=self.colors[index * 2])[0] for _ in SKELETON_CONNECTION_MAP]
            skeleton[0].set_label(motion.label)
            visualized_velocities = [self.ax.plot([], [], [], c=self.colors[index * 2 + 1])[0] for _ in
                                     SKELETON_CONNECTION_MAP]
            self.characters.append(Character(motion, skeleton, visualized_velocities))

        joint_positions = np.array(HEATMAP_JOINT_POSITION)
        self.heatmap = self.ax.scatter(joint_positions[:, 0], joint_positions[:, 1], joint_positions[:, 2], s=200,
                                       vmin=0, vmax=1, c=np.zeros(len(HEATMAP_JOINT_POSITION)), cmap="gist_heat",
                                       alpha=1)

        self.ani = FuncAnimation(self.fig, self.update, frames=len(max(motions)), interval=40, repeat=self.is_repeat)
        self.ax.legend()

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
            arr = self.scores.iloc[index][:-1]
            self.heatmap.set_array(arr)

        for character in self.characters:
            if index < len(character):
                position = character.position_recording.iloc[index]
                update_skeleton()
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
