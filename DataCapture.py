import socket
import struct
import numpy as np
import UR_Commands as UR
import cv2
import os
import pyrealsense2 as rs 
from datetime import datetime
import time

z = 0
HOST = "169.254.71.1"  # The remote host
PORT = 30003  # The same port as used by the server

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 15)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)


# Start streaming
pipe_profile = pipeline.start(config)

# Create an align object
align_to = rs.stream.color
align = rs.align(align_to)
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
cwd = os.getcwd()
start_time = datetime.now().strftime(r'%y_%m_%d')
dir_root = os.path.join(cwd, 'data', start_time) 

dir_RGB = os.path.join(dir_root, 'RGB\\')
dir_depth = os.path.join(dir_root, 'depth\\')

if not os.path.exists(dir_root):
    os.mkdir(dir_root)

if not os.path.exists(dir_RGB):
    os.mkdir(dir_RGB)
    
if not os.path.exists(dir_depth):
    os.mkdir(dir_depth)
    

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

    a = dic_UR3['q actual']
    # for key, value in dic.items():
    #     print(key, end=": ")
    #     print(value[1])
    # print()
    return a
    
    
if __name__ == '__main__':

    count = 270
    
    while True:  
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        img_color = np.asanyarray(color_frame.get_data())
        img_depth = np.asanyarray(depth_frame.get_data())
        cv2.namedWindow('color_frame', cv2.WINDOW_FREERATIO)
        cv2.resizeWindow('color_frame', 640, 480)
        cv2.imshow('color_frame',img_color)
        
        key = cv2.waitKey(1)
        
        if key & 0xFF == ord('a'):
            # 机械臂运动
            q = get_UR3_dict()
            q_type, q_vector = q[0], q[1]
            q_vector_next = list(q_vector)
            q_vector_next[5] = q_vector_next[5] + 0.1744
            UR.movej_list(q_vector_next, 0.1, 0.5)
            time.sleep(3)
            print('{} finished'.format(count/3))
            
        if key & 0xFF == ord('s'):
            # 计数
            count0=count%10
            count1=int(count/10)%10
            count2=int(count/100)%10
            count3=int(count/1000)%10
            count = count + 1
            # 图像采集
            cv2.imwrite(dir_RGB+str(count3)+str(count2)+str(count1)+str(count0)+'.jpg', img_color)
            cv2.imwrite(dir_depth+str(count3)+str(count2)+str(count1)+str(count0)+'.jpg', img_depth)
              
        elif key & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


