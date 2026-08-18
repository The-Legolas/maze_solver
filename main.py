from typing import Any
import sys
import random

from graphics import Window
from maze import Maze


def main()-> None:
    # Increase recursion depth limit to support larger maze grid traversals
    sys.setrecursionlimit(10000)

    screen_x = 800
    screen_y = 600

    # State cache to preserve the maze layout when only changing/re-running algorithms
    app_state: dict[str, Any] = {}

    win = Window(screen_x, screen_y, on_new_maze=lambda: run_maze(win, app_state))

    run_maze(win, app_state)
    win.wait_for_close()

def run_maze(win: Window, state: dict[str, Any]) -> None:
    """Handles creating or resetting the maze, and invoking the selected search algorithm."""
    seed = win.get_seed() or None
    num_rows, num_cols = win.get_maze_dimensions()
    selected_algo = win.get_algo()

    # Check if we can reuse the existing maze layout (same dimensions & seed)
    same_config = (
        state.get("maze") is not None
        and seed is not None
        and state.get("seed") == seed
        and state.get("num_rows") == num_rows
        and state.get("num_cols") == num_cols
    )

    same_config = (
        state.get("maze") is not None
        and seed is not None
        and state.get("seed") == seed
        and state.get("num_rows") == num_rows
        and state.get("num_cols") == num_cols
    )

    if same_config:
        print("Reusing existing maze structure...")
        maze: Maze = state["maze"]
        win.clear_canvas()
        maze._redraw_cells()    # Repaint pristine walls without solution paths
        maze.reset_visited()    # Clear cell visited flags
        maze.reset_solution()   # Safely clear solution path history
    else:
        win.clear_canvas()
        random.seed(seed)

        margin = 50
        screen_x, screen_y = win.get_canvas_size()
        cell_size_x = (screen_x - 2 * margin) / num_cols
        cell_size_y = (screen_y - 2 * margin) / num_rows
        print(f"run_maze canvas size: {screen_x}, {screen_y}")

        maze = Maze(margin, margin, num_rows, num_cols, cell_size_x, cell_size_y, win, seed=seed)
        print("Maze generated successfully.")
        state.update({"maze": maze, "seed": seed, "num_rows": num_rows, "num_cols": num_cols})


    # Dispatch to the chosen pathfinding algorithm
    is_solvable = False
    print(f"Solving maze with algorithm: {selected_algo}...")


    if selected_algo == "DFS":
        is_solvable = maze.solve_dfs()
    elif selected_algo == "BFS":
        is_solvable = maze.solve_bfs()
    elif selected_algo == "A*":
        is_solvable = maze.solve_astar()
    else:
        print(f"Warning: Unknown algorithm '{selected_algo}' selected.")
        return

    # Output final solution status
    if not is_solvable:
        print("maze can not be solved!")
    else:
        print("maze solved!")


if __name__ == "__main__":
    main()