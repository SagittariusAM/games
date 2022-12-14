from cmath import pi
from shutil import move
from threading import local
from tkinter import W, Y
from traceback import format_exc
from unicodedata import name
from urllib.parse import parse_qsl
from xml.sax import parseString
from xml.sax.saxutils import XMLFilterBase
import pygame
from sys import exit
import itertools
import math

pygame.init()

BOARD = 600
PIECE_SIZE = 60
SQUARE = 75
A1 = 7
A2 = A1+SQUARE
A3 = A2+SQUARE
A4 = A3+SQUARE
A5 = A4+SQUARE
A6 = A5+SQUARE
A7 = A6+SQUARE
A8 = A7+SQUARE

screen = pygame.display.set_mode((BOARD, BOARD))
clock = pygame.time.Clock()

yies = [A1, A2, A3, A4, A5, A6, A7, A8]
xies = yies
ss = [1, -1]

piece_touched = False
WhiteTurn = True
black_in_check = False
white_in_check = False
virtual_position = None

chess_surf = pygame.image.load('graphics/chess.png').convert_alpha()
kingW = pygame.image.load('graphics/kingW.png').convert_alpha()
kingB = pygame.image.load('graphics/kingB.png').convert_alpha() 
queenW = pygame.image.load('graphics/queenW.png').convert_alpha()
queenB = pygame.image.load('graphics/queenB.png').convert_alpha()
bishopW = pygame.image.load('graphics/bishopW.png').convert_alpha()
bishopB = pygame.image.load('graphics/bishopB.png').convert_alpha()
knightW = pygame.image.load('graphics/knightW.png').convert_alpha()
knightB = pygame.image.load('graphics/knightB.png').convert_alpha()
rookW = pygame.image.load('graphics/rookW.png').convert_alpha()
rookB = pygame.image.load('graphics/rookB.png').convert_alpha()
pawnW = pygame.image.load('graphics/pawnW.png').convert_alpha()
pawnB = pygame.image.load('graphics/pawnB.png').convert_alpha()

# dot = pygame.image.load('dot.png').convert_alpha()
# dot_rect = dot.get_rect(topleft)

piecesA = [rookW, knightW, bishopW, kingW, queenW, bishopW, knightW, rookW, pawnW, pawnW, pawnW, pawnW, pawnW, pawnW, pawnW, pawnW]
piecesB = [rookB, knightB, bishopB, kingB, queenB, bishopB, knightB, rookB, pawnB, pawnB, pawnB, pawnB, pawnB, pawnB, pawnB, pawnB]

p_rectA = []
p_rectB = []

moves = []
bad_way = []

x1 = A1
y1 = A8
for rectA in piecesA:
    p_rectA.append(rectA.get_rect(topleft=(x1, y1)))
    x1 += SQUARE
    if x1 == BOARD + A1:
        x1 = A1
        y1 -= SQUARE

x1 = A1
y1 = A1
for rectB in piecesB:
    p_rectB.append(rectB.get_rect(topleft=(x1, y1)))
    x1 += SQUARE
    if x1 == BOARD + A1:
        x1 = A1
        y1 += SQUARE

allpieces = p_rectA + p_rectB
# AllPieces = ["White Rook", "White Knight", "White Bishop", "White King", "White Queen", "White Bishop", "White Knight", "White Rook", "White Pawn", "White Pawn", "White Pawn", "White Pawn", "White Pawn", "White Pawn", "White Pawn", "White Pawn", "Black Rook", "Black Knight", "Black Bishop", "Black King", "Black Queen", "Black Bishop", "Black Knight", "Black Rook", "Black Pawn", "Black Pawn", "Black Pawn", "Black Pawn", "Black Pawn", "Black Pawn", "Black Pawn", "Black Pawn"]
# Return to original position:
# def fuckoff(shit):
#     shit.x = originX
#     shit.y = originY
#     return True

def setting_board(rect_pieces, img_pieces):
    for pA, p_A in itertools.zip_longest(img_pieces, rect_pieces):
        if p_A:
            screen.blit(pA, p_A)

# Positioning piece in center of square:
def checkinXY(zing):
    dx = BOARD
    dy = BOARD
    for x in xies:
        if abs(zing.x - x) <= abs(dx):
            dx = zing.x - x
    global destX
    destX = zing.x - dx
    for y in yies:
        if abs(zing.y - y) <= abs(dy):
            dy = zing.y - y
    global destY
    destY = zing.y - dy

# Checking for pieces on squares:
def checkinCollide(zist):
    if any(piece and list(piece.topleft) == mV for piece in zist) or any(it == way for it in bad_way):
        bad_way.append(way)
        return True
    else:
        pass

# Gobbling:
def checkinEnemy(enemy_zist):
    if not any(it == way for it in bad_way) and (any(piece and list(piece.topleft) == mV for piece in enemy_zist) or virtual_position == mV):
        bad_way.append(way)
        return True
    else:
        pass

def executeOrder(enemy_zist):
    for foe in enemy_zist:
        if foe and foe.topleft == Selected.topleft: 
            i = enemy_zist.index(foe)
            enemy_zist[i] = None

# Execute order (66):
# Show available moves:
def showMoves():
    for move in moves:
        pygame.draw.circle(screen, (100,100,100), (move[0]+30, move[1]+30), 10)

def kingSafety(enemy_zist, zist):
    for foe in enemy_zist:
        if foe:
            global originX
            global originY
            originX = foe.x
            originY = foe.y
            checkinWho(foe, enemy_zist, zist)
            # showMoves()
            # u_moves = []
            # for move in moves:
            #     if move not in u_moves:
            #         u_moves.append(move)
            #         print(list(move))
            originX = PositionA[0]
            originY = PositionA[1]
            if (zist[3] and any(move == list(zist[3].topleft) for move in moves)) or (not zist[3] and any(move == virtual_position for move in moves)):
                print("king in check")
                moves.clear()
                return True
            else:
                moves.clear()

# How the rooks move:
def rookMoves(zist, enemy_zist):
    for pos in range(75, 600, 75):
        for factor1 in ss:
            global mV
            global way
            mV = pygame.math.Vector2((originX + pos*factor1), (originY))
            way = pygame.math.Vector2((pos*factor1), 0)
            way = way.normalize()
            if all(0 <= it <= 600 for it in mV) and (checkinEnemy(enemy_zist) or not checkinCollide(zist)):
                moves.append(mV)
            mV = pygame.math.Vector2((originX), (originY + pos*factor1))
            way = pygame.math.Vector2(0, (pos*factor1))
            way = way.normalize()
            if all(0 <= it <= 600 for it in mV) and (checkinEnemy(enemy_zist) or not checkinCollide(zist)):
                moves.append(mV)
    bad_way.clear()

# How the knights move:
def knightMoves(zist):
    global mV
    for factor1 in ss:
        for factor2 in ss:
            mV = pygame.math.Vector2((originX + SQUARE*factor1*factor2), (originY + SQUARE*2*factor1))
            if all(0 <= it <= BOARD for it in mV) and (not any(piece and piece.topleft == mV for piece in zist) or virtual_position == mV):
                moves.append(mV)
    for factor1 in ss:
        for factor2 in ss:
            mV = pygame.math.Vector2((originX + SQUARE*2*factor1*factor2), (originY + SQUARE*factor1))
            if all(0 <= it <= 600 for it in mV) and (not any(piece and piece.topleft == mV for piece in zist) or virtual_position == mV):
                moves.append(mV)
    bad_way.clear()

# How the bishops move:
def bishopMoves(zist, enemy_zist):
    for pos in range(75, 600, 75):
        for factor1 in ss:
            for factor2 in ss:
                global mV
                global way
                mV = pygame.math.Vector2((originX + pos*factor1*factor2), (originY + pos*factor1))
                way = pygame.math.Vector2((pos*factor1*factor2), (pos*factor1))
                way = way.normalize()
                if all(0 <= it <= 600 for it in mV) and (checkinEnemy(enemy_zist) or not checkinCollide(zist)):
                    moves.append(mV)
    bad_way.clear()

# How the king moves
def kingMoves(zist):
    global mV
    for factor1 in ss:
        for factor2 in ss:
            mV = [originX + SQUARE*factor1*factor2, originY + SQUARE*factor1]
            if all(0 <= it <= 600 for it in mV) and (not any(piece and list(piece.topleft) == mV for piece in zist) or virtual_position == mV):
                moves.append(mV)
        mV = [originX + SQUARE*factor1, originY]
        if all(0 <= it <= 600 for it in mV) and (not any(piece and list(piece.topleft) == mV for piece in zist) or virtual_position == mV):
            moves.append(mV)
        mV = [originX, originY + SQUARE*factor1]
        if all(0 <= it <= 600 for it in mV) and (not any(piece and list(piece.topleft) == mV for piece in zist) or virtual_position == mV):
            moves.append(mV)
    bad_way.clear()

# How the queen moves:
def queenMoves(zist, enemy_zist):
    bishopMoves(zist, enemy_zist)
    rookMoves(zist, enemy_zist)

# How the pawns move:
def pawnMoves(zing, zist, enemy_zist):
    global mV
    s = 1
    place = A2
    if is_white_pawn(zing, zist):
        s = -1
        place = A7
    mV = [originX, originY + SQUARE*s]
    if all(0 <= it <= BOARD for it in mV) and not any(piece and list(piece.topleft) == mV for piece in allpieces) and not virtual_position == mV:
        moves.append(mV)
        mV = [originX, originY + SQUARE*s*2]
        if all(0 <= it <= BOARD for it in mV) and originY == place and not any(piece and list(piece.topleft) == mV for piece in allpieces) and not virtual_position == mV:
            moves.append(mV)
    for factor in ss:
        mV = [originX + SQUARE*s*factor, originY + SQUARE*s]
        if all(0 <= it <= BOARD for it in mV) and any(piece and list(piece.topleft) == mV for piece in enemy_zist) or virtual_position == mV:
            moves.append(mV)
    bad_way.clear()

# Makes next section more readable:
def is_rook(zing, zist):
    if zist.index(zing) == 0 or zist.index(zing) == 7:
        return True
def is_knight(zing, zist):
    if zist.index(zing) == 1 or zist.index(zing) == 6:
        return True
def is_bishop(zing, zist):
    if zist.index(zing) == 2 or zist.index(zing) == 5:
        return True
def is_king(zing, zist):
    if zist.index(zing) == 3:
        return True
def is_queen(zing, zist):
    if zist.index(zing) == 4:
        return True
def is_white_pawn(zing, zist):
    if zist == p_rectA and 8 <= zist.index(zing) <= 15:
        return True
def is_black_pawn(zing, zist):
    if zist == p_rectB and 8 <= zist.index(zing) <= 15:
        return True

# What piece was moved and where can it go:
def checkinWho(zing, zist, enemy_zist):
    global moves
    global virtual_position
    if not virtual_position == zing.topleft: # If you 'kill' piece checking the king
        if is_rook(zing, zist):
            rookMoves(zist, enemy_zist)

        elif is_knight(zing, zist):
            knightMoves(zist)

        elif is_bishop(zing, zist):
            bishopMoves(zist, enemy_zist)

        elif is_king(zing, zist):
            kingMoves(zist)

        elif is_queen(zing, zist):
            queenMoves(zist, enemy_zist)

        elif is_white_pawn(zing, zist) or is_black_pawn(zing, zist):
            pawnMoves(zing, zist, enemy_zist)
    
    if not virtual_position and piece_touched and moves:
        amoves = [x for x in moves]
        o = zist.index(zing)
        zist[o] = None
        for move in amoves:
            virtual_position = move
            moves.clear()
            if kingSafety(enemy_zist, zist):
                amoves[amoves.index(move)] = None
        moves = [x for x in amoves if x != None]
        zist[o] = zing
        virtual_position = None
    return moves

# virtual_pocition is the position a piece would be in if the player were to make the corespondant move.
# The purpose of it is to exclude moves which lead to checks by simulating them, instead of actually moving the piece.

class Pieces:
    # def __init__(self):
    #     self.unmoved = bool
    def moving(rect_pieces, enemy_pieces_rect):
        for sltd in rect_pieces:
            global piece_touched
            if sltd and event.type == pygame.MOUSEBUTTONDOWN and sltd.collidepoint(pygame.mouse.get_pos()) and piece_touched is False:
                global Selected
                global originX
                global originY
                global PositionA
                global PositionZ
                Selected = sltd
                originX = Selected.x
                originY = Selected.y
                PositionA = Selected.topleft
                piece_touched = True
            elif event.type == pygame.MOUSEBUTTONDOWN and moves:
                piece_touched = True
            if piece_touched:
                Selected.center = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONUP or moves:
                    checkinWho(Selected, rect_pieces, enemy_pieces_rect)
                    checkinXY(Selected)
                    PositionZ = [destX, destY]
                    for move in moves:
                        if move == PositionZ and not PositionA == PositionZ:
                            Selected.topleft = PositionZ
                            moves.clear()
                            return True
                    piece_touched = False
                    Selected.topleft = PositionA
                    if not Selected.collidepoint(pygame.mouse.get_pos()): moves.clear()
                    return False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(chess_surf, (0, 0))

    setting_board(p_rectA, piecesA)
    setting_board(p_rectB, piecesB)

    if moves:
        showMoves()

    if black_in_check:
        pygame.draw.rect(screen, (255,0,0), p_rectB[3], 4)

    if white_in_check:
        pygame.draw.rect(screen, (255,0,0), p_rectA[3], 4)

    if WhiteTurn:
        if Pieces.moving(p_rectA, p_rectB):
            executeOrder(p_rectB)
            white_in_check = False
            WhiteTurn = False
            piece_touched = False
            moves.clear()
            print("Black's Turn")
            if kingSafety(p_rectA, p_rectB):
                black_in_check = True

    else:
        if Pieces.moving(p_rectB, p_rectA):
            executeOrder(p_rectA)
            black_in_check = False
            WhiteTurn = True
            piece_touched = False
            moves.clear()
            print("White's Turn")
            if kingSafety(p_rectB, p_rectA):
                white_in_check = True

    pygame.display.update()
    clock.tick(60)
    