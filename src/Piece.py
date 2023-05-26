class Piece:
    def __init__(self, color: str, typ: str):
        self.typ = typ
        self.color = color

    def get_image_name(self):
        return self.color + self.typ

    def is_white(self):
        return self.color == "w"


