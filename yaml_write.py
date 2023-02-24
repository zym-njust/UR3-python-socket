from __future__ import print_function
import numpy as np
import cv2 as cv
import sys
import pdb
    
def main():

    
    R = np.eye(3,3)
    T = np.zeros((3,1))
    
    
    filename1 = 'atest.yml'
    filename2 = 'btest.yml'
    
    s1 = cv.FileStorage(filename1, cv.FileStorage_WRITE)
    s2 = cv.FileStorage(filename2, cv.FileStorage_WRITE)
    pdb.set_trace()
    # or:
    # s = cv.FileStorage()
    # s.open(filename, cv.FileStorage_WRITE)
    

    # for i in range(6):
    #     s1.write('R_MAT', i)
    #     s2.write('T_MAT', i)
    
    
    s1.release()
    s2.release()
    
    print ('Write Done.')

    
    
if __name__ == '__main__':
    main()