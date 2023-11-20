from typing import Optional, List
from schnapsen.game import Bot, PlayerPerspective, Move


class MyBot(Bot):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.from_front = True

    def get_move(
        self,
        perspective: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        available_moves: List[Move] = perspective.valid_moves()

        if self.from_front:
            naive_move = available_moves[0]
        else:
            naive_move = available_moves[-1]

        self.from_front = not self.from_front

        return naive_move
