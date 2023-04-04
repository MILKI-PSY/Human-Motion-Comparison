import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from constants import *
import matplotlib.colors as mcolors


class Animation:

    def __init__(self, recording_pairs, with_visualized_velocities=False):
        self.is_paused = False
        self.recording_pairs = recording_pairs
        self.with_visualized_velocities = with_visualized_velocities
        self.colors = list(mcolors.TABLEAU_COLORS.values())

    def show(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")

        ax.set(xlim3d=(-1, 1), xlabel='X')
        ax.set(ylim3d=(-1, 1), ylabel='Y')
        ax.set(zlim3d=(-1, 1), zlabel='Z')

        anis = list()
        for index, recording_pair in self.recording_pairs.iterrows():
            position_recording = recording_pair["position recording"]
            velocity_recording = recording_pair["velocity recording"]
            skeleton = [ax.plot([], [], [], c=self.colors[index * 2])[0] for _ in SKELETON_CONNECTION_MAP]
            visualized_velocities = [ax.plot([], [], [], c=self.colors[index * 2 + 1])[0] for _ in
                                     SKELETON_CONNECTION_MAP]
            anis.append(
                FuncAnimation(fig, self.update, frames=len(position_recording), interval=40, repeat=False,
                              fargs=(position_recording, skeleton, velocity_recording, visualized_velocities)))

        fig.canvas.mpl_connect('button_press_event', self.toggle_pause(anis))
        plt.show()

    def set_with_visualized_velocities(self, value):
        self.with_visualized_velocities = value

    def update(self, index, position_recording, skeleton, velocity_recording, visualized_velocities):
        velocity = None
        position = position_recording.iloc[index]
        if self.with_visualized_velocities:
            velocity = velocity_recording.iloc[index]
        for line, joint_velocity, joint_connection in zip(skeleton, visualized_velocities, SKELETON_CONNECTION_MAP):
            endpoint_0 = joint_connection[0]
            endpoint_1 = joint_connection[1]

            line_x = [position[endpoint_0 + " x"], position[endpoint_1 + " x"]]
            line_y = [position[endpoint_0 + " y"], position[endpoint_1 + " y"]]
            line_z = [position[endpoint_0 + " z"], position[endpoint_1 + " z"]]

            line.set_data([line_x, line_y])
            line.set_3d_properties(line_z)

            if self.with_visualized_velocities:
                joint_velocity_x = [position[endpoint_1 + " x"],
                                    position[endpoint_1 + " x"] - velocity[endpoint_1 + " x"]]
                joint_velocity_y = [position[endpoint_1 + " y"],
                                    position[endpoint_1 + " y"] - velocity[endpoint_1 + " y"]]
                joint_velocity_z = [position[endpoint_1 + " z"],
                                    position[endpoint_1 + " z"] - velocity[endpoint_1 + " z"]]

                joint_velocity.set_data([joint_velocity_x, joint_velocity_y])
                joint_velocity.set_3d_properties(joint_velocity_z)

    def toggle_pause(self, anis):
        if self.is_paused:
            for ani in anis:
                ani.resume()
        else:
            for ani in anis:
                ani.pause()
        self.is_paused = not self.is_paused
