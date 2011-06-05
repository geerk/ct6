from math import cos, sin, pi
from math import radians as rad
from matrix import matrix as mat

def project(p, prtype, c = 1000.0):
    if prtype == "parallel":
        return [p[0], p[1]]
    elif prtype == "central":
        return [p[0]/(1 - p[2] / c), p[1]/(1 - p[2] / c)]

def translate(m, (x, y, z)):
    return m * mat([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [x, y, z, 1]])

def rotate(m, b, (ox, oy, oz)):
    return rotate_oz(rotate_oy(rotate_ox(m, b, ox), b, oy), b, oz)

def rotate_oz(m, b, a):
    cosa, sina = cos(rad(a)), sin(rad(a))
    rotm = translate(mat(1), [-b[0], -b[1], -b[2]])
    rotm = rotm * mat([[ cosa, sina, 0, 0],
                       [-sina, cosa, 0, 0],
                       [    0,    0, 1, 0],
                       [    0,    0, 0, 1]])
    rotm = rotm * translate(mat(1), b)
    return m * rotm
    
def rotate_oy(m, b, a):
    cosa, sina = cos(rad(a)), sin(rad(a))
    rotm = translate(mat(1), [-b[0], -b[1], -b[2]])
    rotm = rotm * mat([[cosa, 0, -sina, 0],
                       [   0, 1,     0, 0],
                       [sina, 0,  cosa, 0],
                       [   0, 0,     0, 1]])
    rotm = rotm * translate(mat(1), b)
    return m * rotm
    
def rotate_ox(m, b, a):
    cosa, sina = cos(rad(a)), sin(rad(a))
    rotm = translate(mat(1), [-b[0], -b[1], -b[2]])
    rotm = rotm * mat([[1,     0,    0, 0],
                       [0,  cosa, sina, 0],
                       [0, -sina, cosa, 0],
                       [0,     0,    0, 1]])
    rotm = rotm * translate(mat(1), b)
    return m * rotm
    
def scale(m, b, (sx, sy, sz)):
    tmp = translate(mat(1), [-b[0], -b[1], -b[2]])
    tmp = tmp * mat([[sx,  0,  0, 0],
                     [ 0, sy,  0, 0],
                     [ 0,  0, sz, 0],
                     [ 0,  0,  0, 1]])
    tmp = tmp * translate(mat(1), b)
    return m * tmp
    
def circle(r = 1, n = 36, h = 0):
    return [[r * cos(rad(360 / n * i)), r * sin(rad(360 / n * i)), h] for i in range(n)]
