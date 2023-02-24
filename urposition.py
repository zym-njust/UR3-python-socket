from __future__ import print_function
import socket
import struct
import numpy as np
import cv2
import os
from utils import *
import pyrealsense2 as rs 
from yaml_toolkit import *
import pdb



# s1.startWriteStruct('Mapping', cv2.FileNode_MAP)
# s2.startWriteStruct('Mapping', cv2.FileNode_MAP)

HOST = "192.168.12.109"  # The remote host
PORT = 30003  # The same port as used by the server

# Declare pointcloud object, for calculating pointclouds and texture mappings
pc = rs.pointcloud()
# We want the points object to be persistent so we can display the last cloud when a frame drops
points = rs.points()


pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

# Start streaming
pipe_profile = pipeline.start(config)

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
cwd = os.getcwd()
dir_root = os.path.join(cwd, 'calib') 

if not os.path.exists(dir_root):
    os.mkdir(dir_root)

def get_UR3_dict():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    dic_UR3 = {'MessageSize': 'i', 'Time': 'd', 'q target': '6d', 'qd target': '6d', 'qdd target': '6d', 'I target': '6d',
           'M target': '6d', 'q actual': '6d', 'qd actual': '6d', 'I actual': '6d', 'I control': '6d',
           'Tool vector actual': '6d', 'TCP speed actual': '6d', 'TCP force': '6d', 'Tool vector target': '6d',
           'TCP speed target': '6d', 'Digital input bits': 'd', 'Motor temperatures': '6d', 'Controller Timer': 'd',
           'Test value': 'd', 'Robot Mode': 'd', 'Joint Modes': '6d', 'Safety Mode': 'd', 'empty1':'6d',
           'Tool Accelerometer values': '3d', 'empty2':'6d','Speed scaling': 'd', 'Linear momentum norm': 'd', 'empty3':'d','empty4':'d',
           'V main': 'd',
           'V robot': 'd', 'I robot': 'd', 'V actual': '6d', 'Digital outputs': 'd', 'Program state': 'd',
           'Elbow position': '3d', 'Elbow velocity': '3d', 'Safety Status': 'd','empty4':'d','empty5':'d','empty6':'d','Payload Mass':'d','Payload CoG':'3d','Payload Inertia':'6d'} # UR3 消息格式 {Type: i=int, d=double |  Number of values: 6d=6 double values}
    
    data = s.recv(1220) # 1220 total size in bytes
    # 参考 https://blog.csdn.net/qq_42236622/article/details/121740703

    names = []
    ii = range(len(dic_UR3))
    # print('ii:{}\n'.format(ii))
    for key, i in zip(dic_UR3, ii):
        fmtsize = struct.calcsize(dic_UR3[key])
        # print('fmtsize:{}\n'.format(fmtsize))
        data1, data = data[0:fmtsize], data[fmtsize:]
        # print('data1:{}\n'.format(data1))
        # print('data:{}\n'.format(data))
        
        fmt = "!" + dic_UR3[key]
        names.append(struct.unpack(fmt, data1))
        dic_UR3[key] = dic_UR3[key], struct.unpack(fmt, data1)
        
    # print("第{0:}次解析".format(z))

    q = dic_UR3['q actual']
    # b = dic_UR3['Tool vector target']
    # print('Tool vector actual: {} \n Tool vector target:{} \n'.format(a,b))
    return q
     
def main():
    index = 1
    n = 15
    filename1 = 'R_gripper2base.yml'
    filename2 = 't_gripper2base.yml'
    R_gripper2base = []
    t_gripper2base = []
    # 写入yml文件
    # s1 = cv2.FileStorage(filename1, cv2.FileStorage_WRITE)
    # s2 = cv2.FileStorage(filename2, cv2.FileStorage_WRITE)
    while True:  

        # 序号字符串
        index0 = index%10
        index1=int(index/10)%10
        # 相机当前帧
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        img_color = np.asanyarray(color_frame.get_data())
        cv2.namedWindow('color_frame', cv2.WINDOW_FREERATIO)
        cv2.resizeWindow('color_frame', 640, 480)
        cv2.imshow('color_frame',img_color)

        # 按键
        key = cv2.waitKey(1)
        if key & 0xFF == ord('a'):
            # 保存当前机械臂末端位姿
            q = get_UR3_dict()
            q_type, q_vector = q[0], q[1]
            print('Pose {} ------------------------------------'.format(index))
            print('Chcek The q_vector: {}'.format(q_vector))
            homo = fwd_kin(q_vector)
            R, t = HTM2RT(homo)
            R_gripper2base.append(R)
            t_gripper2base.append(t)
            # pdb.set_trace()
            # 写入文件 
            # s1 = cv2.FileStorage(filename1, cv2.FileStorage_WRITE)
            # s2 = cv2.FileStorage(filename2, cv2.FileStorage_WRITE)
            
            
            # 保存当前帧标定板图像
            cv2.imwrite(dir_root+'\\%s.jpg'%(str(index1)+str(index0)), img_color)
            print('R = {}   t = {}  \nImage Saved \n'.format(R, t))
            # 计数
            index = index + 1
              
        elif key & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        
    s1 = cv2.FileStorage(filename1, cv2.FileStorage_WRITE)
    s2 = cv2.FileStorage(filename2, cv2.FileStorage_WRITE)
    for i in range(n):
        index = i+1
        index0 = index%10
        index1=int(index/10)%10
        s1.write('RotationVectors%s'%(str(index1)+str(index0)), R_gripper2base[i])
        s2.write('TranslationVectors%s'%(str(index1)+str(index0)), t_gripper2base[i])
    s1.release()
    s2.release()
if __name__ == '__main__':
    main()

    
            
         
    


