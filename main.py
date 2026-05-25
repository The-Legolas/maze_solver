from graphics import Window
from maze import Maze
import sys


def main():
    
    sys.setrecursionlimit(10000)
    screen_x = 800
    screen_y = 600
    win = Window(screen_x, screen_y, on_new_maze=lambda: run_maze(win))
    run_maze(win)

    win.wait_for_close()

def run_maze(win: Window):
    win.clear_canvas()

    num_rows = 22
    num_cols = 32
    margin = 50
    screen_x = 800
    screen_y = 600
    cell_size_x = (screen_x - 2 * margin) / num_cols
    cell_size_y = (screen_y - 2 * margin) / num_rows

    maze = Maze(margin, margin, num_rows, num_cols, cell_size_x, cell_size_y, win, seed=85530929557)
    print("maze created")
    if win.get_algo() == "DFS":
        is_solvable = maze.solve_dfs()
    else:
        is_solvable = maze.solve_bfs()

    if not is_solvable:
        print("maze can not be solved!")
    else:
        print("maze solved!")


if __name__ == "__main__":
    main()