import os

import numpy as np
import pygame as p

class Board:
    DIMENSION = 8
    square_size = 0

    def __init__(self, size, screen):
        self.screen = screen
        self.square_size = size / self.DIMENSION
        self.moveLog = []
        self.whites_turn = True
        self.images = {}
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        self.load_images()
        self.draw_board()
        self.draw_pieces()

    def load_images(self):
        path = "../res/pieces/"
        for piece in sorted(os.listdir(path)):
            self.images[piece.replace(".png", "")] = p.image.load(path + piece)

    def draw_board(self):
        colors = [p.Color("White"), p.Color("gray")]
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                color = colors[(row+col) % 2]
                p.draw.rect(self.screen, color, p.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size))

    def draw_pieces(self):
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                piece = self.board[row, col]
                if piece != "-":
                    self.screen.blit(self.images[piece], p.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size))



