"""
Tic Tac Toe Player
"""

import math
import copy

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

    if terminal(board):
        return "Game Over"

    sumX = 0
    sumO = 0
    sumE = 0

    for row in board:
        for space in row:
            if space == X:
                sumX += 1
            elif space == O:
                sumO += 1
            else:
                sumE += 1
    
    if sumX > sumO:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    if terminal(board):
        return "Game Over"

    moves = set()

    for i in range(len(board[0])):

        for j in range(len(board[0])):

            if board[i][j] == EMPTY:

                tup = (i, j)
                moves.add(tup)

    # print("Board ", board)
    # print("This is what actions returns: ", moves)
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action is None:

        raise Exception("Not valid")

    possibleBoard = copy.deepcopy(board)

    if possibleBoard[action[0]][action[1]] != EMPTY:

        raise Exception("That space is arleady filled")

    if player(possibleBoard) == X or player(possibleBoard) == O:
        possibleBoard[action[0]][action[1]] = player(possibleBoard)

    return possibleBoard



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    i = 0
    k = 0

    for row in board:

        if row.count(X) == 3 or row.count(O) == 3:

            return row[i]

    for j in range(3):

        if board[i][j] == X and board[i + 2][j] == X and board[i + 1][j] == X:
            if board[i][j] == board[i + 1][j] and board[i][j] == board[i + 2][j]:
                return board[i][j]
        elif board[i][j] == O and board[i + 2][j] == O and board[i + 1][j] == O:
            if board[i][j] == board[i + 1][j] and board[i][j] == board[i + 2][j]:
                return board[i][j]

    if board[i][k] == board[i + 1][k + 1] and board[i][k] == board[i + 2][k + 2]:

        return board[i][k]

    if board[i + 2][k] == board[i + 1][k + 1] and board[i + 2][k] == board[i][k + 2]:

        return board[i + 2][k]

    if board.count(EMPTY) > 0:
        return None

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) == X or winner(board) == O:
        return True

    for row in board:
        for space in row:
            if space == EMPTY:
                return False

    return True


def utility(board):

    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    def maxValue(board):

        if terminal(board):

            return [utility(board), (None, None)]

        v = [-10, (None, None)]

        for action in actions(board):

            value = minValue(result(board, action))

            if v[0] < value[0]:

                v = [value[0], action]

        return v


    def minValue(board):

        if terminal(board):

            return [utility(board), (None, None)]

        v = [10, (None, None)]

        for action in actions(board):

            value = maxValue(result(board, action))

            if v[0] > value[0]:

                v = [value[0], action]

        return v


    if terminal(board):
        return None

    if player(board) == X:
        v = maxValue(board)

    elif player(board) == O:
        v = minValue(board)

    print(v)
    return v[1]
