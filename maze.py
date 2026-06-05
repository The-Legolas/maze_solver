from graphics import Window 
from cell import Cell
from collections import deque
import heapq
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

        self.__margin_x = x1
        self.__margin_y = y1
        self.__solution_path: set[tuple[tuple[int, int], tuple[int, int]]] = set()

        if self.__win is not None:
            self.__win.set_resize_callback(self.__on_window_resize)
            
        if seed is None:
            seed = random.randint(0, 1_000_000_000_00)

        random.seed(seed)
        print(f"Maze seed: {seed}")

        self.__create_cells()
        self.__break_entrance_and_exit()
        self.__break_walls_r(0, 0)
        self.__reset_cells_visited()
        time.sleep(1)


    def __create_cells(self):
        self.__solution_path = set()
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
        self.__animate(sleep=0.003)

    def __on_window_resize(self, new_width, new_height):
        if self.__win is None:
            return
        canvas_width, canvas_height = self.__win.get_canvas_size()
        print(f"resize canvas size: {canvas_width}, {canvas_height}")
        self.__cell_size_x = (canvas_width - 2 * self.__margin_x) / self.__num_cols
        self.__cell_size_y = (canvas_height - 2 * self.__margin_y) / self.__num_rows
        self.__win.clear_canvas()
        self.__redraw_all_cells()
        if self.__solution_path:
            self.__redraw_solution()

    def __redraw_all_cells(self):
        for i in range(self.__num_cols):
            for j in range(self.__num_rows):
                x1 = self.__x1 + i * self.__cell_size_x
                y1 = self.__y1 + j * self.__cell_size_y
                x2 = x1 + self.__cell_size_x
                y2 = y1 + self.__cell_size_y
                self.__cells[i][j].draw(x1, y1, x2, y2)
        
        #for (i, j), (ni, nj) in self.__solution_path:
        #    self.__cells[i][j].draw_move(self.__cells[ni][nj])

        if self.__win:
            self.__win.redraw()
        
    def __redraw_solution(self):
        for (i, j), (ni, nj) in self.__solution_path:
            self.__cells[i][j].draw_move(self.__cells[ni][nj])
        if self.__win:
            self.__win.redraw()

    def redraw_cells(self):
        self.__redraw_all_cells()

    def reset_solution(self):
        self.__solution_path = set()

    def __animate(self, sleep: float| None = None):
        if self.__win is None:
            return
        self.__win.redraw()
        if sleep is None:
            sleep = self.__win.get_speed()
        
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

    def reset_visited(self):
        self.__reset_cells_visited()


    def solve_dfs(self) -> bool:
       return self._solve_r(0, 0)

    def _solve_r(self, i, j) -> bool:
        self.__animate()
        self.__cells[i][j].visited = True
        if self.__cells[i][j] == self.__cells[-1][-1]:
            return True
        
        if (
            i > 0 
            and self.__cells[i][j].has_left_wall == False
            and not self.__cells[i - 1][j].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i - 1][j])
            self.__solution_path.add(((i, j), (i - 1, j)))
            if self._solve_r(i -1, j) == True:
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i - 1][j], undo= True)
                self.__solution_path.discard(((i, j), (i - 1, j)))

        if (
            i < self.__num_cols - 1
            and not self.__cells[i][j].has_right_wall
            and not self.__cells[i + 1][j].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i + 1][j])
            self.__solution_path.add(((i, j), (i + 1, j)))
            if self._solve_r(i + 1, j):
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i + 1][j], undo= True)
                self.__solution_path.discard(((i, j), (i + 1, j)))

        # move up if there is no wall and it hasn't been visited
        if (
            j > 0
            and not self.__cells[i][j].has_top_wall
            and not self.__cells[i][j - 1].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i][j - 1])
            self.__solution_path.add(((i, j), (i, j - 1)))
            if self._solve_r(i, j - 1):
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i][j - 1], undo= True)
                self.__solution_path.discard(((i, j), (i, j - 1)))

        # move down if there is no wall and it hasn't been visited
        if (
            j < self.__num_rows - 1
            and not self.__cells[i][j].has_bottom_wall
            and not self.__cells[i][j + 1].visited
        ):
            self.__cells[i][j].draw_move(self.__cells[i][j + 1])
            self.__solution_path.add(((i, j), (i, j + 1)))
            if self._solve_r(i, j + 1):
                return True
            else:
                self.__cells[i][j].draw_move(self.__cells[i][j + 1], undo= True)
                self.__solution_path.discard(((i, j), (i, j + 1)))

        return False

    def solve_bfs(self)-> bool:
        queue = deque()
        queue.append((0, 0))
        self.__cells[0][0].visited = True

        # track where we came from so we can draw the path
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {(0, 0): None}

        solved = False
        while queue:
            i, j = queue.popleft()  # <-- popleft makes it a queue (FIFO)
            self.__animate()

            if i == self.__num_cols - 1 and j == self.__num_rows - 1:
                solved = True
                break

            # check all 4 neighbors (same wall/visited checks as your DFS)
            neighbors = [
                (i - 1, j),  # left
                (i + 1, j),  # right
                (i, j - 1),  # up
                (i, j + 1),  # down
            ]
            for ni, nj in neighbors:
                if (ni == i - 1 
                    and i > 0 
                    and not self.__cells[i][j].has_left_wall 
                    and not self.__cells[ni][nj].visited
                ):
                    self.__cells[i][j].draw_move(self.__cells[ni][nj])
                    self.__solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self.__cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)
                
                if (ni == i + 1 
                    and i < self.__num_cols - 1
                    and not self.__cells[i][j].has_right_wall 
                    and not self.__cells[ni][nj].visited
                ):
                    self.__cells[i][j].draw_move(self.__cells[ni][nj])
                    self.__solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self.__cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)
               
                
                if (nj == j - 1 
                    and j > 0
                    and not self.__cells[i][j].has_top_wall 
                    and not self.__cells[ni][nj].visited
                ):
                    self.__cells[i][j].draw_move(self.__cells[ni][nj])
                    self.__solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self.__cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)

                if (nj == j + 1 
                    and j < self.__num_rows - 1
                    and not self.__cells[i][j].has_bottom_wall 
                    and not self.__cells[ni][nj].visited
                ):
                    self.__cells[i][j].draw_move(self.__cells[ni][nj])
                    self.__solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self.__cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)

        if solved:
            self.__solution_path = set()
            solution_path = set()  # for dead end detection
            current = (self.__num_cols - 1, self.__num_rows - 1)
            while current is not None:
                solution_path.add(current)  # track winning cells
                prev = came_from[current]
                if prev is not None:
                    self.__cells[current[0]][current[1]].draw_move(
                        self.__cells[prev[0]][prev[1]]
                    )
                    self.__solution_path.add(
                        ((current[0], current[1]), (prev[0], prev[1]))
                    )
                current = prev

            # gray out dead ends
            for i in range(self.__num_cols):
                for j in range(self.__num_rows):
                    if self.__cells[i][j].visited and (i, j) not in solution_path:
                        prev = came_from.get((i, j))
                        if prev is not None:
                            self.__cells[i][j].draw_move(
                                self.__cells[prev[0]][prev[1]], undo=True
                            )
        
        return solved
    

    def _heuristic(self, i, j):
        goal_i = self.__num_cols - 1
        goal_j = self.__num_rows - 1
        return abs(goal_i - i) + abs(goal_j - j)    
    

    def solve_astar(self) -> bool:
        # (f_score, g_score, i, j)
        start = (self._heuristic(0, 0), 0, 0, 0)
        open_set: list[tuple[int, int, int, int]] = [start]
        self.__cells[0][0].visited = True
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {(0, 0): None}
        g_score: dict[tuple[int, int], int] = {(0, 0): 0}

        solved = False
        while open_set:
            f, g, i, j = heapq.heappop(open_set)
            self.__animate()

            if i == self.__num_cols - 1 and j == self.__num_rows - 1:
                solved = True
                break
            
            if g > g_score.get((i, j), float("inf")):
                continue

            neighbors = [
                (i - 1, j),  # left
                (i + 1, j),  # right
                (i, j - 1),  # up
                (i, j + 1),  # down
            ]
            for ni, nj in neighbors:
                if (ni == i - 1 
                    and i > 0 
                    and not self.__cells[i][j].has_left_wall 
                ):
                    new_g = g + 1
                    if new_g < g_score.get((ni, nj), float("inf")):
                        g_score[(ni, nj)] = new_g
                        new_f = new_g + self._heuristic(ni, nj)
                        heapq.heappush(open_set, (new_f, new_g, ni, nj))
                        came_from[(ni, nj)] = (i, j)
                        self.__cells[i][j].draw_move(self.__cells[ni][nj])
                        self.__solution_path.add(((i, j), (ni, nj)))
                
                if (ni == i + 1 
                    and i < self.__num_cols - 1
                    and not self.__cells[i][j].has_right_wall 
                ):
                    new_g = g + 1
                    if new_g < g_score.get((ni, nj), float("inf")):
                        g_score[(ni, nj)] = new_g
                        new_f = new_g + self._heuristic(ni, nj)
                        heapq.heappush(open_set, (new_f, new_g, ni, nj))
                        came_from[(ni, nj)] = (i, j)
                        self.__cells[i][j].draw_move(self.__cells[ni][nj])
                        self.__solution_path.add(((i, j), (ni, nj)))
               
                
                if (nj == j - 1 
                    and j > 0
                    and not self.__cells[i][j].has_top_wall 
                ):
                    new_g = g + 1
                    if new_g < g_score.get((ni, nj), float("inf")):
                        g_score[(ni, nj)] = new_g
                        new_f = new_g + self._heuristic(ni, nj)
                        heapq.heappush(open_set, (new_f, new_g, ni, nj))
                        came_from[(ni, nj)] = (i, j)
                        self.__cells[i][j].draw_move(self.__cells[ni][nj])
                        self.__solution_path.add(((i, j), (ni, nj)))

                if (nj == j + 1 
                    and j < self.__num_rows - 1
                    and not self.__cells[i][j].has_bottom_wall 
                ):
                    new_g = g + 1
                    if new_g < g_score.get((ni, nj), float("inf")):
                        g_score[(ni, nj)] = new_g
                        new_f = new_g + self._heuristic(ni, nj)
                        heapq.heappush(open_set, (new_f, new_g, ni, nj))
                        came_from[(ni, nj)] = (i, j)
                        self.__cells[i][j].draw_move(self.__cells[ni][nj])
                        self.__solution_path.add(((i, j), (ni, nj)))

        if solved:
            self.__solution_path = set()
            solution_path = set()  # for dead end detection
            current = (self.__num_cols - 1, self.__num_rows - 1)
            while current is not None:
                solution_path.add(current)  # track winning cells
                prev = came_from[current]
                if prev is not None:
                    self.__cells[current[0]][current[1]].draw_move(
                        self.__cells[prev[0]][prev[1]]
                    )
                    self.__solution_path.add(
                        ((current[0], current[1]), (prev[0], prev[1]))
                    )
                current = prev

            # gray out dead ends
            for i in range(self.__num_cols):
                for j in range(self.__num_rows):
                    if (i, j) in g_score and (i, j) not in solution_path:
                        prev = came_from.get((i, j))
                        if prev is not None:
                            self.__cells[i][j].draw_move(
                                self.__cells[prev[0]][prev[1]], undo=True
                            )
        
        return solved
