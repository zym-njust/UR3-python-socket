'''
Date: 2023/3/9 first editing finished
Author: Yiman Zhu
Function: Read matrix from yaml file, then do handeyecalibration.

'''
import cv2
from toolkit.robot_toolkit import *
from toolkit.yaml_toolkit import *
import pdb

# 检查n和urposition.py是否一致
n = 15
R_target2cam = []
t_target2cam = []
R_gripper2base = []
t_gripper2base = []
filename = 'handeye.yml'
data1 = read_yaml('RotationVectors.yml')
data2 = read_yaml('TranslationVectors.yml')
data3 = read_yaml('R_gripper2base.yml')
data4 = read_yaml('t_gripper2base.yml')


for index in range(1,n+1):
    index0 = index%10
    index1=int(index/10)%10
    key1 = 'RotationVectors%s'%(str(index1)+str(index0))
    key2 = 'TranslationVectors%s'%(str(index1)+str(index0))
    
    R_target2cam_value_vector = data1[key1]
    t_target2cam_value = data2[key2]
    R_target2cam_value, _ = cv2.Rodrigues(R_target2cam_value_vector)
    R_target2cam.append(R_target2cam_value)
    t_target2cam.append(t_target2cam_value)
        
    R_gripper2base_value_vector = data3[key1]
    t_gripper2base_value = data4[key2]
    R_gripper2base_value = R_gripper2base_value_vector.reshape([3,3])
    # pdb.set_trace()
    R_gripper2base.append(R_gripper2base_value)
    t_gripper2base.append(t_gripper2base_value)
    
R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, cv2.CALIB_HAND_EYE_TSAI)
print( 'R_cam2gripper: {}'.format(R_cam2gripper))
print( 't_cam2gripper: {}'.format(t_cam2gripper))

s = cv2.FileStorage(filename, cv2.FileStorage_WRITE)
s.write('RotationMatrix', R_cam2gripper)
s.write('TranslationVector', t_cam2gripper)
s.release()

