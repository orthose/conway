import sys
import os
import time
import random
import threading
import tkinter as tk

# Nombre de cases du tableau
n = int(sys.argv[1])
assert 0 < n

window = tk.Tk()

window_size = min(window.winfo_screenwidth(), window.winfo_screenheight())
window.geometry(f"{window_size}x{window_size}")
window.configure(bg="white")

frame = tk.Frame(window)
frame.pack(fill="both", expand=True)

# Plateau principal de (n + 2) * (n + 2) cases pour ne pas gérer les bordures
board_size = n + 2
current_board = [[False] * board_size for _ in range(board_size)]
labels = [[None] * n for _ in range(n)]

# Initialisation aléatoire du plateau
for i in range(1, board_size-1):
    for j in range(1, board_size-1):
        current_board[i][j] = random.choice([True, False])
        label = tk.Label(frame,
            bg=("black" if current_board[i][j] else "white"),
            )
        label.grid(row=i-1, column=j-1, sticky="nsew")
        labels[i-1][j-1] = label

for i in range(n):
    frame.rowconfigure(i, weight=1)
    frame.columnconfigure(i, weight=1)


# Vue du plateau principal utilisée pour sa modification
previous_board = [line.copy() for line in current_board]


# Fonction d'affichage en console du plateau
def print_board(b):
    global board_size
    cell_to_str = lambda cell: 'O' if cell else '-'

    for i in range(1, board_size-1):
        print(end='\n')
        for j in range(1, board_size-1):
            print(cell_to_str(b[i][j])+' ', end='')
            labels[i-1][j-1].config(bg=("black" if current_board[i][j] else "white"))
    print(end='\n')


epoch = 0
diff = 0

# Fonction appelée par un seul thread lorsque la première barrière
# est sur le point d'être passée
def callback_barrier_current_board():
    global current_board, epoch, diff
    diff = 0 # Pas besoin de lock car appel de la fonction synchrone
    epoch += 1

    time.sleep(0.10)
    os.system("clear")
    print(epoch)
    print_board(current_board)


barrier_current_board = threading.Barrier(n * n, action=callback_barrier_current_board)
barrier_previous_board = threading.Barrier(n * n)
lock_diff = threading.Lock()

# Fonction de mise à jour du plateau
def update_board(cb, pb, i, j):
    global barrier_current_board, barrier_previous_board, diff
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

        # Est-ce que la case (i, j) a changé ?
        lock_diff.acquire()
        diff += (pb[i][j] != cb[i][j])
        lock_diff.release()
        # Modification du plateau précédent
        pb[i][j] = cb[i][j]
        # On attend que tous les threads modifient le plateau précédent
        barrier_previous_board.wait()

        # Si aucune modification par rapport à l'époque précédente alors on arrête
        if diff == 0: break


threads = [threading.Thread(target=update_board, args=(current_board, previous_board, i, j))
    for i in range(1, board_size-1) for j in range(1, board_size-1)]

print_board(current_board)
for t in threads: t.start()
window.mainloop()
