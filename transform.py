from math import cos, sin, pi
from math import radians as rad
from matrix import matrix as mat

def project(p, type = "ortho", c = 10):
    if type == "ortho":
        return (mat([p + [1]]) * mat([[1, 0, 0, 0],
                                      [0, 1, 0, 0],
                                      [0, 0, 0, 0],
                                      [0, 0, 0, 1]])).tolist()[0][:2]
    elif type == "oblique":
        return (mat([p + [1]]) * mat([[   1,    0, 0, 0],
                                      [   0,    1, 0, 0],
                                      [pi/4, pi/4, 0, 0],
                                      [   0,    0, 0, 1]])).tolist()[0][:2]
    elif type == "central":
        vec = (mat([p + [1]]) * mat([[1, 0, 0,   0],
                                     [0, 1, 0,   0],
                                     [0, 0, 0,   0],
                                     [0, 0, 1/c, 1]])).tolist()[0]
        return [vec[0]/vec[3], vec[1]/vec[3]]

def translate(p, (m, n, l)):
    return (mat([p + [1]]) * mat([[1, 0, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [m, n, l, 1]])).tolist()[0][:3]

def rotate_oz(p, b, a):
    cosa, sina = cos(rad(a)), sin(rad(a))
    p = translate(p, (-b[0], -b[1], -b[2]))
    p =    (mat([p + [1]]) * mat([[ cosa, sina, 0, 0],
                                  [-sina, cosa, 0, 0],
                                  [    0,    0, 1, 0],
                                  [    0,    0, 0, 1]])).tolist()[0][:3]
    return translate(p, b)
    
def rotate_oy(p, b, a):
    cosa, sina = cos(rad(a)), sin(rad(a))
    p = translate(p, (-b[0], -b[1], -b[2]))
    p =    (mat([p + [1]]) * mat([[cosa, 0, -sina, 0],
                                  [   0, 1,     0, 0],
                                  [sina, 0,  cosa, 0],
                                  [   0, 0,     0, 1]])).tolist()[0][:3]
    return translate(p, b)
    
def rotate_ox(p, b, a):
    cosa, sina = cos(rad(a)), sin(rad(a))
    p = translate(p, (-b[0], -b[1], -b[2]))
    p =    (mat([p + [1]]) * mat([[1,     0,    0, 0],
                                  [0,  cosa, sina, 0],
                                  [0, -sina, cosa, 0],
                                  [0,     0,    0, 1]])).tolist()[0][:3]
    return translate(p, b)
    
def scale(p, b, sx, sy, sz):
    return translate((mat([translate(p, (-b[0], -b[1], -b[2])) + [1]]) * 
                      mat([[sx,  0,  0, 0],
                           [ 0, sy,  0, 0],
                           [ 0,  0, sz, 0],
                           [ 0,  0,  0, 1]])).tolist()[0][:3], b)
    
def circle(r = 1, n = 36):
    return [[r * cos(rad(360 / n * i)), r * sin(rad(360 / n * i)), 0] for i in range(n)]
