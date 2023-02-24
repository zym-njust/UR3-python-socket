import socket
import struct
import math
import re, time
import numpy as np
import cv2


z = 0
HOST = "169.254.71.1"  # The remote host
PORT = 30003  # The same port as used by the server

def main():

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
        

    a = dic_UR3['Tool vector actual']
    b = dic_UR3['Tool vector target']
    print('Tool vector actual: {} \n Tool vector target:{} \n'.format(a,b))
    # for key, value in dic.items():
    #     print(key, end=": ")
    #     print(value[1])
    # print()
    
def get_calib_data():
    print()
    
def forward_kine():
    print()
    
def handeye():
    cv2.calibrateHandEye()
    
    
if __name__ == '__main__':
    # main()
    # exit()
    while True:
        try:
            # keyboard = input('input:')
            # if keyboard == 'a':
            z = z + 1
            #     main()
            # elif keyboard == 'q':
            #     print('--------------Over--------------')
            #     break
            main()
        except KeyboardInterrupt:
            break


