

level_maps = {
    1: [
        '111111...............11111',
        '1....1...............11..1',
        '1....1...............11..1',
        '1.K..1...........111111DD1',
        '1....1...................1',
        '1....1...................1',
        '11..11...................1',
        '11..11...................1',
        '11..11...................1',
        '11..11............1111...1',
        '11................1111...1',
        '11................1111...1',
        '..................1111...1',
        '.........................1',
        '.....1....1..............1',
        '.....1....1..............1',
        '.....1.11.1..11........111',
        '.....1.11.1..11........111',
        '.....1....1...........1111',
        '.....1....1..........11111',
        '11111111111111111111111111'

    ],
    2: [
        '111111..................11',
        '11111...................11',
        '11..1...................11',
        '11..1...1111111.........11',
        '11DD1..............11...11',
        '..................111....1',
        '..................111....1',
        '...................11....1',
        '...........11............1',
        '...........1111..........1',
        '11111......11111.........1',
        '1..........11111.........1',
        '1........................1',
        '111......................1',
        '111..1.............11...11',
        '111..1.11111.......1.....1',
        '11111111111111.....1..K..1',
        '.................111.....1',
        '.................111.....1',
        '.................111111111',
        '11111111111111111111111111'
    ],
    3: [
        '11.......11111111...111111',
        '11.......11111111...11...1',
        '11.......111..111...11...1',
        '....111..111..111...111..1',
        '...111...111DD111...111..1',
        '...111...................1',
        '.........................1',
        '...............1111......1',
        '11...111.......11111.....1',
        '11..1111.......11111....1',
        '11..1111.................1',
        '11.......................1',
        '11.......................1',
        '11.......................1',
        '11..111.......1....1....11',
        '11.....111....1....1....11',
        '11.......1....1..K.1...111',
        '111......1....1.11.1111111',
        '11111....1....1....1111111',
        '11111....1....1....1111111',
        '11111111111111111111111111',
    ],
}


class Map:
    def __init__(self, game, level_map):
        self.game = game
        self.level_map = level_map

    def draw(self, surface):
        pass
