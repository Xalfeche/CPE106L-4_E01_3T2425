import unittest
import oxo_logic

class TestGameInitialization(unittest.TestCase):

	def test_newGame(self):
		game = oxo_logic.newGame()
		self.assertEqual(len(game), 9, "Game board should have 9 cells.")
		self.assertTrue(all(cell == " " for cell in game), "All cells should be empty.")

class TestUserMove(unittest.TestCase):

	def setUp(self):
		self.game = oxo_logic.newGame()

	def test_valid_user_move(self):
		cell = 0  # Choose the first cell
		result = oxo_logic.userMove(self.game, cell)
		self.assertEqual(self.game[cell], "X", "User move should place 'X' in the chosen cell.")
		self.assertEqual(result, "", "No winner after a single move.")

	def test_invalid_user_move(self):
		cell = 0
		oxo_logic.userMove(self.game, cell)
		with self.assertRaises(ValueError):
			oxo_logic.userMove(self.game, cell)
			
class TestComputerMove(unittest.TestCase):

	def setUp(self):
		self.game = oxo_logic.newGame()

	def test_computer_move(self):
		result = oxo_logic.computerMove(self.game)
		self.assertNotEqual(result, "D", "Game should not be a draw after the first move.")
		self.assertTrue(any(cell == "O" for cell in self.game), "Computer move should place 'O' on the board.")

class TestWinningMove(unittest.TestCase):

	def setUp(self):
		self.game = oxo_logic.newGame()

	def test_winning_move_row(self):
		cells = [0, 1, 2]
		for cell in cells:
			if cell == 0:
				oxo_logic.userMove(self.game, cell)
			else:
				if cell % 2 == 1:
					oxo_logic.computerMove(self.game)
				else:
					oxo_logic.userMove(self.game, cell)
		result = oxo_logic.userMove(self.game, 2)
		self.assertEqual(result, "X", "Should detect a horizontal win.")

class TestDrawCondition(unittest.TestCase):

	def setUp(self):
		self.game = oxo_logic.newGame()

	def test_draw_condition(self):
		for i in range(9):
			if i % 2 == 0:
				oxo_logic.userMove(self.game, i)
			else:
				oxo_logic.computerMove(self.game)
		result = oxo_logic._isWinningMove(self.game)
		self.assertFalse(result, "No win should be detected after filling the board.")
		self.assertTrue(all(cell != " " for cell in self.game), "All cells should be filled.")

class TestSaveRestore(unittest.TestCase):

	def setUp(self):
		self.game = oxo_logic.newGame()
		oxo_logic.userMove(self.game, 0)

	def test_save_restore(self):
		oxo_logic.saveGame(self.game)
		restored_game = oxo_logic.restoreGame()
		self.assertEqual(restored_game, self.game, "Restored game should match the original.")

