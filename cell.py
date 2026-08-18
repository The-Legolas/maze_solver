from __future__ import annotations
from graphics import Window, Point, Line


class Cell:
    """Represents a single grid square in the maze.

    Tracks wall states, visit history, and screen coordinates for rendering.
    """

    def __init__(self, win: Window | None) -> None:
        # Wall state flags (True = wall exists, False = wall is broken/open)
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True

        # Pathfinding flag used during maze generation and solving
        self.visited = False

        # Screen coordinates (top-left corner x1/y1, bottom-right corner x2/y2)
        self._x1 = -1
        self._x2 = -1
        self._y1 = -1 
        self._y2 = -1

        # Reference to the graphical canvas window
        self.__win = win

    def draw(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Saves pixel boundaries and draws all 4 walls to the canvas."""
        if self.__win is None:
            return
        
        self._x1, self._y1 = x1, y1
        self._x2, self._y2 = x2, y2

        # Define the four outer wall line segments
        walls = [
            (self.has_left_wall, Point(x1, y1), Point(x1, y2)),
            (self.has_top_wall, Point(x1, y1), Point(x2, y1)),
            (self.has_right_wall, Point(x2, y1), Point(x2, y2)),
            (self.has_bottom_wall, Point(x1, y2), Point(x2, y2)),
        ]

        # Render walls: "black" draws visible walls, "white" erases broken walls by matching the background
        for has_wall, start_point, end_point in walls:
            color = "black" if has_wall else "white"
            self.__win.draw_line(Line(start_point, end_point), color)

        """ old
        if self.has_left_wall:
            line = Line(Point(x1, y1), Point(x1, y2))
            self.__win.draw_line(line)
        else:
            line = Line(Point(x1, y1), Point(x1, y2))
            self.__win.draw_line(line, "white")
        if self.has_top_wall:
            line = Line(Point(x1, y1), Point(x2, y1))
            self.__win.draw_line(line)
        else:
            line = Line(Point(x1, y1), Point(x2, y1))
            self.__win.draw_line(line, "white")
        if self.has_right_wall:
            line = Line(Point(x2, y1), Point(x2, y2))
            self.__win.draw_line(line)
        else:
            line = Line(Point(x2, y1), Point(x2, y2))
            self.__win.draw_line(line, "white")
        if self.has_bottom_wall:
            line = Line(Point(x1, y2), Point(x2, y2))
            self.__win.draw_line(line)
        else:
            line = Line(Point(x1, y2), Point(x2, y2))
            self.__win.draw_line(line, "white")
        """

    def get_center(self) -> Point:
        """Calculates and returns the (x, y) center pixel coordinate of this cell."""
        center_x = (self._x1 + self._x2) // 2
        center_y = (self._y1 + self._y2) // 2
        return Point(center_x, center_y)
    
    def draw_move(self, to_cell: Cell, undo: bool =False) -> None:
        """Draws a path line connecting the center of this cell to another cell.

        Uses red for active exploration and gray when backtracking.
        """
        if self.__win is None:
            return

        """old
        x_half = abs(self._x2 - self._x1) // 2
                y_half = abs(self._y2 - self._y1) // 2
                x_center = self._x1 + x_half
                y_center = self._y1 + y_half
        
                x_half2 = abs(to_cell._x2 - to_cell._x1) // 2
                y_half2 = abs(to_cell._y2 - to_cell._y1) // 2
                x_center2 = to_cell._x1 + x_half2
                y_center2 = to_cell._y1 + y_half2
        
        """
        
        fill_color = "gray" if undo else "red"
        path_line = Line(self.get_center(), to_cell.get_center())
        self.__win.draw_line(path_line, fill_color)
        

        
