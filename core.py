import transform as tr
from matrix import matrix as mat

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
        self.mat = mat(1)
        
        self.c = []
        self.shapes = {}
        
        self.setparams(kwargs)

    def setparams(self, params):
        for key in params:
            if key in ('name', 'init_p'):
                exec 'self.%s = params[key]' % (key, )
                continue
            if key == 'mat':
                self.mat = mat(params[key])
                continue
            exec """for i in range(len(self.%s)):
                        if params[key][i]:
                            self.%s[i] = params[key][i]""" % (key, key)
        
        if self.mat == mat(1): self.mat = tr.translate(self.mat, self.init_p)
        self.namesofshapes = ('cylA', 'coneB', 'coneC', 'cylD', 'cylE','cylF', 'cylG',
                              'cylH', 'coneI', 'cylJ', 'coneK', 'cylL', 'cylM', 'cylN')
        self.c = self.init_p[:]
        #calculating base point (for rotation, scaling, etc.)
        for j in [getattr(self, i)[2] for i in self.namesofshapes]: self.c[2] += j / 2.0
        
        tmp_init_p = [0, 0, 0]
        for name in self.namesofshapes:
            self.shapes[name] = Cone(tmp_init_p[:], getattr(self, name))
            tmp_init_p[2] += getattr(self, name)[2]

    def cmpt(self, t1, t2):
        """compare two triangles by z axis"""
        d1 = min([k[2] for k in t1])
        d2 = min([k[2] for k in t2])
        if d1 < d2: return -1
        if d1 > d2: return 1
        return 0

    def get_t(self, prtype, hide):
        t = []
        for i in self.shapes.values():
            i.transform(self.mat)
            t += i.t
        if hide: t.sort(self.cmpt)
        return self.project(t, prtype)
        
    def rotate(self, angles):
        self.mat = tr.rotate(self.mat, self.c, angles)
    
    def move(self, vec):
        self.mat = tr.translate(self.mat, vec)
        
    def scale(self, rates):
        self.mat = tr.scale(self.mat, self.c, rates)
        
    def project(self, t, prtype):
        return [[tr.project(j, prtype) for j in i] for i in t]
        
    def __repr__(self):
        #do not change, it's write-only
        s =  '{\\\n\t"name": ' + repr(self.name) + ',\\\n' + \
                '\t"init_p": ' + repr(self.init_p) + ',\\\n'
        for name in self.namesofshapes:
            s += '\t"' + name + '":' + repr(getattr(self, name)) + ',\\\n'
        s += '\t"mat": ' + repr(self.mat) + '\\\n'
        return s + '}'
        
class Cone(object):
    def __init__(self, init_p, (r1, r2, h), n = 9):
        self.v = tuple() #vertex
        self.t = [] #triangles
        #radius, height, number of sectors:
        self.init_p, self.r1, self.r2, self.h, self.n = init_p, r1, r2, h, n
        self.__make_vertex()
        
    def __make_vertex(self):
        r1, r2, h, n = self.r1, self.r2, self.h, self.n
        #vertex:
        v = tr.circle(r1, n, 0)
        v += tr.circle(r2, n, h)
        v += [[0, 0, 0], [0, 0, h]]
        self.v = tuple([[float(j) for j in i] for i in v])
        
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
        
    def transform(self, m):
        v = [tr.translate(mat([i + [1]]), self.init_p).tolist()[0][:3] for i in self.v]
        v = [(mat([i + [1]]) * m).tolist()[0][:3] for i in v]
        self.__make_polygons(v)
