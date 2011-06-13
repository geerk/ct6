import Tkinter as tk
import tkFileDialog
import tkMessageBox
import core

class App():
    def __init__(self, master):
        self.items = {}
        self.hide = False
        self.color = "white"
        self.objects = {}
        self.curobj = ''
        self.prtype = "parallel" #type of projection
        self.cam = None
    
        self.master = master
        self.master.title("ct6")
        self.mainmenu = tk.Menu(self.master)
        self.master.config(menu = self.mainmenu)
        self.filemenu = tk.Menu(self.mainmenu, tearoff=0)
        self.mainmenu.add_cascade(label = "File", menu = self.filemenu)
        self.filemenu.add_command(label = "Save as...", command = self.save)
        self.filemenu.add_command(label = "Load", command = self.load)
        self.scenemenu = tk.Menu(self.mainmenu, tearoff=0)
        self.mainmenu.add_cascade(label = "Scene", menu = self.scenemenu)
        self.scenemenu.add_command(label = "Hide faces", command = self.hide_faces)
        self.projectionmenu = tk.Menu(self.scenemenu, tearoff=0)
        self.scenemenu.add_cascade(label = "Projection", menu = self.projectionmenu)
        self.projectionmenu.add_command(label = "Parallel", command = self.projectparallel)
        self.projectionmenu.add_command(label = "Central", command = self.projectcentral)
        self.objectsmenu = tk.Menu(self.mainmenu, tearoff=0)
        self.mainmenu.add_cascade(label = "Objects", menu = self.objectsmenu)

        self.leftbar = tk.LabelFrame(self.master, text = "Changes")
        self.leftbar.grid(row = 0, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        
        self.allobjcbvar = tk.IntVar()
        self.allobjcb = tk.Checkbutton(self.leftbar, text = "All objects", variable = self.allobjcbvar)
        self.allobjcb.grid(row = 0, column = 0)
        
        axes = ("x", "y", "z")
        frames = ("rotate", "move", "scale")
        for f in frames:
            exec 'self.%(f)sframe = tk.LabelFrame(self.leftbar, text = "%(f)s".title())' % {"f":f}
            exec 'self.%(f)sframe.grid(row = frames.index("%(f)s") + 1, column = 0)' % {"f":f}
            for a in axes:
                exec '%(f)s%(a)slabel = tk.Label(self.%(f)sframe, text = "%(a)s")' % {"a":a, "f":f}
                exec '%(f)s%(a)slabel.grid(row = axes.index("%(a)s"), column = 0)' % {"a":a, "f":f}
                exec 'self.%(f)s%(a)sevar =  tk.DoubleVar()' % {"a":a, "f":f}
                exec '%(f)s%(a)se = tk.Entry(self.%(f)sframe, textvariable = self.%(f)s%(a)sevar)' % {"a":a, "f":f}
                exec '%(f)s%(a)se.grid(row = axes.index("%(a)s"), column = 1)' % {"a":a, "f":f}
            exec 'if f == "scale": scalebclick = self.scaleb_click'
            exec 'if f in ("rotate", "move"): %(f)sbclick = lambda self = self: self.draw_t(\
                lambda i: i.%(f)s([float(self.%(f)sxevar.get()), float(self.%(f)syevar.get()), float(self.%(f)szevar.get())]))' % {"f":f}
            exec '%(f)sb = tk.Button(self.%(f)sframe, text = "%(f)s".title(), command = %(f)sbclick)' % {"f":f}
            exec '%(f)sb.grid(row = 3, column = 1, sticky = tk.E)' % {"f":f}
        
        self.deletebutton = tk.Button(self.leftbar, text = "Delete", command = self.deletebutton_click)
        self.deletebutton.grid(row = 4, column = 0)
        
        self.camlf = tk.LabelFrame(self.leftbar, text = "Camera")
        self.camlf.grid(row = 5, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        self.usecamcbvar = tk.IntVar()
        self.usecamcb = tk.Checkbutton(self.camlf, text = "Use camera", variable = self.usecamcbvar, command = self.usecamcb_click)
        self.usecamcb.grid(row = 0, column = 0)
                
        camp = ('Position x', 'Position y', 'Position z', 'Direction x', 'Direction y', 'Direction z',
            'Near clip z', 'Far clip z', 'Viewport width', 'Viewport Height', 'Angle of view')
        campv = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 50.0, 500.0, 580.0, 580.0, 90.0)
        self.camvars = {}
        for p in camp:
            name = "".join(p.lower().split())
            exec 'self.%(n)sl = tk.Label(self.camlf, text = "%(p)s", state = "disabled")' % {'n':name, 'p':p}
            exec 'self.%(n)sl.grid(row = camp.index("%(p)s") + 1, column = 0, sticky = tk.E)' % {'n':name, 'p':p}
            exec 'self.camvars["%(n)s"] = tk.DoubleVar(value = campv[camp.index("%(p)s")])' % {'n':name, 'p':p}
            exec 'self.%(n)se = tk.Entry(self.camlf, textvariable = self.camvars["%(n)s"], width = 8, state = "disabled")' % {'n':name}
            exec 'self.%(n)se.grid(row = camp.index("%(p)s") + 1, column = 1)' % {'n':name, 'p':p}
        
        self.setcamb = tk.Button(self.camlf, text = "Set cam", command = self.setcamb_click, state = "disabled")
        self.setcamb.grid(row = 1 + len(camp) + 1, column = 1)
        
        self.draw_t(lambda i: i)
        self.canvasframe = tk.LabelFrame(self.master, text = "Scene")
        self.canvasframe.grid(row = 0, column = 1, sticky=tk.N+tk.E+tk.S+tk.W)
        self.canvas = tk.Canvas(self.canvasframe, width = 580, height = 580, bg = "black")
        self.canvas.grid(row = 0, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        
        snames = ('positionx', 'directionx', 'directiony', 'directionz')
        for i in range(len(snames)):
            exec 'self.%(n)sscale = tk.Scale(self.canvasframe, orient = "horizontal",\
                from_ = -180, to = 180, length = 200, command = lambda var, self = self: self.scalecam("%(n)s", var))' % {'n':snames[i]}
            exec 'self.%(n)sscale.grid(row = i + 1, column = 0)' % {'n':snames[i]}
        
        self.paramframe = tk. LabelFrame(self.master, text = "Parameters")
        self.paramframe.grid(row = 0, column = 2, sticky=tk.N+tk.E+tk.S+tk.W)
                
        pvars = {}
        namelabel = tk.Label(self.paramframe, text = "Object name")
        namelabel.grid(row = 0, column = 0, sticky = tk.E)
        nameevar = tk.StringVar(value = "obj")
        namee = tk.Entry(self.paramframe, textvariable = nameevar, width = 10)
        namee.grid(row = 0, column = 1, sticky = tk.W)
        pvars["name"] = namee.get
        
        initpointframe = tk.LabelFrame(self.paramframe, text = "Init point")
        initpointframe.grid(row = 1, column = 0, columnspan = 2, sticky=tk.N+tk.E+tk.S+tk.W)
        names = ('init x', 'init y', 'init z')
        for n in names:
            var = "".join(n.split())
            exec '%(v)sl = tk.Label(initpointframe, text = "%(n)s")' % {'v': var, 'n': n}
            exec '%(v)sl.grid(row = names.index(n), column = 0)' % {'v': var}
            exec '%(v)sevar =  tk.DoubleVar()' % {'v':var}
            exec '%(v)se = tk.Entry(initpointframe, textvariable = %(v)sevar)' % {'v': var}
            exec '%(v)se.grid(row = names.index(n), column = 1, sticky = tk.E)' % {'v': var}
            exec 'pvars["%(v)s"] = %(v)se.get' % {'v': var} #add 'get' function to pvars
            
        nos = ('cyl A r', 'cone B bottom r cone C top r', 'cone C bottom r cone B top r', 'cone B h',
               'cone C h', 'cyl D r', 'cone I top r cyl E G r', 'cyl F r', 'cyl H r', 'cone I h', 'cyl J r',
               'cone K h', 'cone K top r', 'cone K bottom r', 'cyl M r', 'cyl N L r')
        nosv = (10.0, 30.0, 10.0, 40.0, 40.0, 15.0, 10.0, 30.0, 50.0, 100.0, 40.0, 40.0, 40.0, 70.0, 65.0, 70.0)
        i = 0
        for n in nos:
            var = "".join(n.split())
            exec '%(v)sl = tk.Label(self.paramframe, text = "%(n)s")' % {'v': var, 'n': n}
            exec '%(v)sl.grid(row = i + 2, column = 0, sticky = tk.E)' % {'v': var}
            exec '%(v)sevar =  tk.DoubleVar(value = "%(value)s")' % {'v':var, 'value': nosv[nos.index(n)]}
            exec '%(v)se = tk.Entry(self.paramframe, textvariable = %(v)sevar, width = 10)' % {'v': var}
            exec '%(v)se.grid(row = i + 2, column = 1, sticky = tk.W)' % {'v': var}
            exec 'pvars["%(v)s"] = %(v)se.get' % {'v': var} #add 'get' function to pvars
            i += 1
        
        addbutton = tk.Button(self.paramframe, text = "Add new objects",
            command = lambda self = self, pvars = pvars: self.applyparams('add', pvars))
        addbutton.grid(row = len(nos) + 2, column = 0)
        setbutton = tk.Button(self.paramframe, text = "Set params",
            command = lambda self = self, pvars = pvars: self.applyparams('set', pvars))
        setbutton.grid(row = len(nos) + 2, column = 1)

    def applyparams(self, action, vars_):
        name = callable(vars_['name']) and vars_['name']() or vars_['name']
        if action == 'add' and name in self.objects.keys():
            tkMessageBox.showerror("Wrong name!", 'Name "' + name + '" already exist.')
            return
        if action in ('add', 'set'):
            v = {}
            for key in vars_ :
                if key == 'name': continue
                if callable(vars_[key]): v[key] = float(vars_[key]())
                else:                    v[key] = float(vars_[key])
            params = {
                'name': name,
                'init_p': [v['initx'], v['inity'], v['initz']],
                'cylA': [v['cylAr'], v['cylAr'], None],
                'coneB': [v['coneCbottomrconeBtopr'], v['coneBbottomrconeCtopr'], v['coneBh']],
                'coneC': [v['coneBbottomrconeCtopr'], v['coneCbottomrconeBtopr'], v['coneCh']],
                'cylD': [v['cylDr'], v['cylDr'], None],
                'cylE': [v['coneItoprcylEGr'], v['coneItoprcylEGr'], None],
                'cylF': [v['cylFr'], v['cylFr'], None],
                'cylG': [v['coneItoprcylEGr'], v['coneItoprcylEGr'], None],
                'cylH': [v['cylHr'], v['cylHr'], None],
                'coneI': [v['coneItoprcylEGr'], None, v['coneIh']],
                'cylJ': [v['cylJr'], v['cylJr'], None],
                'coneK': [v['coneKtopr'], v['coneKbottomr'], v['coneKh']],
                'cylL': [v['cylNLr'], v['cylNLr'], None],
                'cylM': [v['cylMr'], v['cylMr'], None],
                'cylN': [v['cylNLr'], v['cylNLr'], None]
            }
        elif action == 'load':
            params = vars_
        if action in ('add', 'load'):
            try:
                self.objects[name] = core.Bishop(**params)
            except core.CoreException as e:
                tkMessageBox.showerror("Invalid parameter", e[0])
        if action == 'set':
            del params['name']
            del params['init_p']
            self.objectsmenu.delete(self.curobj)
            try:
                self.objects[self.curobj].setparams(params)
            except core.CoreException as e:
                tkMessageBox.showerror("Invalid parameter", e[0])
            name = self.curobj
        self.set_curobj(name)
        self.objectsmenu.add_command(label = name, command = lambda : self.set_curobj(name))
        
    def projectparallel(self):
        self.prtype = "parallel"
        self.draw_t(lambda i: i)

    def projectcentral(self):
        self.prtype = "central"
        self.draw_t(lambda i: i)
    
    def set_curobj(self, name):
        self.curobj = name
        self.canvasframe.configure(text = "Scene -- Current object: " + name)
        for obj in self.objects:
            if obj == self.curobj:
                self.color = "grey"
                self.draw_t(lambda i: i)
            else:
                #dirty hack
                self.color = "white"
                temp = self.curobj
                self.curobj = obj
                self.draw_t(lambda i: i)
                self.curobj = temp
                self.color = "grey"
        
    def scaleb_click(self):
        x, y, z = self.scalexevar.get(), self.scaleyevar.get(), self.scalezevar.get()
        if x < 0 or y < 0 or z < 0:
            tkMessageBox.showerror('Wrong scale rate', 'Scale rate can"t be negative')
            return
        self.draw_t(lambda i: i.scale([x, y, z]))
        
    def deletebutton_click(self):
        if self.curobj:
            for i in range(len(self.items[self.curobj])):
                self.canvas.delete(self.items[self.curobj].pop())
            del self.objects[self.curobj]
            self.objectsmenu.delete(self.curobj)
            if self.objects:
                self.set_curobj(self.objects.keys()[-1])
            else:
                self.set_curobj('')

    def usecamcb_click(self):
        if self.usecamcbvar.get() == 1:
            for i in self.camlf.winfo_children():
                i.config(state = "normal")
        else:
            self.cam = None
            for i in self.camlf.winfo_children():
                if i != self.usecamcb:
                    i.config(state = "disabled")
        self.draw_t(lambda i: i)

    def scalecam(self, typ, var):
        if self.usecamcbvar.get() == 1:
            self.camvars[typ].set(var)
            self.setcamb_click()

    def setcamb_click(self):
        self.cam = core.Camera(
            pos = [self.camvars["positionx"].get(),
                self.camvars["positiony"].get(),
                self.camvars["positionz"].get()],
            dir_ = [self.camvars["directionx"].get(),
                self.camvars["directiony"].get(),
                self.camvars["directionz"].get()],
            near_clip_z = self.camvars["nearclipz"].get(),
            far_clip_z = self.camvars["farclipz"].get(),
            viewport_width = self.camvars["viewportwidth"].get(),
            viewport_height = self.camvars["viewportheight"].get(),
            fov = self.camvars["angleofview"].get())
        print repr(self.cam)
        self.draw_t(lambda i: i)

    def draw_t(self, fun):
        if not self.curobj: return
        objects = [self.curobj]
        if self.allobjcbvar.get() == 1:
            objects = [obj for obj in self.objects]
        for k in objects:
            if self.items.has_key(k):
                for i in range(len(self.items[k])):
                    self.canvas.delete(self.items[k].pop())
            else:
                self.items[k] = []
            obj = self.objects[k]
            fun(obj)
            if self.cam: self.cam.cull_obj(obj)
            if obj.state == 'visible':
                for i in obj.get_t(self.prtype, self.hide, self.cam):
                    self.items[k].append(self.canvas.create_polygon(i, outline = self.color, fill = self.hide and "black" or ""))
        
    def hide_faces(self):
        if self.hide: self.scenemenu.entryconfigure(0, label =   "Hide faces")
        else:         self.scenemenu.entryconfigure(0, label = "Unhide faces")
        self.hide = not self.hide
        self.draw_t(lambda i: i)
        
    def load(self):
        filename = tkFileDialog.askopenfilename(defaultextension=".scene")
        if filename:
            for key in self.objects:
                self.objectsmenu.delete(key)
            self.objects.clear()
            l = {'objects':{}, 'cam':{}}
            execfile(filename, l)
            for key in l['objects']:
                self.applyparams('load', l['objects'][key])
            self.cam = core.Camera(l['cam'])
        
    def save(self):
        filename = tkFileDialog.asksaveasfilename(defaultextension=".scene")
        if filename:
            s = 'objects = {\\\n'
            for obj in self.objects:
                s += '"' + obj + '": ' + repr(self.objects[obj]) + ',\n'
            s += '}\ncam = ' + repr(self.cam)
            open(filename, "w").write(s)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
