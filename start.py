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
neighbors = [[0,1], [0,-1], [1,0], [-1,0], [-1,-1], [1,1], [1,-1], [-1,1]]

def validate_boundaries(row, col):
    if row < 0 or row >= board_height or col < 0 or col >= board_width:
        return False
    return True

class cell(object):
    def __init__(self, color, bomb_count):
        self.color, self.bomb_count = color, bomb_count

def count_surrounding_bombs(row, col):
    count = 0
    for n in neighbors:
        r,c = row+n[0], col+n[1]
        allbombs = True
        if not validate_boundaries(r, c):
            continue
        if data[r][c].bomb_count == -1:
            count += 1
        else:
            allbombs = False
        return (count, allbombs)

def declare_bomb(row, col):
    for n in neighbors:
        r,c = row+n[0], col+n[1]
        if not validate_boundaries(r, c) or data[r][c].bomb_count == -1:
            continue
        data[r][c].bomb_count += 1

def init_data():
    global data, num_bombs

    # build 2D matrix
    for i in range(board_height):
        row = []
        for j in range(board_width):
            row.append(cell(color_closed, 0))
        data.append(row)
    # add bombs
    while num_bombs:
        brow, bcol = random.randrange(0, board_height), random.randrange(0, board_width)
        if data[brow][bcol] == color_hidden_bomb or count_surrounding_bombs(brow, bcol)[1]:
            continue
        data[brow][bcol].bomb_count = -1
        num_bombs -= 1
        declare_bomb(brow, bcol)

def setCell(row, col, val, state=curses.A_DIM):
    if val == color_flag:
        state = curses.A_REVERSE
    stdscr.addch(board_top + row, board_left + col*2, color_separator, curses.A_DIM)
    stdscr.addch(board_top + row, board_left + col*2 + 1, val, state)

def moveCurrentCell(newrow, newcol):
    global current_row, current_col
    if not validate_boundaries(newrow, newcol):
        return
    val = data[current_row][current_col].color
    newval = data[newrow][newcol].color
    if val == color_hidden_bomb: val = color_closed
    if newval == color_hidden_bomb: newval = color_closed
    setCell(current_row, current_col, val)
    stdscr.addch(board_top + newrow, board_left + newcol*2 + 1, newval, curses.A_BLINK)
    current_row, current_col = newrow, newcol

def reveal_cell(row, col):
    d = data[row][col].bomb_count + ord('0')
    if d == ord('0'):
        d = color_empty
    setCell(row, col, d)
    data[row][col].color = d
    if d == color_empty:
        for n in neighbors:
            r,c = row + n[0], col + n[1]
            if not validate_boundaries(r, c):
                continue
            if data[r][c].color == color_closed:
                reveal_cell(r, c)

def game_over(hasWon):
    if not hasWon:
        for r in range(board_height):
            for c in range(board_width):
                if data[r][c].bomb_count == -1:
                    setCell(r, c, color_bomb, curses.A_REVERSE)

def main(stdscr):
    stdscr.clear()
    init_data()
    for i in range(board_height):
        for j in range(board_width):
            setCell(i, j, data[i][j].color)
        stdscr.addch(i, board_left + board_width*2, color_separator, curses.A_DIM)

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
            if data[current_row][current_col].color in [color_closed, color_hidden_bomb, color_flag]:
                newcolor = color_flag if data[current_row][current_col].color != color_flag else color_closed
                data[current_row][current_col].color = newcolor
                setCell(current_row, current_col, newcolor, curses.A_BLINK)
        elif c == ord(' ') or c == curses.KEY_ENTER:
            if data[current_row][current_col].bomb_count == -1:
                game_over(False)
            else:
                reveal_cell(current_row, current_col)
        elif c == ord('q') or c == ord('Q'):
            break
        moveCurrentCell(newrow, newcol)
        stdscr.refresh()

wrapper(main)
