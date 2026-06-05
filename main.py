from graphics import Window
from maze import Maze
import sys
import random


def main():
    
    sys.setrecursionlimit(10000)
    screen_x = 800
    screen_y = 600
    state = {}
    win = Window(screen_x, screen_y, on_new_maze=lambda: run_maze(win, state))
    run_maze(win, state)

    win.wait_for_close()

def run_maze(win: Window, state: dict):
    seed = win.get_seed() or None
    num_rows, num_cols = win.get_maze_dimensions()
    algo = win.get_algo()

    same_config = (
        state.get("maze") is not None
        and seed is not None
        and state.get("seed") == seed
        and state.get("num_rows") == num_rows
        and state.get("num_cols") == num_cols
    )

    if same_config:
        maze = state["maze"]
        win.clear_canvas()
        maze.redraw_cells()   # repaints walls only, no move lines
        maze.reset_visited()
        maze.__solution_path = set()  # clear stored solution path too
    else:
        win.clear_canvas()
        random.seed(seed)
        margin = 50
        screen_x, screen_y = win.get_canvas_size()
        cell_size_x = (screen_x - 2 * margin) / num_cols
        cell_size_y = (screen_y - 2 * margin) / num_rows
        print(f"run_maze canvas size: {screen_x}, {screen_y}")
        maze = Maze(margin, margin, num_rows, num_cols, cell_size_x, cell_size_y, win, seed=seed)
        print("maze created")
        state.update({"maze": maze, "seed": seed, "num_rows": num_rows, "num_cols": num_cols})



    print("maze created")
    algo = win.get_algo()
    if algo == "DFS":
        is_solvable = maze.solve_dfs()
    elif algo == "BFS":
        is_solvable = maze.solve_bfs()
    elif algo == "A*":
        is_solvable = maze.solve_astar()

    if not is_solvable:
        print("maze can not be solved!")
    else:
        print("maze solved!")


if __name__ == "__main__":
    main()