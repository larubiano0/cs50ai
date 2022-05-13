"""
Tic Tac Toe Player
"""

from copy import *


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
    Xcount = 0
    Ocount = 0
    for i in board:
        for j in i:
            if j==X: Xcount+=1
            elif j==O: Ocount+=1
    if Xcount>Ocount: return O
    elif Xcount==Ocount: return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    act = set()
    i = 0
    while i<=2:
        j=0
        while j<=2:
            if board[i][j]==EMPTY:
                act.add((i,j))
            j+=1
        i+=1
    return act

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j]: raise NameError('Invalid action')
    newBoard = deepcopy(board)
    turn = player(newBoard)
    newBoard[i][j] = turn
    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in board: #horizontal line 
        if i == [X, X, X]: return X
        elif i == [O, O, O]: return O

    c = 0
    while c<=2: #vertical line
        if board[0][c]==X and board[1][c]==X and board[2][c]==X: return X
        elif board[0][c]==O and board[1][c]==O and board[2][c]==O: return O
        c+=1

    #diagonal
    if board[0][0] == X and board[1][1] == X and board[2][2] == X: return X
    elif board[0][0] == O and board[1][1] == O and board[2][2] == O: return O

    #anti diagonal
    if board[0][2] == X and board[1][1] == X and board[2][0] == X: return X
    elif board[0][2] == O and board[1][1] == O and board[2][0] == O: return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board): return True
    if not len(actions(board)): return True
    return False 


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    W = winner(board)
    if W == X: return 1
    if W == O: return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    turn = player(board)
    if terminal(board): return None
    if turn==X: 
        return maxV(board)[0]
    elif turn==O: 
        return minV(board)[0]

def maxV(board):
    if terminal(board): return None, utility(board)
    acts = list(actions(board)) #All the possible actions 
    boards = []           #All the possible boards
    for i in acts:
        boards.append(result(board,i))
    score = [] #The score of each board
    for i in boards:
        if terminal(i): score.append(utility(i))
        else: score.append(minV(i)[1])
    v = max(score)
    move = acts[score.index(v)]
    return move, v 


def minV(board):
    if terminal(board): return None, utility(board)
    acts = list(actions(board)) #All the possible actions 
    boards = []           #All the possible boards
    for i in acts:
        boards.append(result(board,i))
    score = [] #The score of each board
    for i in boards:
        if terminal(i): score.append(utility(i))
        else: score.append(maxV(i)[1])
    v = min(score)
    move = acts[score.index(v)]
    return move, v 