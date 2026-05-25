from __future__ import annotations
from tkinter import Tk, BOTH, Canvas, Button, Entry, Label, Scale, HORIZONTAL, Frame

class Window:

    def __init__(self, width: int, height: int, on_new_maze=None) -> None:
        self.__root = Tk()
        self.__root.title("Maze Solver")

        # =========================
        # Canvas
        # =========================
        self.__canvas = Canvas(
            self.__root,
            bg="white",
            width=width,
            height=height
        )
        self.__canvas.pack(fill=BOTH, expand=1)

        # =========================
        # Frames
        # =========================
        top_frame = Frame(self.__root)
        top_frame.pack(fill="x", pady=5)

        center_frame = Frame(self.__root)
        center_frame.pack(fill="x", pady=5)

        bottom_frame = Frame(self.__root)
        bottom_frame.pack(fill="x", pady=5)

        
        maze_controls_frame = Frame(bottom_frame)
        maze_controls_frame.pack(side="right", padx=10)

        cols_frame = Frame(maze_controls_frame)
        cols_frame.pack(fill="x")
        rows_frame = Frame(maze_controls_frame)
        rows_frame.pack(fill="x")

        # =========================
        # Seed controls
        # =========================
        self.__seed_label = Label(top_frame, text="Seed:")
        self.__seed_label.pack(side="left", padx=(10, 5))

        self.__seed_entry = Entry(top_frame, width=12)
        self.__seed_entry.pack(side="left")

        # =========================
        # Maze controls
        # =========================
        Label(cols_frame, text="Num cols:").pack(side="left", padx=(0,6))
        self.num_cols_entry = Entry(cols_frame, width=12)
        self.num_cols_entry.pack(side="left")

        Label(rows_frame, text="Num rows:").pack(side="left")
        self.num_rows_entry = Entry(rows_frame, width=12)
        self.num_rows_entry.pack(side="left")

        # =========================
        # Buttons
        # =========================
        if on_new_maze:
            self.__new_maze_btn = Button(
                center_frame,
                text="New Maze",
                command=on_new_maze
            )
            self.__new_maze_btn.pack(padx=0)

        self.__algo = "DFS"

        self.__algo_btn = Button(
            bottom_frame,
            text="Algorithm: DFS",
            command=self.__toggle_algo
        )
        self.__algo_btn.pack(side="left", padx=5)

        # =========================
        # Speed slider
        # =========================
        self.__speed = 0.005

        self.__speed_slider = Scale(
            bottom_frame,
            from_=0.000,
            to=0.1,
            resolution=0.001,
            orient=HORIZONTAL,
            label="Speed",
            command=self.__update_speed
        )

        self.__speed_slider.set(self.__speed)
        self.__speed_slider.pack(side="left", padx=(50, 0))

        # =========================
        # Window state
        # =========================
        self.__running = False

        self.__root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )
    
    def get_seed(self):
        value = self.__seed_entry.get()
        self.__seed_entry.delete(0, "end")
        if value == "":
            return None
        try:
            return int(value)
        except ValueError:
            return None
        
    def __update_speed(self, value):
        self.__speed = float(value)

    def get_speed(self):
        return self.__speed
    
    def get_maze_dimensions(self):
        cols = self.num_cols_entry.get()
        rows = self.num_rows_entry.get()
        
        try:
            cols = int(cols) if cols != "" else 12
            rows = int(rows) if rows != "" else 12
        except ValueError:
            cols, rows = 12, 12
        
        return cols, rows

    def redraw(self):
        self.__root.update_idletasks()
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
        print("Clearing canvas")
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
