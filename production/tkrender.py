import tkinter
from tkinter import Tk, Text, Frame, Label, Button, Canvas, Listbox, Scrollbar
from tkinter.font import Font

from typing import List, Tuple
from production.cg import Point, polygon_area
from production.ioformats import load_problem, Problem, get_root


def get_canvas_coord_mapping(canvas, points):
    min_x = float(min(p.x for p in points))
    max_x = float(max(p.x for p in points))
    min_y = float(min(p.y for p in points))
    max_y = float(max(p.y for p in points))

    view_width = canvas.winfo_width()
    view_height = canvas.winfo_height()


    ratio_x = view_width / (max_x - min_x)
    ratio_y = view_height / (max_y - min_y)

    # preserve aspect with letterboxing
    ratio = min(ratio_x, ratio_y) * 0.9
    letterbox_x = (1 - ratio / ratio_x) * view_width / 2
    letterbox_y = (1 - ratio / ratio_y) * view_height / 2

    def mapping(points):
        res = []
        for p in points:
            res.append(round((p.x - min_x) * ratio + letterbox_x))
            res.append(view_height - 1 - round((p.y - min_y) * ratio + letterbox_y))
        return res

    return mapping





def draw_problem(canvas, problem: Problem, size=500):
    canvas.delete(tkinter.ALL)

    points = sum(problem.silhouette, [])
    points.append(Point(0, 0))
    points.append(Point(1, 1))

    toTk = get_canvas_coord_mapping(canvas, points)


    default_bg = canvas.cget('bg')

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

    # Unit square, for scale
    canvas.create_polygon(*toTk([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)]),
            fill='', outline='#4040FF', width=3, dash=(15, 15))



class ProblemBrowser(object):
    def __init__(self):
        self.action = None
        self.root = root = Tk()
        root.title('Never gonna fold you up')
        root.protocol("WM_DELETE_WINDOW", self.close)

        root.pack_propagate(True)

        scrollbar = Scrollbar(root, orient=tkinter.VERTICAL)
        self.problem_list = Listbox(root, exportselection=False, yscrollcommand=scrollbar.set)
        self.problem_list.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        scrollbar.config(command=self.problem_list.yview)
        scrollbar.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.problem_list.bind('<<ListboxSelect>>', lambda evt: self.populate_problem_canvas())

        self.problem_canvas = Canvas(root, bd=1, relief=tkinter.SUNKEN, width=500, height=500)
        self.problem_canvas.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.problem_canvas.bind("<Configure>", lambda evt: self.populate_problem_canvas())

        self.populate_problems()
        self.current_problem_name = None
        self.current_problem = None


    def populate_problems(self):
        self.problem_list.delete(0, tkinter.END)
        for file in sorted((get_root() / 'problems').iterdir()):
            self.problem_list.insert(tkinter.END, file.stem)


    def populate_problem_canvas(self):
        sel = self.problem_list.curselection()
        if not sel: return
        assert len(sel) == 1
        name = self.problem_list.get(sel[0])
        if name != self.current_problem_name:
            self.current_problem_name = name
            self.current_problem = load_problem(name)
        if self.current_problem:
            draw_problem(self.problem_canvas, self.current_problem)


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
