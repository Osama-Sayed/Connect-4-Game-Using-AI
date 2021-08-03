import numpy as np
import pygame
import random 
import sys
import math
from pygame.locals import *
ROW_COUNT = 6
COLUMN_COUNT = 7
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

PLAYER = 0
AI = 1

EMPTY = 0

PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def create_border():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_loacation(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    #check horizontal location for win
    for c in range (COLUMN_COUNT-3):
        for r in  range (ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    #check vertical location for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    #check positively sloped diaganols for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

        # check negatively sloped diaganols for win
        for c in range(COLUMN_COUNT - 3):
            for r in range(3, ROW_COUNT):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                    return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) ==1:
        score+=5
    elif window.count(piece) == 2 and window.count(EMPTY) ==2:
        score+=2 
    if window.count(opp_piece)== 3 and window.count(EMPTY) == 1:
        score -= 4
    return score
def score_position(board, piece):
    score = 0
    #Score Center column
    center_array = [int(i) for i in list(board[:,COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count*3
    #Score Horizontal
    for r in range (ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c: c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)    

    #Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece) 

    #Score positive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range (WINDOW_LENGTH)]
            score += evaluate_window(window, piece) 

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range (WINDOW_LENGTH)]
            score += evaluate_window(window, piece) 
    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_loacation(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_loacation(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_loacation(board):
    vaild_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_loacation(board, col):
            vaild_locations.append(col)
    return vaild_locations


def pick_best_move(board, piece):
    vaild_locations = get_valid_loacation(board)
    best_score = -10000
    best_col = random.choice(vaild_locations)
    for col in vaild_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE ))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE/2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE/2), hight - int(r * SQUARESIZE + SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE/2),hight - int(r * SQUARESIZE + SQUARESIZE/2)), RADIUS)
        pygame.display.update()

def blit_text(surface, text, pos, font, color=(255,255,255)):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

        
board = create_border()

game_over = False

pygame.init()
pygame.display.set_caption('Connect 4 Game')
#a = pygame.image.load('connect.png')
#pygame.display.set_icon(a)

SQUARESIZE = 100
width = SQUARESIZE * COLUMN_COUNT
hight = SQUARESIZE * (ROW_COUNT+1)
size = (width, hight)
RADIUS = int(SQUARESIZE/2 - 5)
screen = pygame.display.set_mode(size)

pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)
click = False
while True:
    screen.fill((0,0,0))
    label = pygame.font.SysFont("monospace", 40).render("Welcome to Connect 4 Game", 1, (255,255,255))
    screen.blit(label, (40,10))
    mx, my = pygame.mouse.get_pos()

    button_1 = pygame.Rect(250, 150, 200, 40)
    button_2 = pygame.Rect(295, 250, 100, 40)


    pygame.draw.rect(screen, (150, 100, 200), button_1)
    pygame.draw.rect(screen, (150, 100, 200), button_2)


    choice1 = pygame.font.SysFont("monospace", 20).render("Start Game", 1, (255,255,255))
    screen.blit(choice1, (290, 160, 200, 50))

    choice2 =pygame.font.SysFont("monospace", 17).render("About", 1, (255,255,255))
    screen.blit(choice2, (320, 260, 200, 50))
    pygame.display.update()
    if button_1.collidepoint((mx, my)):
        if click:
            draw_board(board)
            pygame.display.update()
            while not game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.QUIT()
                        sys.exit()
                    if event.type == pygame.MOUSEMOTION:
                        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                        posx = event.pos[0]
                        if turn%2 == PLAYER:
                            pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                       
                    pygame.display.update()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))            
                        # Ask player 1 input
                        if turn % 2 == PLAYER:
                            posx = event.pos[0]
                            col = int(math.floor(posx/SQUARESIZE))
                                
                            if is_valid_loacation(board, col):
                                row = get_next_open_row(board, col)
                                drop_piece(board, row, col, PLAYER_PIECE)
                                if winning_move(board, PLAYER_PIECE):
                                    label = myfont.render("Player 1 win :)", 1, RED)
                                    screen.blit(label, (40,10))
                                    game_over = True
                                turn += 1
                                print_board(board)
                                draw_board(board)


                if turn %2 == AI and not game_over:
                   #col = random.randint(0, COLUMN_COUNT-1)
                   #col = pick_best_move(board, AI_PIECE)
                   col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
                   pygame.time.wait(500)
                   if is_valid_loacation(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, AI_PIECE)
                    if winning_move(board, AI_PIECE):
                        label = myfont.render("Player 2 win :)", 1, YELLOW)
                        screen.blit(label, (40,10))
                        game_over = True

                    print_board(board)
                    draw_board(board)
                    turn += 1

                if game_over:
                    pygame.time.wait(3000)
                    pygame.quit()
                    sys.exit()
    if button_2.collidepoint((mx, my)):
        if click:
            screen.fill((0,0,0))

            header1= pygame.font.SysFont("monospace", 20).render("Description: ", 1, (255,255,255))
            screen.blit(header1, (40,10))

            font= pygame.font.SysFont("monospace", 20)
            text= "This is a connect4 game with GUI. The game has computer vs. player game mode. The computer player (AI) is implemented using a minimax algorithm, and a set of heuristics to evaluate each move and a given game state. The code will need pygame, numpy, math, random and sys libraries to run."
            blit_text(screen, text,(40,40),font )

            header2= pygame.font.SysFont("monospace", 20).render("How to Play: ", 1, (255,255,255))
            screen.blit(header2, (40,190))

            text="The first Player choose a color and then take turns dropping one colored disc from the top into a seven-column, six-row vertically suspended grid. The pieces fall straight down, occupying the lowest available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs. Connect Four is a solved game. The first player can always win by playing the right moves."
            blit_text(screen, text,(40,210),font )

            Title = pygame.font.SysFont("monospace", 20).render("This Game Is Developed By:- ", 1, (255,255,255))
            screen.blit(Title, (170,440))
            First_Name = pygame.font.SysFont("monospace", 20).render("1-Osama SaYed ", 1, (255,255,255))
            screen.blit(First_Name, (40,470))
            Second_Name = pygame.font.SysFont("monospace", 20).render("2-Kerolos Samy ", 1, (255,255,255))
            screen.blit(Second_Name, (40,490))
            Third_Name = pygame.font.SysFont("monospace", 20).render("3-Marvy Magdy ", 1, (255,255,255))
            screen.blit(Third_Name, (40,510))
            Fourth_Name = pygame.font.SysFont("monospace", 20).render("4-Shahd Hesham ", 1, (255,255,255))
            screen.blit(Fourth_Name, (40,530))
            
            pygame.display.update()
            pygame.time.wait(10000)
            pygame.quit()
            sys.exit()


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True

    pygame.display.update()