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
current_board = [[False] * board_size for _ in range(board_size)]

# Initialisation aléatoire du plateau
for i in range(1, board_size-1):
    for j in range(1, board_size-1):
        current_board[i][j] = random.choice([True, False])

# Vue du plateau principal utilisée pour sa modification
previous_board = [line.copy() for line in current_board]


epoch = 0
# Fonction d'affichage en console du plateau
def print_board(b):
    global board_size, epoch
    cell_to_str = lambda cell: 'O' if cell else '-'

    time.sleep(0.5)
    os.system("clear")
    print(epoch)

    for i in range(1, board_size-1):
        print(end='\n')
        for j in range(1, board_size-1):
            print(cell_to_str(b[i][j])+' ', end='')
    print(end='\n')
    epoch += 1


barrier_current_board = threading.Barrier(n * n, action=lambda: print_board(current_board))
barrier_previous_board = threading.Barrier(n * n)

# Fonction de mise à jour du plateau
def update_board(cb, pb, i, j):
    global barrier_current_board, barrier_previous_board
    while True:
        # Mise à jour du plateau principal sans modifier la vue
        neighbors = (
              pb[i-1][j-1] + pb[i-1][j] + pb[i-1][j+1]
            + pb[ i ][j-1]              + pb[ i ][j+1]
            + pb[i+1][j-1] + pb[i+1][j] + pb[i+1][j+1]
        )
        cb[i][j] = (
            (not cb[i][j] and neighbors == 3)
            or (cb[i][j] and neighbors in [2, 3])
        )
        # On attend que tous les threads modifient le plateau principal
        barrier_current_board.wait()

        # Modification du plateau précédent
        pb[i][j] = cb[i][j]
        # On attend que tous les threads modifient le plateau précédent
        barrier_previous_board.wait()


threads = [threading.Thread(target=update_board, args=(current_board, previous_board, i, j))
    for i in range(1, board_size-1) for j in range(1, board_size-1)]

print_board(current_board)
for t in threads: t.start()
