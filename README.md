# UR3-python-socket
python API for UR3


+ UR_Commands.py: 将控制指令重写为函数，方便直接调用
+ send_demo.py: 调用UR_Commands.py中的函数
+ recv_port_30003: 接收30003端口收到的数据包，并解析。UR机械臂收发的数据包协议由搭载的系统版本决定
+ test.urscript: 用urscript语法编写的脚本，用于UR_Commands.py中的函数send_script()。
+ HandeyeCalibration: 手眼标定，采集和标定的程序

