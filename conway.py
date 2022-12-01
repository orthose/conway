import sys
import os
import time
import random
import threading

# Nombre de cases du tableau
n = int(sys.argv[1])
assert 0 < n

# Plateau principal de (n + 2) * (n + 2) cases pour ne pas gérer les bordures
board_size = n + 2
board = [[False] * board_size for _ in range(board_size)]

# Initialisation aléatoire du plateau
for i in range(1, board_size-1):
    for j in range(1, board_size-1):
        board[i][j] = random.choice([True, False])

# Vue du plateau principal utilisée pour sa modification
board_view = [line.copy() for line in board]


# Fonction de mise à jour du plateau
def update_board(b, v, i, j):
    global board_size
    # Mise à jour du plateau principal sans modifier la vue
    neighbors = (
          v[i-1][j-1] + v[i-1][j] + v[i-1][j+1]
        + v[ i ][j-1]             + v[ i ][j+1]
        + v[i+1][j-1] + v[i+1][j] + v[i+1][j+1]
    )
    b[i][j] = (
        (not b[i][j] and neighbors == 3)
        or (b[i][j] and neighbors in [2, 3])
    )


# Fonction d'affichage en console du plateau
def print_board(b):
    global board_size
    cell_to_str = lambda cell: 'O' if cell else '-'
    for i in range(1, board_size-1):
        print(end='\n')
        for j in range(1, board_size-1):
            print(cell_to_str(b[i][j])+' ', end='')
    print(end='\n')


# Boucle principale
epoch = 0
while True:
    time.sleep(0.5)
    os.system("clear")
    print(epoch)
    print_board(board)
    epoch += 1

    threads = [threading.Thread(target=update_board, args=(board, board_view, i, j))
        for i in range(1, board_size-1) for j in range(1, board_size-1)]

    for t in threads: t.start()
    for t in threads: t.join()

    # Mise à jour de la vue
    for i in range(1, board_size-1):
        for j in range(1, board_size-1):
            board_view[i][j] = board[i][j]
