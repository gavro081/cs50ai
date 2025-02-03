"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
from json.encoder import INFINITY

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count, o_count = 0,0
    for i in range(3):
        for j in range(3):
            move = board[i][j]
            if move == X:
                x_count += 1
            elif move == O:
                o_count += 1

    if x_count == o_count:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions_ = set()
    for i in range(3):
        for j in range(3):
            if not board[i][j]:
                actions_.add((i, j))
    return actions_

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if i < 0 or j < 0 or i >= 3 or j >= 3 or board[i][j] is not None:
        raise ValueError
    new_board = deepcopy(board)
    new_board[i][j] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check rows
    sign = O if player(board) == X else X
    for row in range(3):
        if board[row][0] == sign and board[row][1] == sign and board[row][2] == sign:
            return sign
    # check cols
    for col in range(3):
        if board[0][col] == sign and board[1][col] == sign and board[2][col] == sign:
            return sign

    # check diagonals
    if board[0][2] == sign and board[1][1] == sign and board[2][0] == sign:
        return sign
    if board[0][0] == sign and board[1][1] == sign and board[2][2] == sign:
        return sign
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or len(actions(board)) == 0


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winner_ = winner(board)
    if winner_ == X:
        return 1
    if winner_ == O:
        return -1
    return 0

def min_value(board):
    if terminal(board):
        return utility(board)
    curr_min = math.inf
    for action in actions(board):
        curr_min = min(curr_min, max_value(result(board, action)))
    return curr_min


def max_value(board):
    if terminal(board):
        return utility(board)
    curr_max = -math.inf
    for action in actions(board):
        curr_max = max(curr_max, min_value(result(board, action)))
    return curr_max

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    sign = player(board)
    best_move = None
    if sign == X:
        curr_max = -math.inf
        for action in actions(board):
            move_value = min_value(result(board, action))
            if move_value > curr_max:
                curr_max = move_value
                best_move = action
    else:
        curr_min = math.inf
        for action in actions(board):
            move_value = max_value(result(board, action))
            if move_value < curr_min:
                curr_min = move_value
                best_move = action

    return best_move

