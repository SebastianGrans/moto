# Copyright 2020 Norwegian University of Science and Technology.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Mapping, Tuple, Union
import time

from moto.motion_connection import MotionConnection
from moto.state_connection import StateConnection
from moto.io_connection import IoConnection
from moto.real_time_motion_connection import RealTimeMotionConnection
from moto.control_group import ControlGroupDefinition, ControlGroup
from moto.simple_message import JointTrajPtExData, JointTrajPtFullEx, JointTrajPtFull, ValidFields


class Motion:
    def __init__(self, motion_connection: MotionConnection) -> None:
        self._motion_connection: MotionConnection = motion_connection

    def connect(self):
        self._motion_connection.start()

    def disconnect(self):
        self._motion_connection.disconnect()

    def check_motion_ready(self):
        return self._motion_connection.check_motion_ready()

    def stop_motion(self):
        return self._motion_connection.stop_motion()

    def start_servos(self):
        return self._motion_connection.start_servos()

    def stop_servos(self):
        return self._motion_connection.stop_servos()

    def start_trajectory_mode(self):
        return self._motion_connection.start_traj_mode()

    def stop_trajectory_mode(self):
        return self._motion_connection.stop_traj_mode()

    def select_tool(self, groupno: int, tool: int, sequence: int = -1):
        return self._motion_connection.select_tool(groupno, tool, sequence)

    def get_dh_parameters(self):
        return self._motion_connection.get_dh_parameters()

    def send_joint_trajectory_point(
        self, joint_trajectory_point: Union[JointTrajPtFull, JointTrajPtFullEx]
    ):
        return self._motion_connection.send_joint_trajectory_point(
            joint_trajectory_point
        )


class State:
    def __init__(self, state_connection: StateConnection) -> None:
        self._state_connection: StateConnection = state_connection

    def connect(self):
        self._state_connection.start()

    def joint_feedback(self, groupno: int):
        return self._state_connection.joint_feedback(groupno)

    def joint_feedback_ex(self):
        return self._state_connection.joint_feedback_ex()

    def robot_status(self):
        return self._state_connection.robot_status()

    def add_joint_feedback_msg_callback(self, callback):
        self._state_connection.add_joint_feedback_msg_callback(callback)

    def add_joint_feedback_ex_msg_callback(self, callback):
        self._state_connection.add_joint_feedback_ex_msg_callback(callback)


class IO:
    def __init__(self, io_connection: IoConnection) -> None:
        self._io_connection: IoConnection = io_connection

    def connect(self):
        self._io_connection.start()

    def read_bit(self, address: int):
        return self._io_connection.read_io_bit(address)

    def write_bit(self, address: int, value: int):
        return self._io_connection.write_io_bit(address, value)

    def read_group(self, address: int):
        return self._io_connection.read_io_group(address)

    def write_group(self, address: int, value: int):
        return self._io_connection.write_io_group(address, value)


class RealTimeMotion:
    def __init__(self, real_time_motion_connection: RealTimeMotionConnection) -> None:
        self._real_time_motion_connection: RealTimeMotionConnection = (
            real_time_motion_connection
        )

    def connect(self):
        self._real_time_motion_connection.start()

    def start_rt_mode(self):
        self._real_time_motion_connection.start_rt_mode()

    def stop_rt_mode(self):
        self._real_time_motion_connection.stop_rt_mode()


class Moto:
    def __init__(
        self,
        robot_ip: str,
        control_group_defs: List[ControlGroupDefinition],
        start_motion_connection: bool = True,
        start_state_connection: bool = True,
        start_io_connection: bool = True,
        start_real_time_connection: bool = False,
    ):
        self._robot_ip: str = robot_ip
        self._control_group_defs: List[ControlGroupDefinition] = control_group_defs

        self._motion_connection: MotionConnection = MotionConnection(self._robot_ip)
        self._state_connection: StateConnection = StateConnection(self._robot_ip)
        self._io_connection: IoConnection = IoConnection(self._robot_ip)
        self._real_time_motion_connection: RealTimeMotionConnection = (
            RealTimeMotionConnection(self._robot_ip)
        )

        self._control_groups: Mapping[str, ControlGroup] = {}
        for control_group_def in self._control_group_defs:
            self._control_groups[control_group_def.groupid] = ControlGroup(
                control_group_def, self._motion_connection, self._state_connection,
            )

        if start_motion_connection:
            self._motion_connection.start()
        if start_state_connection:
            self._state_connection.start()
        if start_io_connection:
            self._io_connection.start()

    @property
    def control_groups(self):
        return self._control_groups

    @property
    def motion(self):
        return Motion(self._motion_connection)

    @property
    def state(self):
        return State(self._state_connection)

    @property
    def io(self):
        return IO(self._io_connection)

    @property
    def rt(self):
        return RealTimeMotion(self._real_time_motion_connection)

    def go_to(self, position):
        '''
            Args:
                position (dictionary): Dictionary of groupid-List pair. 
        '''
        print("asdf")

        # TODO: Assert that the position lies within joint space.
        # TODO: Check that joint velocities are within some limit. 
                
        # TODO: Assert that the state connection is actually running.
        # Otherwise this will return None.
        joint_feedback = self.state.joint_feedback_ex()

        start_joint_traj_pt_data = [] 
        end_joint_traj_pt_data = [] 

        for _, group in self.control_groups.items():
            start_joint_traj_pt_data.append(
                JointTrajPtExData(
                    groupno=group.groupno,
                    valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
                    time=0.0,
                    # TODO: Confirm that joint_feedback_data is sorted by the
                    # groupno.
                    pos=joint_feedback.joint_feedback_data[group.groupno].pos,
                    vel=[0.0] * 10,
                    acc=[0.0] * 10,
                )
            )

            end_joint_traj_pt_data.append(
                JointTrajPtExData(
                    groupno=group.groupno,
                    valid_fields=ValidFields.TIME | ValidFields.POSITION | ValidFields.VELOCITY,
                    time=5.0,
                    pos=position[group.groupno],
                    vel=[0.0] * 10,
                    acc=[0.0] * 10,
                )
            )

        start = JointTrajPtFullEx(
            number_of_valid_groups=len(position),
            sequence=0,
            joint_traj_pt_data=start_joint_traj_pt_data
        )

        end = JointTrajPtFullEx(
            number_of_valid_groups=len(position),
            sequence=1,
            joint_traj_pt_data=end_joint_traj_pt_data
        )

        # Check that trajectory mode is on.
        ret = self.motion.start_trajectory_mode()
        while not self.state.robot_status().motion_possible and \
            not self.state.robot_status().drives_powered:
            time.sleep(0.1)

        # TODO: Assert that the motion connection is active.
        ret1 = self.motion.send_joint_trajectory_point(start)
        ret2 = self.motion.send_joint_trajectory_point(end)
        

        time.sleep(1)
        # TODO: This isn't a reliable way to know if the trajectory is complete.
        while self.state.robot_status().in_motion:
            print(self.state.robot_status())
            time.sleep(0.1)

        
        # self.motion.stop_trajectory_mode()
        # self.motion.stop_servos()
    
    
    def go_home(self):
        pos_dict = {}
        for i in range(len(self.control_groups)):
            pos_dict[i] = [0.0] * 10
        self.go_to(pos_dict)