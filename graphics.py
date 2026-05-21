from __future__ import annotations
from tkinter import Tk, BOTH, Canvas

class Window:
    def __init__(self, width: int, height: int) -> None:
        self.__root  = Tk()
        self.__root.title("Maze Solver")
        self.__canvas = Canvas(master=self.__root, bg="white", height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=1) 
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        # This processes all "idle" tasks (like resizing or redrawing widgets)
        self.__root.update_idletasks()
        # This processes all events (like mouse clicks or keyboard hits)
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()
        print("window closed...")
    
    def draw_line(self, line: Line, fill_color: str ="black"):
        line.draw(self.__canvas, fill_color)

    def close(self):
        self.__running = False


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Line:
    def __init__(self, p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2
    
    def draw(self, canvas: Canvas, fill_color: str="black"):
        canvas.create_line(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=fill_color, width=2
        )
