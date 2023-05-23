import pygame as p
from Board import Board

WIDTH, HEIGHT = 512, 512
MAX_FPS = 15
class Game:

    run = True

    def __init__(self):
        self.WIN = p.display.set_mode((WIDTH, HEIGHT))
        self.board = Board(WIDTH, self.WIN)
        self.clock = p.time.Clock()

    def main_loop(self):

        while self.run:
            for event in p.event.get():
                if event.type == p.QUIT:
                    self.run = False

            self.clock.tick(MAX_FPS)
            p.display.flip()

        p.quit()
