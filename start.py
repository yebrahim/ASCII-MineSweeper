import curses
import curses.textpad
import time, random
from curses import wrapper

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)

# colors:
color_separator = '|'
color_closed = curses.ACS_CKBOARD
color_empty = ' '
color_bomb = 'X'
color_flag = 'F'
color_hidden_bomb = 'H'

# params
board_width = 10
board_height = 10
board_top = 0
board_left = 0
difficulty = 0.1
num_bombs = board_width * board_height * difficulty

# data
data = []

current_row = current_col = 0

def count_surrounding_bombs(row, col):
    neighbors = [[0,1], [0,-1], [1,0], [-1,0], [-1,-1], [1,1], [1,-1], [-1,1]]
    count = 0
    for n in neighbors:
        r,c = row+n[0], col+n[1]
        allbombs = True
        if r < 0 or r >= board_height or c < 0 or c >= board_width:
            continue
        if data[r][c] == color_hidden_bomb:
            count += 1
        else:
            allbombs = False
        return (count, allbombs)

def init_data():
    global data, num_bombs

    for i in range(board_height):
        data.append(board_width*[color_closed])
    while num_bombs:
        brow, bcol = random.randrange(0, board_height), random.randrange(0, board_width)
        if data[brow][bcol] == color_hidden_bomb or count_surrounding_bombs(brow, bcol)[1]:
            continue
        data[brow][bcol] = color_hidden_bomb
        num_bombs -= 1

def setCell(row, col, val, state=curses.A_DIM):
    stdscr.addch(board_top + row, board_left + col*2, color_separator, curses.A_DIM)
    stdscr.addch(board_top + row, board_left + col*2 + 1, val, state)

def moveCurrentCell(newrow, newcol):
    global current_row, current_col
    if newrow < 0 or newrow >= board_height or newcol < 0 or newcol >= board_width:
        return
    val = data[current_row][current_col]
    newval = data[newrow][newcol]
    if val == color_hidden_bomb: val = color_closed
    if newval == color_hidden_bomb: newval = color_closed
    stdscr.addch(board_top + current_row, board_left + current_col*2 + 1, val)
    stdscr.addch(board_top + newrow, board_left + newcol*2 + 1, newval, curses.A_BLINK)
    current_row, current_col = newrow, newcol

def main(stdscr):
    stdscr.clear()
    init_data()
    for i in range(board_height):
        for j in range(board_width):
            setCell(i, j, color_closed)
        stdscr.addch(i, board_left + board_width*2, color_separator, curses.A_DIM)

    # setCell(5,5,color_flag)
    # setCell(2,5,color_empty)
    # setCell(2,6,color_empty)
    # setCell(3,5,color_empty)
    # setCell(3,6,color_empty)
    # setCell(3,7,color_empty)
    # setCell(9,7,color_bomb)
    # setCell(1,5,'3')
    # stdscr.addch(board_top + 8, board_left + 8*2 + 1, '8', curses.A_BLINK)

    moveCurrentCell(0, 0)
    stdscr.refresh()
    while 1:
        newrow, newcol = current_row, current_col
        c=stdscr.getch()
        if c == curses.KEY_RIGHT:
            newrow, newcol = current_row, current_col + 1
        elif c == curses.KEY_LEFT:
            newrow, newcol = current_row, current_col - 1
        elif c == curses.KEY_UP:
            newrow, newcol = current_row - 1, current_col
        elif c == curses.KEY_DOWN:
            newrow, newcol = current_row + 1, current_col
        elif c == ord('f') or c == ord('F'):
            if data[current_row][current_col] not in [color_closed, color_hidden_bomb, color_flag]:
                continue
            newcolor = color_flag if data[current_row][current_col] != color_flag else color_closed
            data[current_row][current_col] = newcolor
            setCell(current_row, current_col, newcolor, curses.A_BLINK)
        elif c == ord('q') or c == ord('Q'):
            break
        moveCurrentCell(newrow, newcol)
        stdscr.refresh()

wrapper(main)
