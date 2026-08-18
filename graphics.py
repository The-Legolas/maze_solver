from __future__ import annotations
from typing import Callable, Tuple
from tkinter import (
    Tk, 
    Canvas, 
    Button, 
    Entry, 
    Label, 
    Scale, 
    HORIZONTAL, 
    Frame,
    Radiobutton, 
    StringVar,
)

class Point:
    """Represents a 2D pixel coordinate (x, y) on the screen."""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Line:
    """Represents a straight line segment between two points."""

    def __init__(self, start_point: Point, end_point: Point) -> None:
        self.p1 = start_point
        self.p2 = end_point
    
    def draw(self, canvas: Canvas, fill_color: str="black"):
        """Draws this line segment onto a Tkinter Canvas widget."""
        canvas.create_line(
            self.p1.x,
            self.p1.y, 
            self.p2.x, 
            self.p2.y, 
            fill=fill_color, 
            width=2,
        )


class Window:
    """Manages the main GUI window, Tkinter canvas, and control widgets."""

    def __init__(self, width: int, height: int, on_new_maze: Callable[[], None] | None) -> None:
        # Core Tkinter setup
        self._root = Tk()
        self._root.title("Maze Solver")


        # Window state & pixel dimensions
        self._width = width
        self._height = height
        self._is_running = False
        self._is_resizing = False

        # Event handling callback references
        self._on_resize_callback: Callable[[int, int], None] | None = None
        self._resize_job = None


        # =========================
        # UI Construction Sequence (Modular Layout)
        # =========================
        self._create_canvas(width, height)
        self._create_frames()
        self._create_seed_controls()
        self._create_dimension_controls()
        self._create_algorithm_selector()
        self._create_speed_slider()
        self._create_action_buttons(on_new_maze)

        # Window event bindings
        self._root.bind("<Configure>", self.__on_resize)
        self._root.protocol("WM_DELETE_WINDOW", self.close)


    # =========================
    # UI Builder Helpers
    # =========================

    def _create_canvas(self, width: int, height: int) -> None:
        """Creates the drawing area where the maze lines and path solution are rendered."""
        self._canvas = Canvas(
            self._root,
            bg="white",
            width=width,
            height=height
        )
        self._canvas.pack(fill="both", expand=True)

    def _create_frames(self) -> None:
        """Sets up stacked horizontal container frames at the bottom for controls."""
        self._bottom_frame = Frame(self._root)
        self._bottom_frame.pack(fill="x", pady=5, side="bottom")

        self._center_frame = Frame(self._root)
        self._center_frame.pack(fill="x", pady=5, side="bottom")

        self._top_frame = Frame(self._root)
        self._top_frame.pack(fill="x", pady=5, side="bottom")
        
    def _create_seed_controls(self) -> None:
        """Creates the label and text entry field for setting a fixed random seed."""
        self._seed_label = Label(self._top_frame, text="Seed:")
        self._seed_label.pack(side="left", padx=(10, 5))

        self._seed_entry = Entry(self._top_frame, width=12)
        self._seed_entry.pack(side="left")

    def _create_dimension_controls(self) -> None:
        """Creates input fields allowing users to specify grid dimensions (Columns & Rows)."""
        maze_controls_frame = Frame(self._bottom_frame)
        maze_controls_frame.pack(side="right", padx=10)

        cols_frame = Frame(maze_controls_frame)
        cols_frame.pack(fill="x")

        rows_frame = Frame(maze_controls_frame)
        rows_frame.pack(fill="x")        

        Label(cols_frame, text="Num cols:").pack(side="left", padx=(0,6))
        self._num_cols_entry = Entry(cols_frame, width=12)
        self._num_cols_entry.pack(side="left")

        Label(rows_frame, text="Num rows:").pack(side="left")
        self._num_rows_entry = Entry(rows_frame, width=12)
        self._num_rows_entry.pack(side="left")

    def _create_algorithm_selector(self) -> None:
        """Creates radio buttons for choosing the active search algorithm."""
        self._selected_algo = StringVar(value="DFS")
        
        for algo_name in ["DFS", "BFS", "A*"]:
            Radiobutton(
                self._bottom_frame,
                text=algo_name,
                variable=self._selected_algo,
                value=algo_name,
                font=("Arial", 10),
                padx=10,
                pady=5
            ).pack(side="left", padx=5)

    def _create_speed_slider(self) -> None:
        """Creates a slider control to adjust step-by-step animation delay (in seconds)."""
        self._speed_seconds = 0.005
        
        self._speed_slider = Scale(
            self._bottom_frame,
            from_=0.000,
            to=0.2,
            resolution=0.001,
            orient=HORIZONTAL,
            label="Speed",
            command=self.__update_speed
        )

        self._speed_slider.set(self._speed_seconds)
        self._speed_slider.pack(side="left", padx=(50, 0))

    def _create_action_buttons(self, on_new_maze: Callable[[], None] | None) -> None:
        """Creates the 'New Maze' trigger button if a callback function was passed in."""
        if on_new_maze:
            self._new_maze_btn = Button(
                self._center_frame,
                text="New Maze",
                command=on_new_maze
            )
            self._new_maze_btn.pack(padx=0)

    # =========================
    # Public Data Parsers
    # =========================

    def get_seed(self) -> int | str | None:
        """Reads the seed text field. 
        Returns an integer if it's a number, a string if it's a word, 
        or None if left empty.
        """
        value = self._seed_entry.get().strip()
        
        if not value:
            return None    
        try:
            return int(value)
        except ValueError:
            return value
        
    def __update_speed(self, value: str) -> None:
        """Callback triggered automatically whenever the speed slider moves."""
        self._speed_seconds = float(value)

    def get_speed(self) -> float:
        """Returns the current animation sleep delay in seconds."""
        return self._speed_seconds
    
    def get_maze_dimensions(self, default_cols: int = 12, default_rows: int = 12) -> Tuple[int, int]:
        """Reads row and column counts from user inputs.
        Falls back to default values if empty or invalid.
        """
        raw_cols = self._num_cols_entry.get().strip()
        raw_rows = self._num_rows_entry.get().strip()
        
        try:
            cols = int(raw_cols) if raw_cols else default_cols
            rows = int(raw_rows) if raw_rows else default_rows
        except ValueError:
            cols, rows = default_cols, default_rows
        
        return cols, rows

    def get_algo(self) -> str:
        """Returns the currently selected pathfinding algorithm ("DFS", "BFS", or "A*")."""
        return self._selected_algo.get()

    # =========================
    # Drawing & Render Loop Methods
    # =========================

    def redraw(self)-> None:
        """Forces Tkinter to process UI events and update the screen immediately.
        Without this, the screen would freeze while the maze generation runs.
        """
        self._root.update_idletasks()
        self._root.update()

    def wait_for_close(self)-> None:
        """A manual event loop that keeps the window open until closed.
        We use this instead of Tkinter's default .mainloop() so we can draw 
        the maze step-by-step.
        """
        self._is_running = True
        while self._is_running:
            self.redraw()
        print("window closed...")
    
    def draw_line(self, line: Line, fill_color: str ="black")-> None:
        """Delegates drawing to the Line object, passing in our canvas."""
        line.draw(self._canvas, fill_color)

    def clear_canvas(self)-> None:
        """Erases all drawn lines and paths from the visual canvas."""
        print("Clearing canvas")
        self._canvas.delete("all")

    # =========================
    # Window Resizing & Dimensions
    # =========================

    def set_resize_callback(self, callback: Callable[[int, int], None]) -> None:
        """Registers a function to run whenever the user resizes the window."""
        self._on_resize_callback = callback

    def get_size(self)-> Tuple[int, int]:
        """Returns the window's last known overall pixel dimensions."""
        return self._width, self._height

    def get_canvas_size(self)-> Tuple[int, int]:
        """Queries Tkinter for the exact current pixel dimensions of just the drawing canvas."""
        self._root.update()
        actual_canvas_width = self._canvas.winfo_width()
        actual_canvas_height = self._canvas.winfo_height()
        return actual_canvas_width, actual_canvas_height

    def __on_resize(self, event)-> None:
        """Handles window resizing events with 'debouncing' to avoid lag."""
        # Ignore resize events triggered by smaller widgets inside the window
        if event.widget is not self._root:
            return
        if self._is_resizing:
            return

        new_width = event.width
        new_height = event.height

        # If the size didn't actually change, do nothing
        if new_width == self._width and new_height == self._height:
            return

        self._is_resizing = True
        self._width = new_width
        self._height = new_height


        # Debounce logic: Wait 300ms after the user stops dragging the window corner 
        # before redrawing the maze. This prevents crashing from drawing 100 mazes a second.
        if self._on_resize_callback is not None:
            callback = self._on_resize_callback
            if self._resize_job is not None:
                self._root.after_cancel(self._resize_job)
                
            self._resize_job = self._root.after(
                300, lambda: callback(new_width, new_height)
            )

        self._is_resizing = False

    def close(self) -> None:
        """Stops the main render loop, allowing the program to exit cleanly."""
        self._is_running = False


