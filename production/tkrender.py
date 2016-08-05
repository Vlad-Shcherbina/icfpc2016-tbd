import tkinter
from tkinter import Tk, Text, Frame, Label, Button, Canvas, Listbox, Scrollbar
from tkinter.font import Font

from typing import List, Tuple
from production.cg import Point, polygon_area
from production.ioformats import load_problem, Problem, get_root

def draw_problem(canvas, problem: Problem, size=300):
    canvas.delete(tkinter.ALL)

    # Unit square, for scale
    def toTk(points):
        res = []
        for p in points:
            res.append(round(size * p.x))
            res.append(size - 1 - round(size * p.y))
        return res
    
    default_bg = canvas.cget('bg')
    canvas.create_polygon([0, 0, size, 0, size, size, 0, size], fill=default_bg, outline='#000000', width=1)
    
    for poly in problem.silhouette:
        if polygon_area(poly) > 0:
            color = '#305030'
            tag = None
        else:
            color = default_bg
            tag = 'hole'
        canvas.create_polygon(*toTk(poly), fill=color, outline=None, tag=tag)
    
    canvas.tag_raise('hole')
    
    for line in problem.skeleton:
        canvas.create_line(*toTk(line), fill='#FF4040')

    c_bbox = canvas.bbox(tkinter.ALL)
    canvas.config(scrollregion=c_bbox, width=c_bbox[2] - c_bbox[0], height=c_bbox[3] - c_bbox[1])
    

class ProblemBrowser(object):
    def __init__(self):
        self.action = None
        self.root = root = Tk()
        root.title('Never gonna fold you up' )
        root.protocol("WM_DELETE_WINDOW", self.close)
        
        root.pack_propagate(True)
        
        scrollbar = Scrollbar(root, orient=tkinter.VERTICAL)
        self.problem_list = Listbox(root, exportselection=False, yscrollcommand=scrollbar.set)
        self.problem_list.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        scrollbar.config(command=self.problem_list.yview)
        scrollbar.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.problem_list.bind('<<ListboxSelect>>', lambda evt: self.populate_problem_canvas())
        
        self.problem_canvas = Canvas(root, bd=5, relief=tkinter.SUNKEN)
        self.problem_canvas.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        
        self.populate_problems()
        self.current_problem_name = None
        
        
    def populate_problems(self):
        self.problem_list.delete(0, tkinter.END)
        for file in sorted((get_root() / 'problems').iterdir()):
            self.problem_list.insert(tkinter.END, file.stem)
        print('Hello')
            

    def populate_problem_canvas(self):
        sel = self.problem_list.curselection()
        assert len(sel) == 1
        name = self.problem_list.get(sel[0])
        if name != self.current_problem_name:
            self.current_problem_name = name
            problem = load_problem(name)
            draw_problem(self.problem_canvas, problem)

        
    def run(self):
        self.root.mainloop()
    
    def close(self):
        if self.root:
            self.root.destroy()
            self.root = None


def main():
    ProblemBrowser().run()

if __name__ == '__main__':
    main()
