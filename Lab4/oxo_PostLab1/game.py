import random # Import the random module

class Game:
    def __init__(self):
        self.board = self.newGame()

    def newGame(self):
        ' return new empty game'
        return list(" " * 9)

    def userMove(self, cell):
        if self.board[cell] != ' ':
            raise ValueError('Invalid cell')
        else:
            self.board[cell] = 'X'
        if self._isWinningMove():
            return 'X'
        else:
            return ""

    def computerMove(self):
        cell = self._generateMove()
        if cell == -1:
            return ('D', -1) # Return draw result and no cell
        self.board[cell] = 'O'
        if self._isWinningMove():
            return ('O', cell) # Return win result and the cell
        else:
            return ('', cell) # Return no win result and the cell

    def _generateMove(self):
        ''' generate a random cell from those available.
            If all cells are used return -1'''
        options = [i for i in range(len(self.board)) if self.board[i] == " "]
        if options:
            return random.choice(options)
        else:
            return -1

    def _isWinningMove(self):
        wins = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                (0, 4, 8), (2, 4, 6))

        for a, b, c in wins:
            chars = self.board[a] + self.board[b] + self.board[c]
            if chars == 'XXX' or chars == 'OOO':
                return True
        return False