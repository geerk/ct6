import transform as tr

class Bishop(object):
    def __init__(self, **kwargs):
        self.name = 'obj'
        self.init_p = [0, 0, 0]
        self.cylA = [10, 10, 5]
        self.coneB = [10, 30, 40]
        self.coneC = [30, 10, 40]
        self.cylD = [15, 15,  5]
        self.cylE = [10, 10, 15]
        self.cylF = [30, 30, 10]
        self.cylG = [10, 10,  5]
        self.cylH = [50, 50, 10]
        self.coneI = [10, 30, 100]
        self.cylJ = [40, 40, 20]
        self.coneK = [40, 70, 40]
        self.cylL = [70, 70,  5]
        self.cylM = [65, 65,  5]
        self.cylN = [70, 70, 10]
        self.oxa = 0
        self.oya = 0
        self.oza = 0
        self.sx = 1
        self.sy = 1
        self.sz = 1
        
        for key in kwargs:
            exec 'self.%s = kwargs[key]' % (key, ) #to add a test
        
        self.namesofshapes = ('cylA', 'coneB', 'coneC', 'cylD', 'cylE',
                              'cylF', 'cylG', 'cylH', 'coneI', 'cylJ',
                              'coneK', 'cylL', 'cylM', 'cylN')
        self.c = self.init_p[:]
        #calculating base point (for rotation, scaling, etc.)
        for j in [getattr(self, i)[2] for i in self.namesofshapes]: self.c[2] += j / 2.0
        self.shapes = {}
        tmp_init_p = self.init_p[:]
        modifparams = [self.oxa, self.oya, self.oza, self.sx, self.sy, self.sz]
        for name in self.namesofshapes:
            params = getattr(self, name) + modifparams
            self.shapes[name] = Cone(tmp_init_p[:], self.c[:], params)
            tmp_init_p[2] += params[2]
            
    def get_t(self, prtype):
        t = []
        for i in self.shapes.values():
            t += i.project(prtype)
        return t
    
    def rotate(self, (ox, oy, oz)):
        self.oxa += ox
        self.oya += oy
        self.oza += oz
        for i in self.shapes.values():
            i.rotate(self.c[:], self.oxa, self.oya, self.oza)
            
    def move(self, vec):
        for i in range(len(vec)):
            self.init_p[i] += vec[i]
            self.c[i] += vec[i]
        for i in self.shapes.values():
            i.move(vec)
    
    def __repr__(self):
        #do not change, it's write-only
        s =  '{\\\n\t"name": ' + repr(self.name) + ',\\\n' + \
                '\t"init_p": ' + repr(self.init_p) + ',\\\n'
        for name in self.namesofshapes:
            s += '\t"' + name + '":' + repr(getattr(self, name)) + ',\\\n'
        for axis in ('x', 'y', 'z'):
            exec 's += "\\t\'o%(a)sa\':" + repr(self.o%(a)sa) + ",\\\\\\n"' % {"a":axis}
            exec 's += "\\t\'s%(a)s\':" + repr(self.s%(a)s) + ",\\\\\\n"' % {"a":axis}
        return s + '}'
        
class Cone(object):
    def __init__(self, init_p, base, (r1, r2, h, oxa, oya, oza, sx, sy, sz), n = 9):
        self.v = tuple() #vertex
        self.t = [] #triangles
        #radius, height, number of sectors:
        self.init_p, self.r1, self.r2, self.h, self.n = init_p, r1, r2, h, n
        self.rotate_point = self.scale_point = base
        self.ox_angle, self.oy_angle, self.oz_angle = oxa, oya, oza #rotation angles
        self.sx, self.sy, self.sz = sx, sy, sz #scale rate
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
        c1 = v[0:n]
        c2 = v[n:n+n]
        for i in range(n):
            t += [[c1[i], c2[i], c1[i+1-n]]]
            t += [[c1[i], c2[i], c2[i-1]]]
            t += [[c1[i], c1[i+1-n], v[n+n]]]
            t += [[c2[i], c2[i+1-n], v[n+n+1]]]
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
        
    def project(self, prtype):
        return [[tr.project(j, prtype) for j in i] for i in self.t]
        
    def translate(self, vec):
        self.init_p = vec
        self.__draw()
        
    def move(self, vec):
        for i in range(len(vec)):
            self.init_p[i] += vec[i]
        self.__draw()
        
    def rotate(self, base, oxa, oya, oza):
        self.rotate_point = base
        self.ox_angle = oxa
        self.oy_angle = oya
        self.oz_angle = oza
        self.__draw()
        
    def scale(self, base, sx, sy, sz):
        self.scale_point = base
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.__draw()
