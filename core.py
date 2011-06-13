from math import cos, sin, tan, pi, sqrt
from math import radians as rad
import transform as tr
from matrix import matrix as mat

class CoreException(Exception): pass
class NegativeException(CoreException): pass
class BadRadiusException(CoreException): pass

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
        
        self.state = 'visible'
        self.c = []
        self.shapes = {}
        self.max_radius = 0
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
                        
                        if params[key][i] == None: continue
                        if params[key][i] < 0: raise NegativeException("Parameters can't be negative")
                        self.%s[i] = params[key][i]""" % (key, key)
        
        if self.cylM[1] > self.cylN[0]: raise BadRadiusException('Radius cyl M must be less then radius cyl N')
        if self.cylD[0] > self.cylF[0]: raise BadRadiusException('Radius cyl D must be less then radius cyl F')
        if self.cylF[0] > self.cylH[0]: raise BadRadiusException('Radius cyl F must be less then radius cyl H')
        if self.mat == mat(1): self.mat = tr.translate(self.mat, self.init_p)
        self.namesofshapes = ('cylA', 'coneB', 'coneC', 'cylD', 'cylE','cylF', 'cylG',
                              'cylH', 'coneI', 'cylJ', 'coneK', 'cylL', 'cylM', 'cylN')
        self.c = self.init_p[:]
        #calculating base point (for rotation, scaling, etc.)
        for j in [getattr(self, i)[2] for i in self.namesofshapes]: self.c[2] += j / 2.0
        
        tmp_init_p = [0, 0, 0]
        for name in self.namesofshapes:
            sh = getattr(self, name)[:]
            maxr = sqrt((tmp_init_p[2] - self.c[2]) ** 2 + (sh[0] > sh[1] and sh[0] or sh[1]) ** 2)#may cause bug
            self.max_radius = maxr > self.max_radius and maxr or self.max_radius#may cause bug
            self.shapes[name] = Cone(tmp_init_p[:], getattr(self, name))
            tmp_init_p[2] += getattr(self, name)[2]

    def get_c(self):
        return (mat([self.c[:] + [1]]) * self.mat).tolist()[0][:3]

    def __cmpt(self, t1, t2):
        """compare two triangles by z axis"""
        d1 = min([k[2] for k in t1])
        d2 = min([k[2] for k in t2])
        if d1 < d2: return -1
        if d1 > d2: return 1
        return 0

    def get_t(self, prtype, hide, cam = None):
        t = []
        for i in self.shapes.values():
            i.transform(self.mat)
            t += i.t
        if hide: t.sort(self.__cmpt)
        if cam: return [[cam.world2scr(v) for v in i] for i in t]
        return self.project(t, prtype)
    def rotate(self, angles):
        self.mat = tr.rotate(self.mat, self.c, angles)
    
    def move(self, vec):
        self.mat = tr.translate(self.mat, vec)
        self.c = [self.c[0] + vec[0], self.c[1] + vec[1], self.c[2] + vec[2]]
        
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
        
class Camera(object):
    def __init__(self, **kwargs):
        self.pos = kwargs['pos'][:]
        self.dir_ = kwargs['dir_'][:]
        self.near_clip_z = kwargs['near_clip_z']
        self.far_clip_z = kwargs['far_clip_z']
        self.viewport_width = kwargs['viewport_width']
        self.viewport_height = kwargs['viewport_height']
        self.viewport_center_x = (self.viewport_width - 1) / 2
        self.viewport_center_y = (self.viewport_height - 1) / 2
        self.aspect_ratio = float(self.viewport_width) / float(self.viewport_height)
        if kwargs.has_key('mcam'): self.mcam = kwargs['mcam']
        else:                      self.mcam = mat(1)
        self.fov = kwargs['fov']
        self.viewplane_width = 2.0
        self.viewplane_height = 2.0 / self.aspect_ratio
        self.view_dist = 0.5 * self.viewplane_width * tan(rad(self.fov / 2.0))
        #init mcam:
        self.mcam = tr.translate(self.mcam, (-self.pos[0], -self.pos[1], -self.pos[2]))
        (mat_oz, mat_oy, mat_ox) = tr.camat(self.dir_)
        self.mcam = self.mcam * mat_oz
        self.mcam = self.mcam * mat_oy
        self.mcam = self.mcam * mat_ox
        
    def cull_obj(self, obj):
        obj.state = 'visible'
        sphere_pos = self.world2cam(obj.get_c())
        if (sphere_pos[2] - obj.max_radius) > self.far_clip_z or (sphere_pos[2] + obj.max_radius) < self.near_clip_z:
            obj.state = 'culled'
            return
        z_test = 0.5 * self.viewplane_width * sphere_pos[2] / self.view_dist
        if (sphere_pos[0] - obj.max_radius) > z_test or (sphere_pos[0] + obj.max_radius) < -z_test:
            obj.state = 'culled'
            return
        z_test = 0.5 * self.viewplane_height * sphere_pos[2] / self.view_dist
        if (sphere_pos[1] - obj.max_radius) > z_test or (sphere_pos[1] + obj.max_radius) < -z_test:
            obj.state = 'culled'

    def world2cam(self, v):
        return (mat([v + [1]]) * self.mcam).tolist()[0][:3]
        
    def cam2scr(self, v):
        return [self.view_dist * v[0] / v[2], self.view_dist * v[1] * self.aspect_ratio / v[2]]
        
    def world2scr(self, v):
        alpha = 0.5 * self.viewport_width - 0.5
        beta = 0.5 * self.viewport_height - 0.5
        r = self.cam2scr(self.world2cam(v))
        r = [alpha + alpha * r[0], beta - beta * r[1]]
        return r
        
    def __repr__(self):
        return  '{\\\n\t"pos": ' + repr(self.pos) + ',\\\n' + \
                 '\t"dir_": ' + repr(self.dir_) + ',\\\n' + \
                 '\t"near_clip_z": ' + repr(self.near_clip_z) + ',\\\n' + \
                 '\t"far_clip_z": ' + repr(self.far_clip_z) + ',\\\n' + \
                 '\t"viewport_width": ' + repr(self.viewport_width) + ',\\\n' + \
                 '\t"viewport_height": ' + repr(self.viewport_height) + ',\\\n' + \
                 '\t"fov": ' + repr(self.fov) + ',\\\n' + \
                 '\t"mcam": ' + repr(self.mcam) + ',\\\n}'
