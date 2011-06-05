import Tkinter as tk
import tkFileDialog
import core

class App():
    def __init__(self, master):
        self.items = {}
        self.x = 0
        self.y = 0
        self.hide = False
        self.color = "white"
        self.rotateangle = 1
        self.scale_rate = 0.05
        self.objects = {}
        self.curobj = ''
        self.prtype = "parallel" #type of projection
    
        self.master = master
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

        self.addobjectframe = tk.LabelFrame(self.master, text = "Add object")
        self.leftbar = tk.LabelFrame(self.master, text = "Changes")
        self.leftbar.grid(row = 0, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        
        axes = ("x", "y", "z")
        frames = ("rotate", "move", "scale")
        for f in frames:
            exec 'self.%(f)sframe = tk.LabelFrame(self.leftbar, text = "%(f)s".title())' % {"f":f}
            exec 'self.%(f)sframe.grid(row = frames.index("%(f)s"), column = 0)' % {"f":f}
            for a in axes:
                exec '%(f)s%(a)slabel = tk.Label(self.%(f)sframe, text = "%(a)s")' % {"a":a, "f":f}
                exec '%(f)s%(a)slabel.grid(row = axes.index("%(a)s"), column = 0)' % {"a":a, "f":f}
                exec 'self.%(f)s%(a)sevar = tk.StringVar(value = "0")' % {"a":a, "f":f}
                exec '%(f)s%(a)se = tk.Entry(self.%(f)sframe, textvariable = self.%(f)s%(a)sevar)' % {"a":a, "f":f}
                exec '%(f)s%(a)se.grid(row = axes.index("%(a)s"), column = 1)' % {"a":a, "f":f}
            exec 'self.%(f)sbclick = lambda self = self: self.draw_t(\
                lambda i: i.%(f)s([float(self.%(f)sxevar.get()), float(self.%(f)syevar.get()), float(self.%(f)szevar.get())]))' % {"f":f}
            exec '%(f)sb = tk.Button(self.%(f)sframe, text = "%(f)s".title(), command = self.%(f)sbclick)' % {"f":f}
            exec '%(f)sb.grid(row = 3, column = 1, sticky = tk.E)' % {"f":f}
        
        self.deletebutton = tk.Button(self.leftbar, text = "Delete", command = self.deletebutton_click)
        self.deletebutton.grid(row = 3, column = 0)
        self.draw_t(lambda i: i)
        self.canvasframe = tk.LabelFrame(self.master, text = "Scene")
        self.canvasframe.grid(row = 0, column = 1)
        self.canvas = tk.Canvas(self.canvasframe, height = 500, width = 500, bg = "black")
        self.canvas.grid(row = 0, column = 0)
        
        self.paramframe = tk. LabelFrame(self.master, text = "Parameters")
        self.paramframe.grid(row = 0, column = 2, sticky=tk.N+tk.E+tk.S+tk.W)
                
        pvars = {}
        namelabel = tk.Label(self.paramframe, text = "Object name")
        namelabel.grid(row = 0, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        nameevar = tk.StringVar(value = "obj")
        namee = tk.Entry(self.paramframe, textvariable = nameevar, width = 10)
        namee.grid(row = 0, column = 1)
        pvars["name"] = namee.get
        
        initpointframe = tk.LabelFrame(self.paramframe, text = "Init point")
        initpointframe.grid(row = 1, column = 0, columnspan = 2, sticky=tk.N+tk.E+tk.S+tk.W)
        names = ('init x', 'init y', 'init z')
        for n in names:
            var = "".join(n.split())
            exec '%(v)sl = tk.Label(initpointframe, text = "%(n)s")' % {'v': var, 'n': n}
            exec '%(v)sl.grid(row = names.index(n), column = 0)' % {'v': var}
            exec '%(v)sevar = tk.StringVar(value = "0")' % {'v':var}
            exec '%(v)se = tk.Entry(initpointframe, textvariable = %(v)sevar)' % {'v': var}
            exec '%(v)se.grid(row = names.index(n), column = 1)' % {'v': var}
            exec 'pvars["%(v)s"] = %(v)se.get' % {'v': var} #add 'get' function to pvars
            
        nos = {'cyl A r': 10, 'cone B bottom r cone C top r': 30, 'cone C bottom r cone B top r': 10,
               'cone B h': 40, 'cone C h': 40, 'cyl D r': 15, 'cone I top r cyl E G r': 10,
               'cyl F r': 30, 'cyl H r': 50, 'cone I h': 100, 'cyl J r': 40,
               'cone K h': 40, 'cone K top r': 40, 'cone K bottom r': 70, 'cyl M r': 65, 'cyl N L r': 70}
        i = 0
        for n in nos:
            var = "".join(n.split())
            exec '%(v)sl = tk.Label(self.paramframe, text = "%(n)s")' % {'v': var, 'n': n}
            exec '%(v)sl.grid(row = i + 2, column = 0)' % {'v': var}
            exec '%(v)sevar = tk.StringVar(value = "%(value)s")' % {'v':var, 'value': str(nos[n])}
            exec '%(v)se = tk.Entry(self.paramframe, textvariable = %(v)sevar)' % {'v': var}
            exec '%(v)se.grid(row = i + 2, column = 1)' % {'v': var}
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
            self.objects[name] = core.Bishop(**params)
        if action == 'set':
            del params['name']
            del params['init_p']
            self.objectsmenu.delete(self.curobj)
            self.objects[self.curobj].setparams(params)
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

    def draw_t(self, fun):
        try:
            if not self.curobj: return
            if self.items.has_key(self.curobj):
                for i in range(len(self.items[self.curobj])):
                    self.canvas.delete(self.items[self.curobj].pop())
            else:
                self.items[self.curobj] = []
            obj = self.objects[self.curobj]
            fun(obj)
            for i in obj.get_t(self.prtype, self.hide):
                self.items[self.curobj].append(self.canvas.create_polygon(i, outline = self.color, fill = self.hide and "black" or ""))
        except Exception as e:
            print e
        
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
            l = {'objects':{}}
            execfile(filename, l)
            for key in l['objects']:
                self.applyparams('load', l['objects'][key])
        
    def save(self):
        filename = tkFileDialog.asksaveasfilename(defaultextension=".scene")
        if filename:
            s = 'objects = {\\\n'
            for obj in self.objects:
                s += '"' + obj + '": ' + repr(self.objects[obj]) + ',\n'
            open(filename, "w").write(s + '}')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
