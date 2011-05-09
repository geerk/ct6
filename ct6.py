import Tkinter as tk
import core

class App():
    def __init__(self, master):
        self.master = master
        self.mainmenu = tk.Menu(self.master)
        self.master.config(menu = self.mainmenu)
        self.filemenu = tk.Menu(self.mainmenu)
        self.mainmenu.add_cascade(label = "File", menu = self.filemenu)
        self.transformmenu = tk.Menu(self.mainmenu)
        self.mainmenu.add_cascade(label = "Transform", menu = self.transformmenu)
        self.transformmenu.add_command(label = "Hide", command = self.hide)
        self.scenemenu = tk.Menu(self.mainmenu)
        self.mainmenu.add_cascade(label = "Scene", menu = self.scenemenu)
        self.scenemenu.add_command(label = "Add object", command = self.add_object)
        self.objectsmenu = tk.Menu(self.mainmenu)
        self.mainmenu.add_cascade(label = "Objects", menu = self.objectsmenu)

        self.addobjectframe = tk.LabelFrame(self.master, text = "Add object")
        self.leftbar = tk.LabelFrame(self.master, text = "Changes")
        self.leftbar.grid(row = 0, column = 0, sticky=tk.N+tk.E+tk.S+tk.W)
        
        self.rotationframe = tk.LabelFrame(self.leftbar, text = "Rotation")
        self.rotationframe.grid(row = 0, column = 0)
        
        self.rotate_x_label = tk.Label(self.rotationframe, text = "x")
        self.rotate_x_label.grid(row = 0, column = 0)
        self.rotate_x_entry_var = tk.StringVar(value = "0")
        self.rotate_x_entry = tk.Entry(self.rotationframe, textvariable = self.rotate_x_entry_var)
        self.rotate_x_entry.grid(row = 0, column = 1)
        
        self.rotate_y_label = tk.Label(self.rotationframe, text = "y")
        self.rotate_y_label.grid(row = 1, column = 0)
        self.rotate_y_entry_var = tk.StringVar(value = "0")
        self.rotate_y_entry = tk.Entry(self.rotationframe, textvariable = self.rotate_y_entry_var)
        self.rotate_y_entry.grid(row = 1, column = 1)
        
        self.rotate_z_label = tk.Label(self.rotationframe, text = "z")
        self.rotate_z_label.grid(row = 2, column = 0)
        self.rotate_z_entry_var = tk.StringVar(value = "0")
        self.rotate_z_entry = tk.Entry(self.rotationframe, textvariable = self.rotate_z_entry_var)
        self.rotate_z_entry.grid(row = 2, column = 1)
        
        self.rotatebutton = tk.Button(self.rotationframe, text = "Rotate", command = self.rotatebutton_click)
        self.rotatebutton.grid(row = 3, column = 1, sticky = tk.E)
        
        self.moveframe = tk.LabelFrame(self.leftbar, text = "Move")
        self.moveframe.grid(row = 1, column = 0)
        
        
        
        self.canvasframe = tk.LabelFrame(self.master, text = "Scene")
        self.canvasframe.grid(row = 0, column = 1)
        self.canvas = tk.Canvas(self.canvasframe, height = 500, width = 500)
        self.canvas.bind("<B1-Motion>", self.rotate)
        self.master.bind("<MouseWheel>", self.scale)
        self.canvas.grid(row = 0, column = 0)
        
        self.items = {}
        self.x = 0
        self.y = 0
        self.angle = 0.1
        self.scale_rate = 0.05
        self.objects = {}
        self.curobj = ""

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
        self.__rotate(int(self.rotate_x_entry_var.get()),
                      int(self.rotate_y_entry_var.get()),
                      int(self.rotate_z_entry_var.get()))()
  
    def draw_t(self, fun):
        if self.items.has_key(self.curobj):
            for i in range(len(self.items[self.curobj])):
                self.canvas.delete(self.items[self.curobj].pop())
        else:
            self.items[self.curobj] = []
        obj = self.objects[self.curobj]
        fun(obj)
        for i in obj.get_t():
            self.items[self.curobj].append(self.canvas.create_polygon(i, outline = "black", fill = ""))
        
    def rotate(self, e):
        x = self.canvas.canvasx(e.x)
        y = self.canvas.canvasy(e.y)
        ox = self.x - x
        oy = y - self.y
        self.x, self.y = x, y
        self.__rotate(ox, oy, 0)()
            
    def __rotate(self, ox, oy, oz):
        return lambda : self.draw_t(lambda s: s.rotate(ox * self.angle, oy * self.angle, 0))
        
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
