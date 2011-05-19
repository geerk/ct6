import Tkinter as tk
import core

class App():
    def __init__(self, master):
        self.items = {}
        self.x = 0
        self.y = 0
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
        self.transformmenu = tk.Menu(self.mainmenu, tearoff=0)
        self.mainmenu.add_cascade(label = "Transform", menu = self.transformmenu)
        self.transformmenu.add_command(label = "Hide", command = self.hide)
        self.scenemenu = tk.Menu(self.mainmenu, tearoff=0)
        self.mainmenu.add_cascade(label = "Scene", menu = self.scenemenu)
        self.scenemenu.add_command(label = "Add object", command = self.add_object)
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
        frames = ("rotate", "move")
        for f in frames:
            exec 'self.%(frame)sframe = tk.LabelFrame(self.leftbar, text = "%(frame)s".title())' % {"frame":f}
            exec 'self.%(frame)sframe.grid(row = frames.index("%(frame)s"), column = 0)' % {"frame":f}
            for a in axes:
                exec '%(frame)s_%(axis)s_label = tk.Label(self.%(frame)sframe, text = "%(axis)s")' % {"axis":a, "frame":f}
                exec '%(frame)s_%(axis)s_label.grid(row = axes.index("%(axis)s"), column = 0)' % {"axis":a, "frame":f}
                exec 'self.%(frame)s_%(axis)s_entry_var = tk.StringVar(value = "0")' % {"axis":a, "frame":f}
                exec '%(frame)s_%(axis)s_entry = tk.Entry(self.%(frame)sframe, textvariable = self.%(frame)s_%(axis)s_entry_var)' % {"axis":a, "frame":f}
                exec '%(frame)s_%(axis)s_entry.grid(row = axes.index("%(axis)s"), column = 1)' % {"axis":a, "frame":f}
            exec '%(frame)sbutton = tk.Button(self.%(frame)sframe, text = "%(frame)s".title(), command = self.%(frame)sbutton_click)' % {"frame":f}
            exec '%(frame)sbutton.grid(row = 3, column = 1, sticky = tk.E)' % {"frame":f}
        
        self.deletebutton = tk.Button(self.leftbar, text = "Delete", command = self.deletebutton_click)
        self.deletebutton.grid(row = 2, column = 0)
        
        self.canvasframe = tk.LabelFrame(self.master, text = "Scene")
        self.canvasframe.grid(row = 0, column = 1)
        self.canvas = tk.Canvas(self.canvasframe, height = 500, width = 500)
        self.canvas.bind("<B1-Motion>", self.rotate)
        self.master.bind("<MouseWheel>", self.scale)
        self.canvas.grid(row = 0, column = 0)

    def add_object(self):
        self.leftbar.grid_remove()
        self.addobjectframe.grid(row = 0, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        namelabel = tk.Label(self.addobjectframe, text = "Object name")
        namelabel.grid(row = 0, column = 0)
        nameentry = tk.Entry(self.addobjectframe, width = 10)
        nameentry.grid(row = 0, column = 1)
        initpointframe = tk.LabelFrame(self.addobjectframe, text = "Init point")
        initpointframe.grid(row = 1, column = 0, columnspan = 2)
        labelx = tk.Label(initpointframe, text = "x")
        labelx.grid(row = 0, column = 0)
        labely = tk.Label(initpointframe, text = "y")
        labely.grid(row = 1, column = 0)
        labelz = tk.Label(initpointframe, text = "z")
        labelz.grid(row = 2, column = 0)
        entryx = tk.Entry(initpointframe)
        entryx.grid(row = 0, column = 1)
        entryy = tk.Entry(initpointframe)
        entryy.grid(row = 1, column = 1)
        entryz = tk.Entry(initpointframe)
        entryz.grid(row = 2, column = 1)
        addbutton = tk.Button(self.addobjectframe, text = "Add",
            command = lambda : self.addbutton_click(nameentry.get(), int(entryx.get()), int(entryy.get()), int(entryz.get())))
        addbutton.grid(row = 2, column = 0)
        cancelbutton = tk.Button(self.addobjectframe, text = "Cancel", command = self.hide_addobjectframe)
        cancelbutton.grid(row = 2, column = 1)
        
    def projectparallel(self):
        self.prtype = "parallel"
        self.draw_t(lambda i: i)

    def projectcentral(self):
        self.prtype = "central"
        self.draw_t(lambda i: i)
        
    def addbutton_click(self, name, x, y, z):
        self.objects[name] = core.Bishop(name, [x, y, z])
        self.set_curobj(name)
        self.draw_t(lambda i: i)
        self.hide_addobjectframe()
        self.objectsmenu.add_command(label = name, command = lambda : self.set_curobj(name))
    
    def set_curobj(self, name):
        self.curobj = name
        self.canvasframe.configure(text = "Scene -- Current object: " + name)
    
    def hide_addobjectframe(self):
        self.addobjectframe.grid_remove()
        self.leftbar.grid(row = 0, column = 0)
        
    def rotatebutton_click(self):
        if self.curobj:
            self.draw_t(lambda i: i.rotate([int(self.rotate_x_entry_var.get()),
                                            int(self.rotate_y_entry_var.get()),
                                            int(self.rotate_z_entry_var.get())]))

    def movebutton_click(self):
        if self.curobj:
            self.draw_t(lambda i: i.move([int(self.move_x_entry_var.get()),
                                          int(self.move_y_entry_var.get()),
                                          int(self.move_z_entry_var.get())]))

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
        if not self.curobj: return
        if self.items.has_key(self.curobj):
            for i in range(len(self.items[self.curobj])):
                self.canvas.delete(self.items[self.curobj].pop())
        else:
            self.items[self.curobj] = []
        obj = self.objects[self.curobj]
        fun(obj)
        for i in obj.get_t(self.prtype):
            self.items[self.curobj].append(self.canvas.create_polygon(i, outline = "black", fill = ""))
        
    def rotate(self, e):
        x = self.canvas.canvasx(e.x)
        y = self.canvas.canvasy(e.y)
        ox = self.x - x
        oy = self.y - y
        self.x, self.y = x, y
        self.__rotate(ox * self.rotateangle, oy * self.rotateangle, 0)()
            
    def __rotate(self, ox, oy, oz):
        return lambda : self.draw_t(lambda s: s.rotate((ox, oy, 0)))
        
    def scale(self, e):
        if e.delta < 0:
            sign = -1
        else:
            sign = 1
        self.draw_t(lambda s: s.scale(self.c, self.scale_rate * sign))
        
    def hide(self):
        pass
        
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
