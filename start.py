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
color_separator = '.'
color_closed = curses.ACS_CKBOARD
color_empty = ' '
color_bomb = 'X'
color_flag = 'F'

# states:
state_playing = 0
state_finished = 1
game_state = state_playing

# params
board_width = 30
board_height = 30
board_top = 0
board_left = 0
difficulty = 0.1

# data
data = []

current_row = current_col = 0
neighbors = [[0,1], [0,-1], [1,0], [-1,0], [-1,-1], [1,1], [1,-1], [-1,1]]

playing_commands = "Move: arrow keys  -  Flag: 'F'  -  Open: space  -  Quit: 'Q'"
finised_commands = "Quit: 'Q'  -  Restart: 'R'"

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
    global data

    # build 2D matrix
    data = []
    num_bombs = board_width * board_height * difficulty
    for i in range(board_height):
        row = []
        for j in range(board_width):
            row.append(cell(color_closed, 0))
        data.append(row)
    # add bombs
    while num_bombs:
        brow, bcol = random.randrange(0, board_height), random.randrange(0, board_width)
        if data[brow][bcol].bomb_count == -1 or count_surrounding_bombs(brow, bcol)[1]:
            continue
        data[brow][bcol].bomb_count = -1
        num_bombs -= 1
        declare_bomb(brow, bcol)

def init_board():
    global game_state

    stdscr.clear()
    init_data()
    for i in range(board_height):
        for j in range(board_width):
            setCell(i, j, data[i][j].color)
        stdscr.addch(i, board_left + board_width*2, color_separator, curses.A_DIM)
    moveCurrentCell(0, 0)
    game_state = state_playing
    log(playing_commands)

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
    setCell(current_row, current_col, val)
    if newval == color_empty:
        newval = '-'
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

def log(s):
    log_row = board_top * 2 + board_height
    stdscr.addstr(log_row,0,len(playing_commands) * " ")
    stdscr.addstr(log_row,0,s)

def main(stdscr):
    global current_row, current_col, game_state
    init_board()

    while 1:
        newrow, newcol = current_row, current_col
        c = stdscr.getch()
        while game_state == state_finished and c not in [ord('r'), ord('R'), ord('q'), ord('Q')]:
            c = stdscr.getch()

        if c == curses.KEY_RIGHT:
            newrow, newcol = current_row, current_col + 1
        elif c == curses.KEY_LEFT:
            newrow, newcol = current_row, current_col - 1
        elif c == curses.KEY_UP:
            newrow, newcol = current_row - 1, current_col
        elif c == curses.KEY_DOWN:
            newrow, newcol = current_row + 1, current_col
        elif c == ord('f') or c == ord('F'):
            if data[current_row][current_col].color in [color_closed, color_flag]:
                newcolor = color_flag if data[current_row][current_col].color != color_flag else color_closed
                data[current_row][current_col].color = newcolor
                setCell(current_row, current_col, newcolor, curses.A_BLINK)
        elif c == ord(' ') or c == curses.KEY_ENTER:
            if data[current_row][current_col].bomb_count == -1:
                game_over(False)
                game_state = state_finished
                log(finised_commands)
            else:
                reveal_cell(current_row, current_col)
        elif c == ord('q') or c == ord('Q'):
            break
        elif c in [ord('r'), ord('R')]:
            init_board()
        if game_state == state_playing:
            moveCurrentCell(newrow, newcol)

wrapper(main)
