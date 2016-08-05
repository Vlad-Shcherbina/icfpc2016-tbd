import tkinter
from tkinter import Tk, Text, Frame, Label, Button, Canvas, Listbox, Scrollbar, IntVar, Checkbutton
from tkinter.font import Font

from typing import List, Tuple
from production.cg import Point, polygon_area
from production.ioformats import load_problem, Problem, get_root, Solution, center_problem
from production import meshes

def get_canvas_coord_mapping(canvas, points):
    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    view_width = canvas.winfo_width()
    view_height = canvas.winfo_height()


    ratio_x = float(view_width) / (max_x - min_x)
    ratio_y = float(view_height) / (max_y - min_y)

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


def draw_problem(canvas, problem: Problem):
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


def draw_solution(canvas, solution: Solution):
    canvas.delete(tkinter.ALL)
    
    points = list(solution.dst_points)
    points.append(Point(0, 0))
    points.append(Point(1, 1))

    toTk = get_canvas_coord_mapping(canvas, points)

    for poly in solution.facets:
        transformed = [solution.dst_points[idx] for idx in poly]
        canvas.create_polygon(*toTk(transformed), fill='#FFD0D0', outline='')
        canvas.create_polygon(*toTk(transformed), fill='', outline='#000000', tag='skeleton')
    canvas.tag_raise('skeleton')

    # Unit square, for scale
    canvas.create_polygon(*toTk([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)]),
            fill='', outline='#4040FF', width=3, dash=(15, 15))


def edges_of_a_facet(facet: List[Point]):
    for idx in range(len(facet)):
        yield facet[idx - 1], facet[idx]


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

        button_frame = Frame(root)
        button_frame.pack(fill=tkinter.Y, side=tkinter.LEFT)

        # Reposition the figure so it's center of mass is at 0.5, 0.5
        v = IntVar()
        self.center_cb = Checkbutton(button_frame, text="center", variable=v, command=lambda: self.populate_problem_canvas())
        self.center_cb.var = v
        self.center_cb.pack(side=tkinter.TOP)

        # Use meshes.reconstruct_facets instead of polygon/hole logic.
        v = IntVar()
        self.reconstruct_cb = Checkbutton(button_frame, text="reconstruct", variable=v, command=lambda: self.populate_problem_canvas())
        self.reconstruct_cb.var = v
        self.reconstruct_cb.pack(side=tkinter.TOP)

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
            p = self.current_problem
            if self.center_cb.var.get():
                p = center_problem(p)
            if self.reconstruct_cb.var.get():
                facets = meshes.reconstruct_facets(p)
                # paranoid about that extra facet.
                assert len([f for f in facets if polygon_area(f) < 0]) == 1
                facets = [f for f in facets if polygon_area(f) > 0]
                skeleton = [e for f in facets for e in edges_of_a_facet(f)]
                p = Problem(facets, skeleton)
            draw_problem(self.problem_canvas, p)


    def run(self):
        self.root.mainloop()

    def close(self):
        if self.root:
            self.root.destroy()
            self.root = None


class SolutionViewer(object):
    '''Feed it progressively enhanced solutions in a loop:
    
    solution = initial
    while sv.show_and_wait(solution):
        new_solution = elaborate(solution)
        if new_solution is None:
            return solution
    '''
    
    def __init__(self):
        self.action = None
        self.root = root = Tk()
        root.title('Fold me baby one more time')
        root.protocol("WM_DELETE_WINDOW", self.close)
        
        # exists the mainloop()
        root.bind("<space>", lambda evt: root.quit())

        root.pack_propagate(True)

        self.canvas = Canvas(root, bd=1, relief=tkinter.SUNKEN, width=500, height=500)
        self.canvas.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        self.canvas.bind("<Configure>", lambda evt: self.populate_canvas())
        self.current_solution = None


    def populate_canvas(self):
        if self.current_solution is None:
            return
        draw_solution(self.canvas, self.current_solution)


    def show_and_wait(self, solution):
        '''Return False if user closed the window'''
        self.current_solution = solution
        self.populate_canvas() 
        self.root.mainloop()
        return self.root is not None


    def close(self):
        if self.root:
            self.root.destroy()
            self.root = None


def main():
    ProblemBrowser().run()

if __name__ == '__main__':
    main()
