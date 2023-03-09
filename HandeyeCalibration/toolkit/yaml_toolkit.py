from __future__ import print_function
import yaml
import numpy as np
import os
import cv2 
import pdb


def opencv_matrix(loader, node):
    mapping = loader.construct_mapping(node, deep=True)
    mat = np.array(mapping["data"])
    mat.resize(mapping["rows"], mapping["cols"])
    return mat
yaml.add_constructor(u"tag:yaml.org,2002:opencv-matrix", opencv_matrix)


def opencv_matrix_representer(dumper, mat):
    mapping = {'rows': mat.shape[0], 'cols': mat.shape[1], 'dt': 'd', 'data': mat.reshape(-1).tolist()}
    return dumper.represent_mapping(u"tag:yaml.org,2002:opencv-matrix", mapping)
yaml.add_representer(np.ndarray, opencv_matrix_representer)


def read_yaml(dir):
    with open(dir, 'r') as f:
        c = f.read()
        # pdb.set_trace()
        # some operator on raw conent of c may be needed
        if c.startswith("%YAML:1.0") and c[10] != '-':
            c = "%YAML 1.1"+os.linesep+"---" + c[len("%YAML:1.0"):]        
        if c.startswith("%YAML:1.0") and c[10] == '-':
            c = "%YAML 1.1" + c[len("%YAML:1.0"):] 
            
        # print(c)
        result = yaml.load(c)
        # data = yaml.load(stream=f, Loader=yaml.FullLoader)
        return result
    
    
if __name__ == '__main__':
    n = 10
    R_target2cam = []
    data = read_yaml('RotationVectors.yml')
    # print(data)
    for index in range(1,n+1):
        index0 = index%10
        index1 = int(index/10)%10
        key = 'RotationVectors%s'%(str(index1)+str(index0))
        R_vector = data[key]
        R, _ = cv2.Rodrigues(R_vector)
        R_target2cam.append(R)
    print(R_target2cam)
    