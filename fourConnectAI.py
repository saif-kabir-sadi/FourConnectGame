import math
import random

class ConnectFourGame:
    def __init__(self, rows=6, cols=7):
        self.ROWS = rows
        self.COLS = cols
        self.board = []
        for _ in range(rows):
            row = []
            for _ in range(cols):
                row.append(' ')
            self.board.append(row)
    
    def check_winner(self, player):
        # Horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                if (self.board[row][col] == self.board[row][col+1] == 
                    self.board[row][col+2] == self.board[row][col+3] == player):
                    return [(row, col), (row, col+1), (row, col+2), (row, col+3)]
        
        # Vertical
        for row in range(self.ROWS - 3):
            for col in range(self.COLS):
                if (self.board[row][col] == self.board[row+1][col] == 
                    self.board[row+2][col] == self.board[row+3][col] == player):
                    return [(row, col), (row+1, col), (row+2, col), (row+3, col)]
        
        # Diagonal (left-right)
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                if (self.board[row][col] == self.board[row+1][col+1] == 
                    self.board[row+2][col+2] == self.board[row+3][col+3] == player):
                    return [(row, col), (row+1, col+1), (row+2, col+2), (row+3, col+3)]
        
        # Diagonal (right-left)
        for row in range(self.ROWS - 3):
            for col in range(3, self.COLS):
                if (self.board[row][col] == self.board[row+1][col-1] == 
                    self.board[row+2][col-2] == self.board[row+3][col-3] == player):
                    return [(row, col), (row+1, col-1), (row+2, col-2), (row+3, col-3)]
        
        return None

    def is_draw(self):
        for col in range(self.COLS):
            if self.board[0][col] == ' ':
                return False
        return True

    def get_valid_moves(self):
        moves = []
        for col in range(self.COLS):
            if self.board[0][col] == ' ':
                moves.append(col)
        return moves

    def drop_piece(self, col, player):
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == ' ':
                self.board[row][col] = player
                return row
        return -1
    def reset_board(self):
        self.board = []
        for _ in range(self.ROWS):
            row = []
            for _ in range(self.COLS):
                row.append(' ')
            self.board.append(row)

    def remove_piece(self, row, col):
        self.board[row][col] = ' '

    def minimax():
        print("Minimax-code")
        
    def get_ai_move():
        print("AI-code")