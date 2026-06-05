from __future__ import annotations
from typing import Callable, Optional
from tkinter import Tk, BOTH, Canvas, Button, Entry, Label, Scale, HORIZONTAL, Frame, Radiobutton, StringVar

class Window:

    def __init__(self, width: int, height: int, on_new_maze=None) -> None:
        self.__root = Tk()
        self.__root.title("Maze Solver")
        #self.__root.geometry(f"{width}x{height}")
        self.__resizing = False

        # =========================
        # Canvas
        # =========================
        self.__canvas = Canvas(
            self.__root,
            bg="white",
            width=width,
            height=height
        )

        self.__canvas.pack(fill="both", expand=True)

        
        # =========================
        # Frames
        # =========================

        self.__bottom_frame = Frame(self.__root)
        self.__bottom_frame.pack(fill="x", pady=5, side="bottom")

        self.__center_frame = Frame(self.__root)
        self.__center_frame.pack(fill="x", pady=5, side="bottom")

        self.__top_frame = Frame(self.__root)
        self.__top_frame.pack(fill="x", pady=5, side="bottom")

        
        maze_controls_frame = Frame(self.__bottom_frame)
        maze_controls_frame.pack(side="right", padx=10)

        cols_frame = Frame(maze_controls_frame)
        cols_frame.pack(fill="x")
        rows_frame = Frame(maze_controls_frame)
        rows_frame.pack(fill="x")

        # =========================
        # Seed controls
        # =========================
        self.__seed_label = Label(self.__top_frame, text="Seed:")
        self.__seed_label.pack(side="left", padx=(10, 5))

        self.__seed_entry = Entry(self.__top_frame, width=12)
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
                self.__center_frame,
                text="New Maze",
                command=on_new_maze
            )
            self.__new_maze_btn.pack(padx=0)

        

        self.__algo = StringVar(value="DFS")

        for algo in ["DFS", "BFS", "A*"]:
            Radiobutton(
                self.__bottom_frame,
                text=algo,
                variable=self.__algo,
                value=algo,
                font=("Arial", 10),
                padx=10,
                pady=5
            ).pack(side="left", padx=5)

        # =========================
        # Speed slider
        # =========================
        self.__speed = 0.005

        self.__speed_slider = Scale(
            self.__bottom_frame,
            from_=0.000,
            to=0.2,
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

        self.__width = width
        self.__height = height
        self.__on_resize_callback: Optional[Callable[[int, int], None]] = None
        self.__root.bind("<Configure>", self.__on_resize)
        

        self.__root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )
    
    def get_seed(self):
        value = self.__seed_entry.get()
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

    def get_algo(self):
        return self.__algo.get()

    def clear_canvas(self):
        print("Clearing canvas")
        self.__canvas.delete("all")

    def set_resize_callback(self, fn):
        self.__on_resize_callback = fn

    def get_size(self):
        return self.__width, self.__height

    def get_canvas_size(self):
        self.__root.update()
        actual_canvas_width = self.__canvas.winfo_width()
        actual_canvas_height = self.__canvas.winfo_height()
        return actual_canvas_width, actual_canvas_height

    def __on_resize(self, event):
        if event.widget is not self.__root:
            return
        if self.__resizing:
            return

        new_width = event.width
        new_height = event.height

        if new_width == self.__width and new_height == self.__height:
            return

        self.__resizing = True
        self.__width = new_width
        self.__height = new_height


        if self.__on_resize_callback is not None:
            callback = self.__on_resize_callback
            if hasattr(self, "_resize_job") and self._resize_job:
                self.__root.after_cancel(self._resize_job)
            self._resize_job = self.__root.after(
                300, lambda: callback(new_width, new_height)
            )

        self.__resizing = False

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
