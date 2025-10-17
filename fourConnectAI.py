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

    def minimax(self, depth, is_maximizing, max_depth=5, alpha=-math.inf, beta=math.inf):
        if self.check_winner('O'):
            return 100 - depth
        if self.check_winner('X'):
            return depth - 100
        if self.is_draw() or depth >= max_depth:
            return 0

        if is_maximizing:
            value = -math.inf
            for col in self.get_valid_moves():
                row = self.drop_piece(col, 'O')
                score = self.minimax(depth + 1, False, max_depth, alpha, beta)
                self.remove_piece(row, col)
                value = max(value, score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    # beta cut-off
                    break
            return value
        else:
            value = math.inf
            for col in self.get_valid_moves():
                row = self.drop_piece(col, 'X')
                score = self.minimax(depth + 1, True, max_depth, alpha, beta)
                self.remove_piece(row, col)
                value = min(value, score)
                beta = min(beta, value)
                if alpha >= beta:
                    # alpha cut-off
                    break
            return value
        
    def get_ai_move():
        print("AI-code")