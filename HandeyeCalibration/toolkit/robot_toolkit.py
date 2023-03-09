#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ching-Yen Weng"
__version__ = "1.0.1"
__maintainer__ = "Ching-Yen Weng"
__email__ = "wengchingyen@gmail.com"
__status__ = "Prototype"

import numpy as np
import transformations as tf
from math import *
import cmath
from geometry_msgs.msg import Pose, Quaternion
import pdb
import cv2
"""Kinematics Docstring
   This python script provides solution of forward kinematics and 
   inverse kinematics for Universal Robot UR3/5/10.
"""

# Congifuration
# Select the robot type.
# UR10 for 'UR10'
# UR5 for 'UR5'
# UR3 for 'UR3'

ROBOT = 'UR3'


# DH Parameter

if ROBOT == 'UR10':

    # d (unit: mm)
    d1 = 127.3
    d2 = d3 = 0
    d4 = 163.941
    d5 = 115.7
    d6 = 92.2

    # a (unit: mm)
    a1 = a4 = a5 = a6 = 0
    a2 = -612
    a3 = -572.3

elif ROBOT == 'UR5':

    # d (unit: mm)
    d1 = 89.159 
    d2 = d3 = 0
    d4 = 109.15
    d5 = 94.65
    d6 = 82.3

    # a (unit: mm)
    a1 = a4 = a5 = a6 = 0
    a2 = -425
    a3 = -392.25

elif ROBOT == 'UR3':

    # d (unit: mm)
    d1 = 151.9 
    d2 = d3 = 0
    d4 = 112.35
    d5 = 85.35
    d6 = 81.9

    # a (unit: mm)
    a1 = a4 = a5 = a6 = 0
    a2 = -243.65
    a3 = -213.25


# List type of D-H parameter
# Do not remove these
d = np.array([d1, d2, d3, d4, d5, d6]) # unit: mm
a = np.array([a1, a2, a3, a4, a5, a6]) # unit: mm
alpha = np.array([pi/2, 0, 0, pi/2, -pi/2, 0]) # unit: radian


# Auxiliary Functions

def ur2ros(ur_pose):
    """Transform pose from UR format to ROS Pose format.
    Args:
        ur_pose: A pose in UR format [px, py, pz, rx, ry, rz] 
        (type: list)
    Returns:
        An HTM (type: Pose).
    """

    # ROS pose
    ros_pose = Pose()

    # ROS position
    ros_pose.position.x = ur_pose[0]
    ros_pose.position.y = ur_pose[1]
    ros_pose.position.z = ur_pose[2]

    # Ros orientation
    angle = sqrt(ur_pose[3] ** 2 + ur_pose[4] ** 2 + ur_pose[5] ** 2)
    direction = [i / angle for i in ur_pose[3:6]]
    np_T = tf.rotation_matrix(angle, direction)
    np_q = tf.quaternion_from_matrix(np_T)
    ros_pose.orientation.x = np_q[0]
    ros_pose.orientation.y = np_q[1]
    ros_pose.orientation.z = np_q[2]
    ros_pose.orientation.w = np_q[3]
    
    return ros_pose


def ros2np(ros_pose):
    """Transform pose from ROS Pose format to np.array format.
    Args:
        ros_pose: A pose in ROS Pose format (type: Pose)
    Returns:
        An HTM (type: np.array).
    """

    # orientation
    np_pose = tf.quaternion_matrix([ros_pose.orientation.x, ros_pose.orientation.y, \
                                    ros_pose.orientation.z, ros_pose.orientation.w])
    
    # position
    np_pose[0][3] = ros_pose.position.x
    np_pose[1][3] = ros_pose.position.y
    np_pose[2][3] = ros_pose.position.z

    return np_pose


def np2ros(np_pose):
    """Transform pose from np.array format to ROS Pose format.
    Args:
        np_pose: A pose in np.array format (type: np.array)
    Returns:
        An HTM (type: Pose).
    """

    # ROS pose
    ros_pose = Pose()

    # ROS position
    ros_pose.position.x = np_pose[0, 3]
    ros_pose.position.y = np_pose[1, 3]
    ros_pose.position.z = np_pose[2, 3]

    # ROS orientation 
    np_q = tf.quaternion_from_matrix(np_pose)
    ros_pose.orientation.x = np_q[0]
    ros_pose.orientation.y = np_q[1]
    ros_pose.orientation.z = np_q[2]
    ros_pose.orientation.w = np_q[3]

    return ros_pose


def select(q_sols, q_d, w=[1]*6):
    """Select the optimal solutions among a set of feasible joint value 
       solutions.
    Args:
        q_sols: A set of feasible joint value solutions (unit: radian)
        q_d: A list of desired joint value solution (unit: radian)
        w: A list of weight corresponding to robot joints
    Returns:
        A list of optimal joint value solution.
    """

    error = []
    for q in q_sols:
        error.append(sum([w[i] * (q[i] - q_d[i]) ** 2 for i in range(6)]))
    
    return q_sols[error.index(min(error))]


def HTM(i, theta):
    """Calculate the HTM(homogeneous transformation matrix) between two links. 
    Args:
        i: A target index of joint value. 
        theta: A list of joint value solution. (unit: radian)
    Returns:
        An HTM of Link l w.r.t. Link l-1, where l = i + 1.
    """

    Rot_z = np.matrix(np.identity(4))
    Rot_z[0, 0] = Rot_z[1, 1] = cos(theta[i])
    Rot_z[0, 1] = -sin(theta[i])
    Rot_z[1, 0] = sin(theta[i])

    Trans_z = np.matrix(np.identity(4))
    Trans_z[2, 3] = d[i]

    Trans_x = np.matrix(np.identity(4))
    Trans_x[0, 3] = a[i]

    Rot_x = np.matrix(np.identity(4))
    Rot_x[1, 1] = Rot_x[2, 2] = cos(alpha[i])
    Rot_x[1, 2] = -sin(alpha[i])
    Rot_x[2, 1] = sin(alpha[i])

    A_i = Rot_z * Trans_z * Trans_x * Rot_x
	    
    return A_i

def HTM2RT(HTM):
    assert HTM.shape == (4,4)
    RotMat = np.zeros([3, 3])
    TranVec = np.zeros([3, 1])
    RotMat[0,:] = HTM[0, 0:3]
    RotMat[1,:] = HTM[1, 0:3]
    RotMat[2,:] = HTM[2, 0:3]
    TranVec = HTM[0:3, 3]
    return RotMat, TranVec
        

# Forward Kinematics

def fwd_kin(theta, i_unit='r', o_unit='n'):
    
    """Solve the HTM based on a list of joint values.
    Args:
        theta: A list of joint values. (unit: radian)
        i_unit: Input format. 'r' for radian; 'd' for degree.
        o_unit: Output format. 'n' for np.array; 'p' for ROS Pose.
    Returns:
        The HTM of end-effector joint w.r.t. base joint
    """

    T_06 = np.matrix(np.identity(4))

    if i_unit == 'd':
        theta = [radians(i) for i in theta]
    
    for i in range(6):
        T_06 *= HTM(i, theta)

    if o_unit == 'n':
        return T_06
    elif o_unit == 'p':
        return np2ros(T_06)


# Inverse Kinematics

def inv_kin(p, q_d, i_unit='r', o_unit='r'):
    """Solve the joint values based on an HTM.
    Args:
        p: A pose.
        q_d: A list of desired joint value solution 
             (unit: radian).
        i_unit: Output format. 'r' for radian; 'd' for degree.
        o_unit: Output format. 'r' for radian; 'd' for degree.
    Returns:
        A list of optimal joint value solution.
    """

    # Preprocessing
    if type(p) == Pose: # ROS Pose format
        T_06 = ros2np(p)
    elif type(p) == list: # UR format
        T_06 = ros2np(ur2ros(p))

    if i_unit == 'd':
        q_d = [radians(i) for i in q_d]

    # Initialization of a set of feasible solutions
    theta = np.zeros((8, 6))
 
    # theta1
    P_05 = T_06[0:3, 3] - d6 * T_06[0:3, 2]
    phi1 = atan2(P_05[1], P_05[0])
    phi2 = acos(d4 / sqrt(P_05[0] ** 2 + P_05[1] ** 2))
    theta1 = [pi / 2 + phi1 + phi2, pi / 2 + phi1 - phi2]
    theta[0:4, 0] = theta1[0]
    theta[4:8, 0] = theta1[1]
  
    # theta5
    P_06 = T_06[0:3, 3]
    theta5 = []
    for i in range(2):
        theta5.append(acos((P_06[0] * sin(theta1[i]) - P_06[1] * cos(theta1[i]) - d4) / d6))
    for i in range(2):
        theta[2*i, 4] = theta5[0]
        theta[2*i+1, 4] = -theta5[0]
        theta[2*i+4, 4] = theta5[1]
        theta[2*i+5, 4] = -theta5[1]
  
    # theta6
    T_60 = np.linalg.inv(T_06)
    theta6 = []
    for i in range(2):
        for j in range(2):
            s1 = sin(theta1[i])
            c1 = cos(theta1[i])
            s5 = sin(theta5[j])
            theta6.append(atan2((-T_60[1, 0] * s1 + T_60[1, 1] * c1) / s5, (T_60[0, 0] * s1 - T_60[0, 1] * c1) / s5))
    for i in range(2):
        theta[i, 5] = theta6[0]
        theta[i+2, 5] = theta6[1]
        theta[i+4, 5] = theta6[2]
        theta[i+6, 5] = theta6[3]

    # theta3, theta2, theta4
    for i in range(8):  
        # theta3
        T_46 = HTM(4, theta[i]) * HTM(5, theta[i])
        T_14 = np.linalg.inv(HTM(0, theta[i])) * T_06 * np.linalg.inv(T_46)
        P_13 = T_14 * np.array([[0, -d4, 0, 1]]).T - np.array([[0, 0, 0, 1]]).T
        if i in [0, 2, 4, 6]:
            theta[i, 2] = -cmath.acos((np.linalg.norm(P_13) ** 2 - a2 ** 2 - a3 ** 2) / (2 * a2 * a3)).real
            theta[i+1, 2] = -theta[i, 2]
        # theta2
        theta[i, 1] = -atan2(P_13[1], -P_13[0]) + asin(a3 * sin(theta[i, 2]) / np.linalg.norm(P_13))
        # theta4
        T_13 = HTM(1, theta[i]) * HTM(2, theta[i])
        T_34 = np.linalg.inv(T_13) * T_14
        theta[i, 3] = atan2(T_34[1, 0], T_34[0, 0])       

    theta = theta.tolist()

    # Select the most close solution
    q_sol = select(theta, q_d)

    # Output format
    if o_unit == 'r': # (unit: radian)
        return q_sol
    elif o_unit == 'd': # (unit: degree)
        return [degrees(i) for i in q_sol]
    
    
if __name__ == '__main__':
    # pose = fwd_kin([-81.01, -0.03, -117.17, -23, 256.02, 33.83], i_unit='d')
    # 回零
    pose0 = fwd_kin([90, -120, -60, -90, -50, 0], i_unit='d')
    pose = fwd_kin([2.0684847831726074, -3.5050318876849573, 0.6794490814208984, -1.5130012671100062, 1.5725288391113281, 1.3537758588790894])
    # np.set_printoptions(precision=4) # 保留4位小数
    np.set_printoptions(suppress=True) # 取消科学计数法
    rot = np.array([1.078, 0.002, 2.951])
    R, _ = cv2.Rodrigues(rot)

    print(pose0, R )