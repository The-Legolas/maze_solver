import unittest

from maze import Maze


class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)
        
        self.assertEqual(len(m1._cells), num_cols)
        self.assertEqual(len(m1._cells[0]), num_rows)

    def test_maze_create_cells_large(self):
        num_cols = 16
        num_rows = 12
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)

        self.assertEqual(len(m1._cells), num_cols)
        self.assertEqual(len(m1._cells[0]), num_rows)
    

    def test_maze_break_entrance_and_exit(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)

        self.assertFalse(m1._cells[0][0].has_top_wall)
        self.assertFalse(m1._cells[num_cols - 1][num_rows - 1].has_bottom_wall)
    
    def test_maze_reset_cells_visited(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)

        m1.reset_visited()
        for col in m1._cells:
            for cell in col:
                self.assertFalse(cell.visited)

    def test_deterministic_seed_generation(self):
        """Ensures two mazes generated with the same seed produce identical wall layouts."""
        m1 = Maze(0, 0, 6, 6, 10, 10, seed=42)
        m2 = Maze(0, 0, 6, 6, 10, 10, seed=42)

        for col in range(6):
            for row in range(6):
                c1, c2 = m1._cells[col][row], m2._cells[col][row]
                self.assertEqual(c1.has_left_wall, c2.has_left_wall)
                self.assertEqual(c1.has_right_wall, c2.has_right_wall)
                self.assertEqual(c1.has_top_wall, c2.has_top_wall)
                self.assertEqual(c1.has_bottom_wall, c2.has_bottom_wall)

    def test_calculate_heuristic(self):
        """Tests Manhattan distance calculation for A* search."""
        num_cols, num_rows = 10, 10
        m = Maze(0, 0, num_rows, num_cols, 10, 10)

        # Distance from top-left (0,0) to bottom-right (9,9) should be 9 + 9 = 18
        heuristic_start = m._calculate_heuristic(0, 0)
        self.assertEqual(heuristic_start, 18)

        # Distance from goal (9,9) to goal (9,9) should be 0
        heuristic_goal = m._calculate_heuristic(9, 9)
        self.assertEqual(heuristic_goal, 0)

    def test_get_accessible_neighbors(self):
        """Verifies neighbor retrieval returns valid coordinates within bounds."""
        m = Maze(0, 0, 5, 5, 10, 10, seed=10)
        neighbors = m._get_accessible_neighbors(0, 0)

        self.assertIsInstance(neighbors, list)
        for n_col, n_row in neighbors:
            self.assertTrue(0 <= n_col < 5)
            self.assertTrue(0 <= n_row < 5)

    def test_solve_dfs(self):
        """Validates that DFS solves a generated maze."""
        m = Maze(0, 0, 8, 8, 10, 10, seed=100)
        m.reset_visited()
        self.assertTrue(m.solve_dfs())

    def test_solve_bfs(self):
        """Validates that BFS solves a generated maze."""
        m = Maze(0, 0, 8, 8, 10, 10, seed=100)
        m.reset_visited()
        self.assertTrue(m.solve_bfs())

    def test_solve_astar(self):
        """Validates that A* search solves a generated maze."""
        m = Maze(0, 0, 8, 8, 10, 10, seed=100)
        m.reset_visited()
        self.assertTrue(m.solve_astar())

    def test_reset_solution(self):
        """Ensures reset_solution clears solution path segments."""
        m = Maze(0, 0, 6, 6, 10, 10, seed=50)
        m.reset_visited()
        m.solve_bfs()

        self.assertGreater(len(m._solution_path), 0)
        m.reset_solution()
        self.assertEqual(len(m._solution_path), 0)

if __name__ == "__main__":
    unittest.main()
