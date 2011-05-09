import transform as tr

class Bishop(object):
    def __init__(self, name, init_p):
        self.name = name
        self.init_p = init_p
        self.c = self.init_p[:]
        self.params = [[10, 10,  5],
                       [10, 30, 40],
                       [30, 10, 40],
                       [15, 15,  5],
                       [10, 10, 15],
                       [30, 30, 10],
                       [10, 10,  5],
                       [50, 50, 10],
                       [10, 30, 100],
                       [40, 40, 20],
                       [40, 70, 40],
                       [70, 70,  5],
                       [65, 65,  5],
                       [70, 70, 10]]
        self.shapes = []
        tmp_init_p = self.init_p[:]
        for i in self.params:
            self.shapes.append(Cone(tmp_init_p[:], i))
            tmp_init_p[2] += i[2]
        self.c[2] = tmp_init_p[2] / 2
            
    def get_t(self):
        t = []
        for i in self.shapes:
            t += i.project()
        return t
    
    def rotate(self, ox, oy, oz):
        for i in self.shapes:
            i.rotate(self.c[:], ox, oy, oz)
        
class Cone(object):
    def __init__(self, init_p, (r1, r2, h), n = 9):
        self.v = tuple() #vertex
        self.t = [] #triangles
        #radius, height, number of sectors:
        self.init_p, self.r1, self.r2, self.h, self.n = init_p, r1, r2, h, n
        self.rotate_point = self.scale_point = self.init_p
        self.ox_angle = self.oy_angle = self.oz_angle = 0 #rotation angles
        self.sx = self.sy = self.sz = 1 #scale rate
        self.__make_vertex()
        self.__draw()
        
    def __make_vertex(self):
        r1, r2, h, n = self.r1, self.r2, self.h, self.n
        #vertex:
        v = tr.circle(r1, n)
        v += [tr.translate(i, [0, 0, h]) for i in tr.circle(r2, n)]
        v += [[0, 0, 0], [0, 0, h]]
        self.v = tuple(v)
        
    def __make_polygons(self, v):
        n = self.n
        t = [] #triangles
        for i in range(n):
            i2 = (i + 1) % n
            t += [[v[2 * n], v[i], v[i2]]]
            t += [[v[2 * n + 1], v[n + i], v[n + i2]]]
            t += [[v[i], v[n + i2], v[i2]]]
        self.t = t
        
    def __draw(self):
        """Applies all changes then make and return polygons"""
        v = self.v
        v = [tr.translate(i, self.init_p) for i in v]
        if self.ox_angle:
            v = [tr.rotate_ox(i, self.rotate_point, self.ox_angle) for i in v]
        if self.oy_angle:
            v = [tr.rotate_oy(i, self.rotate_point, self.oy_angle) for i in v]
        if self.oz_angle:
            v = [tr.rotate_oz(i, self.rotate_point, self.oz_angle) for i in v]
        v = [tr.scale(i, self.scale_point, self.sx, self.sy, self.sz) for i in v]
        self.__make_polygons(v)
        
    def project(self):
        return [[tr.project(j) for j in i] for i in self.t]
        
    def translate(self, vec):
        self.init_p = vec
        self.__draw()
        
    def rotate(self, base, oxa, oya, oza):
        self.rotate_point = base
        self.ox_angle += oxa
        self.oy_angle += oya
        self.oz_angle += oza
        self.__draw()
        
    def scale(self, base, s):
        self.scale_point = base
        self.sx += s
        self.sy += s
        self.sz += s
        self.__draw()
