import requests
from env import API

EMPTY_SLOT = "—"

class Game:
    def __init__(self):
        print("\nWelcome to Minesweeper!\n")

        self.game_over = False
        try:
            self.width = int(input("Board width: "))
            self.height = int(input("Board height: "))
            self.mines = int(input("Number of mines: "))
        except ValueError:
            print("\nInvalid input")
            return self.__init__()
        self.empty_slots = self.width * self.height
        if self.mines >= self.empty_slots or self.mines == 0:
            print("\nInvalid number of mines")
            return self.__init__()
        self.mine_found = False
        self.board_id = self.get_board_id()
        self.board = self.init_board()
        self.print_board()

    def get_board_id(self):
        res = requests.post(
            "{}/init".format(API),
            json={"width": self.width, "height": self.height, "mines": self.mines},
        )

        return res.json().get("boardId")

    def init_board(self):
        board = []
        for h in range(self.height):
            row = []
            for w in range(self.width):
                row.append(EMPTY_SLOT)
            board.append(row)

        return board

    def handle_reveal(self, data):
        self.construct_board(data)

        if self.mine_found:
            print("\nBOOM!")
            self.end()
        if self.empty_slots == self.mines:
            print("\nYou win!")
            self.end()

    def construct_board(self, data):
        self.empty_slots -= len(data)
        for slot in data:
            if slot["isMine"]:
                self.mine_found = True
                self.board[slot["y"]][slot["x"]] = "*"
            else:
                self.board[slot["y"]][slot["x"]] = slot["count"]

        self.print_board()

    def print_board(self):
        print("")
        for w in range(self.width):
            if w == 0:
                print("  0", end=" ")
            else:
                print(w, end=" ")
        print("")
        for index, row in enumerate(self.board):
            print(index, *row)

    def reveal(self):
        try:
            x = int(input("x: "))
            y = int(input("y: "))
        except ValueError:
            print("Invalid coordinates\n")
            return self.reveal()

        if x > self.width - 1 or y > self.height - 1:
            print("\nInvalid coordinates")
            self.print_board()
            return self.reveal()
        if self.board[y][x] != EMPTY_SLOT:
            print("\nThis slot has already been revealed")
            self.print_board()
            return self.reveal()

        res = requests.post(
            "{}/reveal".format(API),
            json={"x": x, "y": y, "boardId": self.board_id},
        )
        data = res.json().get("data")
        self.handle_reveal(data)

    def reveal_all(self):
        res = requests.post(
            "{}/reveal-all".format(API),
            json={"boardId": self.board_id},
        )
        data = res.json().get("data")
        self.construct_board(data)

    def play(self):
        while not self.game_over:
            self.reveal()

    def end(self):
        self.reveal_all()
        self.game_over = True


def main():
    play_again = ""
    game = Game()
    game.play()
    if game.game_over:
        while play_again not in ["yes", "no"]:
            play_again = input("\nWould you like to play again?: [YES/NO] ").lower()

    if play_again == "yes":
        main()
    else:
        print("\nThanks for playing!")


main()
