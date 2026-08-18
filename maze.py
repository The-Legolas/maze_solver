from collections import deque
import heapq
import time
import random

from cell import Cell
from graphics import Window


class Maze:
    def __init__(
        self,
        origin_x: int,
        origin_y: int,
        num_rows: int,
        num_cols: int,
        cell_size_x: float,
        cell_size_y: float,
        win: Window | None = None,
        seed: int | str | None = None,
    ) -> None:
        """Initializes the grid, generates a random maze layout, and draws it to the window."""
        self._win = win
        self._num_rows = num_rows
        self._num_cols = num_cols

        # Grid placement and cell dimensions in pixels
        self._origin_x = origin_x
        self._origin_y = origin_y
        self._cell_size_x = cell_size_x
        self._cell_size_y = cell_size_y

        # Margins reserved around the canvas for resizing calculations
        self._margin_x = origin_x
        self._margin_y = origin_y

        # 2D grid storing Cell objects: self._cells[col_index][row_index]
        self._cells: list[list[Cell]] = []
        
        # Stores path segments for redrawing the solution line when window resizes
        self._solution_path: set[tuple[tuple[int, int], tuple[int, int]]] = set()

        # Listen for window resize events if a GUI window was provided
        if self._win is not None:
            self._win.set_resize_callback(self._on_window_resize)

        # Seed the random number generator for reproducible maze generation         
        if seed is None:
            seed = random.randint(0, 1_000_000_000_00)

        random.seed(seed)
        print(f"Maze seed: {seed}")

        self._create_cells()
        self._break_entrance_and_exit()
        self._carve_passages_recursive(col=0, row=0)
        self.reset_visited()
        time.sleep(1)

    # =========================
    # Grid Construction & Cell Coordinate Math
    # =========================

    def _get_cell_bounds(self, col: int, row: int) -> tuple[int, int, int, int]:
        """Calculates the exact pixel bounding box (x1, y1, x2, y2) for a given grid cell."""
        x1 = self._origin_x + col * self._cell_size_x
        y1 = self._origin_y + row * self._cell_size_y
        x2 = x1 + self._cell_size_x
        y2 = y1 + self._cell_size_y
        return int(x1), int(y1), int(x2), int(y2),
    
    def _create_cells(self)-> None:
        """Populates the 2D array with Cell objects and draws the initial uncarved grid."""
        self._solution_path = set()

        # Build 2D list structured as: columns -> rows
        for col in range(self._num_cols):
            col_cells = []
            for row in range(self._num_rows):
                col_cells.append(Cell(self._win))
            self._cells.append(col_cells)

        # Draw each cell onto the canvas
        for col in range(self._num_cols):
            for row in range(self._num_rows):
                self._draw_cell(col, row)
        
    def _draw_cell(self, col: int, row: int) -> None:
        """Draws or updates a single cell on the canvas."""
        if self._win is None:
            return
        x1, y1, x2, y2 = self._get_cell_bounds(col, row)
        self._cells[col][row].draw(x1, y1, x2, y2)
        self._animate(sleep=0.003)

    # =========================
    # Maze Generation
    # =========================

    def _break_entrance_and_exit(self) -> None:
        """Opens the top wall of the top-left cell (start)
        and the bottom wall of the bottom-right cell (finish)."""
        # Start cell at top-left (col 0, row 0)
        self._cells[0][0].has_top_wall = False
        self._draw_cell(0, 0)
        
        # End cell at bottom-right (last col, last row)
        end_col = self._num_cols - 1
        end_row = self._num_rows - 1
        self._cells[end_col][end_row].has_bottom_wall = False
        self._draw_cell(end_col, end_row)
        
    def _carve_passages_recursive(self, col: int, row: int) -> None:
        """Generates the maze layout by carving passages using Depth-First Search (Recursive Backtracking)."""
        self._cells[col][row].visited = True

        while True:
            # Look at all 4 surrounding neighbors and collect unvisited ones
            unvisited_neighbors = []

            # Check Left neighbor
            if col > 0 and not self._cells[col - 1][row].visited:
                unvisited_neighbors.append((col - 1, row))

            # Check Right neighbor
            if col < self._num_cols - 1 and not self._cells[col + 1][row].visited:
                unvisited_neighbors.append((col + 1, row))

            # Check Up neighbor
            if row > 0 and not self._cells[col][row - 1].visited:
                unvisited_neighbors.append((col, row - 1))

            # Check Down neighbor
            if row < self._num_rows - 1 and not self._cells[col][row + 1].visited:
                unvisited_neighbors.append((col, row + 1))

            # If no unvisited neighbors remain, backtrack out of this cell
            if len(unvisited_neighbors) == 0:
                self._draw_cell(col, row)
                return

            # Pick a random unvisited neighbor to visit next
            next_col, next_row = random.choice(unvisited_neighbors)

            # Knock down the walls between current cell and chosen neighbor:
            # Moved Left
            if next_col == col - 1:
                self._cells[col][row].has_left_wall = False
                self._cells[next_col][row].has_right_wall = False

            # Moved Right
            elif next_col == col + 1:
                self._cells[col][row].has_right_wall = False
                self._cells[next_col][row].has_left_wall = False

            # Moved Up
            elif next_row == row - 1:
                self._cells[col][row].has_top_wall = False
                self._cells[col][next_row].has_bottom_wall = False

            # Moved Down
            elif next_row == row + 1:
                self._cells[col][row].has_bottom_wall = False
                self._cells[col][next_row].has_top_wall = False

            # Recurse into the neighbor
            self._carve_passages_recursive(next_col, next_row)

    def reset_visited(self) -> None:
        """Resets the 'visited' status on all cells so pathfinding algorithms can start clean."""
        for column in self._cells:
            for cell in column:
                cell.visited = False

    # =========================
    # Rendering, Resizing & Animation Helpers
    # =========================

    def _animate(self, sleep: float| None = None)-> None:
        """Refreshes the window and introduces a tiny delay to animate wall carving/solving step-by-step."""
        if self._win is None:
            return
        self._win.redraw()

        if sleep is None:
            sleep = self._win.get_speed()
        
        time.sleep(sleep)

    def _on_window_resize(self, _width: int, _height: int) -> None:
        """Callback triggered when the window is resized.
        Recalculates cell sizes based on new canvas dimensions and redraws everything.
        """
        if self._win is None:
            return
        
        canvas_width, canvas_height = self._win.get_canvas_size()
        print(f"resize canvas size: {canvas_width}, {canvas_height}")

        # Recalculate cell pixel size to fit new canvas dimensions
        self._cell_size_x = (canvas_width - 2 * self._margin_x) / self._num_cols
        self._cell_size_y = (canvas_height - 2 * self._margin_y) / self._num_rows

        self._win.clear_canvas()
        self._redraw_cells()

        if self._solution_path:
            self._redraw_solution()

    def _redraw_cells(self) -> None:
        """Redraws every cell grid in its current state (used after window resizing)."""
        for col in range(self._num_cols):
            for row in range(self._num_rows):
                x1, y1, x2, y2 = self._get_cell_bounds(col, row)
                self._cells[col][row].draw(x1, y1, x2, y2)

        if self._win:
            self._win.redraw()
        
    def _redraw_solution(self)-> None:
        """Re-renders the solution line path if the window is resized after solving."""
        for (col, row), (neighbor_col, neighbor_row) in self._solution_path:
            self._cells[col][row].draw_move(self._cells[neighbor_col][neighbor_row])        

            if self._win:
                self._win.redraw()

    # =========================
    # Algorithm Helpers & Navigation
    # =========================

    def reset_solution(self) -> None:
        """Clears the solution path record."""
        self._solution_path = set()

    def _get_accessible_neighbors(self, col: int, row: int) -> list[tuple[int, int]]:
        """Returns a list of neighboring (col, row) cells that are connected 
        to the current cell (i.e. no wall between them).
        """
        cell = self._cells[col][row]
        neighbors = []

        # Check Left (no wall on left)
        if col > 0 and not cell.has_left_wall:
            neighbors.append((col - 1, row))

        # Check Right (no wall on right)
        if col < self._num_cols - 1 and not cell.has_right_wall:
            neighbors.append((col + 1, row))

        # Check Up (no wall on top)
        if row > 0 and not cell.has_top_wall:
            neighbors.append((col, row - 1))

        # Check Down (no wall on bottom)
        if row < self._num_rows - 1 and not cell.has_bottom_wall:
            neighbors.append((col, row + 1))

        return neighbors

    def _reconstruct_and_highlight_path(
        self, 
        came_from: dict[tuple[int, int], tuple[int, int] | None],
        visited_positions: list[tuple[int, int]] | set[tuple[int, int]]
    ) -> None:
        """Traces back from the finish cell to the start cell to render the final solution path,
        and grays out any explored dead ends that didn't lead to the goal.
        """
        self._solution_path = set()
        winning_cells = set()

        # Step 1: Trace backward from destination (bottom-right) to start (0,0)
        current = (self._num_cols - 1, self._num_rows - 1)
        while current is not None:
            winning_cells.add(current)
            prev = came_from.get(current)
            if prev is not None:
                curr_col, curr_row = current
                prev_col, prev_row = prev
                
                # Draw winning path segment
                self._cells[curr_col][curr_row].draw_move(self._cells[prev_col][prev_row])
                self._solution_path.add(((curr_col, curr_row), (prev_col, prev_row)))
            current = prev

        # Step 2: Gray out dead ends (cells explored during search that aren't on the winning path)
        for col, row in visited_positions:
            if (col, row) not in winning_cells:
                prev = came_from.get((col, row))
                if prev is not None:
                    self._cells[col][row].draw_move(
                        self._cells[prev[0]][prev[1]], undo=True
                    )

    # =========================
    # Algorithm 1: Depth-First Search (DFS)
    # =========================
    
    def solve_dfs(self) -> bool:
        """Solves the maze using Depth-First Search (DFS).
        Explores as far as possible down each branch before backtracking.
        """
        return self._solve_dfs_recursive(col=0, row=0)

    def _solve_dfs_recursive(self, col: int, row: int) -> bool:
        """Recursive helper function for DFS traversal."""
        self._animate()
        self._cells[col][row].visited = True

        # Base Case: Reached the bottom-right exit cell!
        if self._cells[col][row] == self._cells[-1][-1]:
            return True

        # Check all accessible neighbors
        for neighbor_col, neighbor_row in self._get_accessible_neighbors(col, row):
            neighbor_cell = self._cells[neighbor_col][neighbor_row]
            
            # Skip if we've already visited this neighbor
            if neighbor_cell.visited:
                continue

            # Step forward: draw move line to neighbor
            self._cells[col][row].draw_move(neighbor_cell)
            self._solution_path.add(((col, row), (neighbor_col, neighbor_row)))

            # Recurse down the path
            if self._solve_dfs_recursive(neighbor_col, neighbor_row):
                return True

            # Backtrack: If the path didn't lead to the exit, undo line and remove from path
            self._cells[col][row].draw_move(neighbor_cell, undo=True)
            self._solution_path.discard(((col, row), (neighbor_col, neighbor_row)))

        """old
            if (
                i > 0 
                and self._cells[col][row].has_left_wall == False
                and not self._cells[i - 1][j].visited
            ):
                self._cells[col][row].draw_move(self._cells[i - 1][j])
                self._solution_path.add(((i, j), (i - 1, j)))
                if self._solve_r(i -1, j) == True:
                    return True
                else:
                    self._cells[col][row].draw_move(self._cells[i - 1][j], undo= True)
                    self._solution_path.discard(((i, j), (i - 1, j)))
                    """
               
        return False

    # =========================
    # Algorithm 2: Breadth-First Search (BFS)
    # =========================
    
    def solve_bfs(self)-> bool:
        """Solves the maze using Breadth-First Search (BFS).
        Explores all cells level-by-level using a FIFO queue. Guarantees the shortest path.
        """
        start_pos = (0, 0)
        end_pos = (self._num_cols - 1, self._num_rows - 1)

        queue: deque[tuple[int, int]] = deque([(0, 0)])
        self._cells[0][0].visited = True

        # Dictionary mapping each position to where it came from: 
        # {(col, row): (prev_col, prev_row)}
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start_pos: None}
        solved = False

        while queue:
            col, row = queue.popleft()  # <-- popleft makes it a queue (FIFO)
            self._animate()

            # Check if exit is reached
            if (col, row) == end_pos:
                solved = True
                break

            for n_col, n_row in self._get_accessible_neighbors(col, row):
                if not self._cells[n_col][n_row].visited:
                    self._cells[col][row].draw_move(self._cells[n_col][n_row])
                    self._solution_path.add(((col, row), (n_col, n_row)))
                    
                    self._cells[n_col][n_row].visited = True
                    came_from[(n_col, n_row)] = (col, row)
                    queue.append((n_col, n_row))

            """old
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
                    and not self._cells[col][row].has_left_wall 
                    and not self._cells[ni][nj].visited
                ):
                    self._cells[col][row].draw_move(self._cells[ni][nj])
                    self._solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self._cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)
                
                if (ni == i + 1 
                    and i < self._num_cols - 1
                    and not self._cells[col][row].has_right_wall 
                    and not self._cells[ni][nj].visited
                ):
                    self._cells[col][row].draw_move(self._cells[ni][nj])
                    self._solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self._cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)
               
                
                if (nj == j - 1 
                    and j > 0
                    and not self._cells[col][row].has_top_wall 
                    and not self._cells[ni][nj].visited
                ):
                    self._cells[col][row].draw_move(self._cells[ni][nj])
                    self._solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self._cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)

                if (nj == j + 1 
                    and j < self._num_rows - 1
                    and not self._cells[col][row].has_bottom_wall 
                    and not self._cells[ni][nj].visited
                ):
                    self._cells[col][row].draw_move(self._cells[ni][nj])
                    self._solution_path.add(((i, j), (ni, nj)))
                    queue.append((ni, nj))
                    self._cells[ni][nj].visited = True
                    came_from[(ni, nj)] = (i, j)
        """

        # Reconstruct path and highlight dead ends if exit was reached
        if solved:
            all_visited = [
                (c, r) for c in range(self._num_cols) 
                for r in range(self._num_rows) 
                if self._cells[c][r].visited
            ]
            self._reconstruct_and_highlight_path(came_from, all_visited)

            """old
            self._solution_path = set()
            solution_path = set()  # for dead end detection
            current = (self._num_cols - 1, self._num_rows - 1)
            while current is not None:
                solution_path.add(current)  # track winning cells
                prev = came_from[current]
                if prev is not None:
                    self._cells[current[0]][current[1]].draw_move(
                        self._cells[prev[0]][prev[1]]
                    )
                    self._solution_path.add(
                        ((current[0], current[1]), (prev[0], prev[1]))
                    )
                current = prev

            # gray out dead ends
            for i in range(self._num_cols):
                for j in range(self._num_rows):
                    if self._cells[col][row].visited and (i, j) not in solution_path:
                        prev = came_from.get((i, j))
                        if prev is not None:
                            self._cells[col][row].draw_move(
                                self._cells[prev[0]][prev[1]], undo=True
                            )"""
        
        return solved

    # =========================
    # Algorithm 3: A* Search
    # =========================

    def _calculate_heuristic(self, col: int, row: int) -> int:
        """Calculates Manhattan distance from (col, row) to the bottom-right exit.
        Used as the heuristic estimate h(n) in A* search.
        """
        goal_col = self._num_cols - 1
        goal_row = self._num_rows - 1
        return abs(goal_col - col) + abs(goal_row - row)  
    

    def solve_astar(self) -> bool:
        """Solves the maze using A* Search algorithm.
        Uses path cost g(n) + heuristic h(n) to prioritize exploring cells closer to the exit.
        """
        start_pos = (0, 0)
        end_pos = (self._num_cols - 1, self._num_rows - 1)

        # Priority Queue storing tuples: (f_score, g_score, col, row)
        # f_score = cost_from_start + estimated_cost_to_goal
        start_f = self._calculate_heuristic(0, 0)
        open_set: list[tuple[int, int, int, int]] = [(start_f, 0, 0, 0)]

        self._cells[0][0].visited = True
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start_pos: None}
        g_scores: dict[tuple[int, int], int] = {start_pos: 0}

        solved = False

        while open_set:
            estimated_total_cost, cost_from_start, col, row = heapq.heappop(open_set)
            self._animate()

            if (col, row) == end_pos:
                solved = True
                break
            
            # Skip stale heap entries if a shorter route to this cell was already processed
            if cost_from_start > g_scores.get((col, row), float("inf")):
                continue

            for n_col, n_row in self._get_accessible_neighbors(col, row):
                tentative_g_score = cost_from_start + 1

                # If this path to neighbor is better than any previous one
                if tentative_g_score < g_scores.get((n_col, n_row), float("inf")):
                    g_scores[(n_col, n_row)] = tentative_g_score
                    f_score = tentative_g_score + self._calculate_heuristic(n_col, n_row)
                    
                    heapq.heappush(open_set, (f_score, tentative_g_score, n_col, n_row))
                    came_from[(n_col, n_row)] = (col, row)
                    
                    self._cells[col][row].draw_move(self._cells[n_col][n_row])
                    self._solution_path.add(((col, row), (n_col, n_row)))

            """old
            neighbors = [
                            (i - 1, j),  # left
                            (i + 1, j),  # right
                            (i, j - 1),  # up
                            (i, j + 1),  # down
                        ]
                        for ni, nj in neighbors:
                            if (ni == i - 1 
                                and i > 0 
                                and not self._cells[col][row].has_left_wall 
                            ):
                                new_g = g + 1
                                if new_g < g_score.get((ni, nj), float("inf")):
                                    g_score[(ni, nj)] = new_g
                                    new_f = new_g + self._heuristic(ni, nj)
                                    heapq.heappush(open_set, (new_f, new_g, ni, nj))
                                    came_from[(ni, nj)] = (i, j)
                                    self._cells[col][row].draw_move(self._cells[ni][nj])
                                    self._solution_path.add(((i, j), (ni, nj)))
                            
                            if (ni == i + 1 
                                and i < self._num_cols - 1
                                and not self._cells[col][row].has_right_wall 
                            ):
                                new_g = g + 1
                                if new_g < g_score.get((ni, nj), float("inf")):
                                    g_score[(ni, nj)] = new_g
                                    new_f = new_g + self._heuristic(ni, nj)
                                    heapq.heappush(open_set, (new_f, new_g, ni, nj))
                                    came_from[(ni, nj)] = (i, j)
                                    self._cells[col][row].draw_move(self._cells[ni][nj])
                                    self._solution_path.add(((i, j), (ni, nj)))
                           
                            
                            if (nj == j - 1 
                                and j > 0
                                and not self._cells[col][row].has_top_wall 
                            ):
                                new_g = g + 1
                                if new_g < g_score.get((ni, nj), float("inf")):
                                    g_score[(ni, nj)] = new_g
                                    new_f = new_g + self._heuristic(ni, nj)
                                    heapq.heappush(open_set, (new_f, new_g, ni, nj))
                                    came_from[(ni, nj)] = (i, j)
                                    self._cells[col][row].draw_move(self._cells[ni][nj])
                                    self._solution_path.add(((i, j), (ni, nj)))
            
                            if (nj == j + 1 
                                and j < self._num_rows - 1
                                and not self._cells[col][row].has_bottom_wall 
                            ):
                                new_g = g + 1
                                if new_g < g_score.get((ni, nj), float("inf")):
                                    g_score[(ni, nj)] = new_g
                                    new_f = new_g + self._heuristic(ni, nj)
                                    heapq.heappush(open_set, (new_f, new_g, ni, nj))
                                    came_from[(ni, nj)] = (i, j)
                                    self._cells[col][row].draw_move(self._cells[ni][nj])
                                    self._solution_path.add(((i, j), (ni, nj)))
            """
            

        # Reconstruct path and highlight dead ends if exit was reached
        if solved:
            self._reconstruct_and_highlight_path(came_from, set(g_scores.keys()))

            """old
            self._solution_path = set()
                        solution_path = set()  # for dead end detection
                        current = (self._num_cols - 1, self._num_rows - 1)
                        while current is not None:
                            solution_path.add(current)  # track winning cells
                            prev = came_from[current]
                            if prev is not None:
                                self._cells[current[0]][current[1]].draw_move(
                                    self._cells[prev[0]][prev[1]]
                                )
                                self._solution_path.add(
                                    ((current[0], current[1]), (prev[0], prev[1]))
                                )
                            current = prev
            
                        # gray out dead ends
                        for i in range(self._num_cols):
                            for j in range(self._num_rows):
                                if (i, j) in g_score and (i, j) not in solution_path:
                                    prev = came_from.get((i, j))
                                    if prev is not None:
                                        self._cells[col][row].draw_move(
                                            self._cells[prev[0]][prev[1]], undo=True
                                        )
            """
        
        return solved
