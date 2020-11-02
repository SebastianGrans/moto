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

from moto.simple_message import (
    JointFeedback,
    JointTrajPtFull,
    Header,
    MsgType,
    CommType,
    ReplyType,
    SimpleMessage,
)


class ControlGroup:

    MAX_CONTROLLABLE_GROUPS: int = 4

    def __init__(
        self,
        groupid: str,
        groupno: int,
        num_joints: int,
        motion_connection: "MotionConnection",
        state_connection: "StateConnection",
        io_connection: "IoConnection",
    ):
        self._groupid: str = groupid
        self._groupno: int = groupno
        self._num_joints = num_joints
        self._motion_connection: "MotionConnection" = motion_connection
        self._state_connection: "StateConnection" = state_connection
        self._io_connection: "IoConnection" = io_connection

    @property
    def groupid(self) -> str:
        return self._groupid

    @property
    def groupno(self) -> int:
        return self._groupno

    @property
    def num_joints(self) -> int:
        return self._num_joints

    @property
    def position(self):
        return self.joint_feedback.pos[: self.num_joints]

    @property
    def velocity(self):
        return self.joint_feedback.vel[: self.num_joints]

    @property
    def acceleration(self):
        return self.joint_feedback.acc[: self.num_joints]

    @property
    def joint_feedback(self) -> JointFeedback:
        return self._state_connection.joint_feedback(self._groupno)

    def check_queue_count(self):
        return self._motion_connection._check_queue_count(self.groupno)

    def send_joint_traj_pt_full(self, joint_traj_pt_full: JointTrajPtFull) -> None:
        msg = SimpleMessage(
            Header(
                msg_type=MsgType.JOINT_TRAJ_PT_FULL,
                comm_type=CommType.TOPIC,
                reply_type=ReplyType.INVALID,
            ),
            joint_traj_pt_full,
        )
        self._motion_connection.send(msg)
