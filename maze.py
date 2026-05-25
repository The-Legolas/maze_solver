from graphics import Window 
from cell import Cell
import time
import random

class Maze:
    def __init__(self, x1:int, y1:int, num_rows:int, num_cols:int, 
                 cell_size_x, cell_size_y, win:Window | None = None, 
                 seed = None) -> None:
        self.__cells = []
        self.__x1 = x1
        self.__y1 = y1
        self.__num_rows = num_rows
        self.__num_cols = num_cols
        self.__cell_size_x = cell_size_x
        self.__cell_size_y = cell_size_y
        self.__win = win
        if seed:
            random.seed(seed)

        self.__create_cells()
        time.sleep(5)
        self.__break_entrance_and_exit()
        self.__break_walls_r(0, 0)
        self.__reset_cells_visited()


    def __create_cells(self):
        for i in range(self.__num_cols):
            col_cells = []
            for j in range(self.__num_rows):
                col_cells.append(Cell(self.__win))
            self.__cells.append(col_cells)

        for i in range(self.__num_cols):
            for j in range(self.__num_rows):
                self.__draw_cell(i, j)
        

    def __draw_cell(self, i, j):
        if self.__win is None:
            return
        x1 = self.__x1 + i * self.__cell_size_x
        y1 = self.__y1 + j * self.__cell_size_y
        x2 = x1 + self.__cell_size_x
        y2 = y1 + self.__cell_size_y
        self.__cells[i][j].draw(x1, y1, x2, y2)
        self.__animate()

    def __animate(self, sleep: float = 0.002):
        if self.__win is None:
            return
        self.__win.redraw()
        time.sleep(sleep)
    
    def __break_entrance_and_exit(self):
        self.__cells[0][0].has_top_wall = False
        self.__draw_cell(0, 0)

        self.__cells[self.__num_cols - 1][self.__num_rows - 1].has_bottom_wall = False
        self.__draw_cell(self.__num_cols - 1, self.__num_rows - 1)
    
    def __break_walls_r(self, i, j):
        self.__cells[i][j].visited = True
        while True:
            next_index_list = []
            if i > 0 and not self.__cells[i - 1][j].visited:
                next_index_list.append((i -1, j))

            if i < self.__num_cols - 1 and not self.__cells[i + 1][j].visited:
                next_index_list.append((i +1, j))

            if j > 0 and not self.__cells[i][j - 1].visited:
                next_index_list.append((i, j -1))

            if j < self.__num_rows - 1 and not self.__cells[i][j + 1].visited:
                next_index_list.append((i, j +1))

            
            if len(next_index_list) == 0:
                self.__draw_cell(i, j)
                return

            direction_index = random.randrange(len(next_index_list))
            next_index = next_index_list[direction_index]

            # did we move left?
            if next_index[0] == i - 1:
                self.__cells[i][j].has_left_wall = False
                self.__cells[i - 1][j].has_right_wall = False

            # did we move right?
            if next_index[0] == i + 1:
                self.__cells[i][j].has_right_wall = False
                self.__cells[i + 1][j].has_left_wall = False

            # did we move up?
            if next_index[1] == j - 1:
                self.__cells[i][j].has_top_wall = False
                self.__cells[i][j - 1].has_bottom_wall = False

            # did we move down?
            if next_index[1] == j + 1:
                self.__cells[i][j].has_bottom_wall = False
                self.__cells[i][j + 1].has_top_wall = False
            
            self.__break_walls_r(next_index[0], next_index[1])

    def __reset_cells_visited(self):
        for col in self.__cells:
            for cell in col:
                cell.visited = False

    def solve(self) -> bool:
        return self._solve_r(0, 0)

    def _solve_r(self, i, j) -> bool:
        self.__animate(sleep=0.7)
        self.__cells[i][j].visited = True
        if self.__cells[i][j] == self.__cells[-1][-1]:
            return True
        
        if (
            i > 0 
            and self.__cells[i][j].has_left_wall == False
            and not self.__cells[i - 1][j].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i - 1][j])
            if self._solve_r(i -1, j) == True:
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i - 1][j], undo= True)

        if (
            i < self.__num_cols - 1
            and not self.__cells[i][j].has_right_wall
            and not self.__cells[i + 1][j].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i + 1][j])
            if self._solve_r(i + 1, j):
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i + 1][j], undo= True)

        # move up if there is no wall and it hasn't been visited
        if (
            j > 0
            and not self.__cells[i][j].has_top_wall
            and not self.__cells[i][j - 1].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i][j - 1])
            if self._solve_r(i, j - 1):
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i][j - 1], undo= True)

        # move down if there is no wall and it hasn't been visited
        if (
            j < self.__num_rows - 1
            and not self.__cells[i][j].has_bottom_wall
            and not self.__cells[i][j + 1].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i][j + 1])
            if self._solve_r(i, j + 1):
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i][j + 1], undo= True)

        return False


