from __future__ import annotations
from tkinter import Tk, BOTH, Canvas, Button

class Window:
    def __init__(self, width: int, height: int, on_new_maze=None) -> None:
        self.__root  = Tk()
        self.__root.title("Maze Solver")
        
        self.__canvas = Canvas(self.__root, bg="white", height=height, width=width)
        self.__canvas.pack(fill=BOTH, expand=1)

        if on_new_maze:
            btn = Button(self.__root, text="New Maze", command=on_new_maze)
            btn.pack()

        self.__running = False

        self.__algo = "DFS"  # track current algorithm
        self.__algo_btn = Button(
            self.__root, 
            text="Algorithm: DFS", 
            command=self.__toggle_algo
        )
        self.__algo_btn.pack(side="left")

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
    
    def __toggle_algo(self):
        if self.__algo == "DFS":
            self.__algo = "BFS"
        else:
            self.__algo = "DFS"
        self.__algo_btn.config(text=f"Algorithm: {self.__algo}")

    def get_algo(self):
        return self.__algo

    def clear_canvas(self):
        print("clearing canvas")
        self.__canvas.delete("all")

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
