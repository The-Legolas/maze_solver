from __future__ import annotations
from graphics import Window, Point, Line


class Cell:
    def __init__(self, win: Window | None) -> None:
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.visited = False
        self.__x1 = -1
        self.__x2 = -1
        self.__y1 = -1 
        self.__y2 = -1
        self.__win = win

    def draw(self, x1, y1, x2, y2):
        if self.__win is None:
            return
        self.__x1 = x1
        self.__x2 = x2
        self.__y1 = y1 
        self.__y2 = y2

        
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

    def draw_move(self, to_cell: Cell, undo=False):
        if self.__win is None:
            return
        
        x_half = abs(self.__x2 - self.__x1) // 2
        y_half = abs(self.__y2 - self.__y1) // 2
        x_center = self.__x1 + x_half
        y_center = self.__y1 + y_half

        x_half2 = abs(to_cell.__x2 - to_cell.__x1) // 2
        y_half2 = abs(to_cell.__y2 - to_cell.__y1) // 2
        x_center2 = to_cell.__x1 + x_half2
        y_center2 = to_cell.__y1 + y_half2

        fill_color = "red" if not undo else "gray"

        line = Line(Point(x_center, y_center), Point(x_center2, y_center2))
        self.__win.draw_line(line, fill_color)
        

        
