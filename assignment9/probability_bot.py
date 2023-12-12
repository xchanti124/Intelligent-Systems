"""
ProbabilityRandBot -- A bot that applies a very simple probabilistic strategy whenever it is our
turn to play the first card.

At each move in the first phase, the probability is calculated that the opponent has a card in his/her hand
which is in the same color as our options, but higher. This could be considered an easy win for
our opponent, and should be avoided. This means we want to play a card with the highest probability that
there is no higher card of the same color in the opponents hand.

In the second phase we simply play random

"""


import random
from typing import Optional
from schnapsen.bots import RandBot
from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase,
)


class ProbabilityBot(Bot):
    "For Phase 1 of the game"

    def __init__(
        self, rand: random.Random, name: Optional[str] = "ProbabilityBot"
    ) -> None:
        super().__init__(name)
        self.rng = rand

    def get_move(
        self,
        perspective: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        """
        Use probability to choose a move.

        Args:
            perspective: An object representing the perspective of the player.
            leader_move: The move of the leader. If this is None, we are the leader.

        Returns:
            A Move object
        """
        # get all valid moves
        valid_moves = perspective.valid_moves()
        if leader_move is not None:
            # we are the follower, we play randomly.
            return self.rng.choice(valid_moves)

        else:
            # get the initial deck of cards:
            initial_deck = perspective.get_engine().deck_generator.get_initial_deck()

            # Get all the cards that the player has seen so far.
            seen_cards = perspective.seen_cards(leader_move=None)

            # Get all the un-seen cards
            unseen_cards = [card for card in initial_deck if card not in seen_cards]

            # sanity checK
            assert len(unseen_cards) == len(initial_deck) - len(seen_cards)

            # Below two variables will change while we loop over the valid moves.
            chosen_move = None
            max_probability = 0

            # Now we are looking for the problematic cards (dangerous_cards), i.e.
            # those cards that would be easy wins for the opponent, i.e. cards
            # that have the same color as the one played, but with a higher value.
            for move in valid_moves:
                # we don't consider trump exchange nor marriage here.
                if move.is_trump_exchange() or move.is_marriage():
                    continue
                if chosen_move is None:
                    chosen_move = move

                dangerous_cards = []
                for card in unseen_cards:
                    if (card.suit == move.card.suit) and (
                        perspective.get_engine().trick_scorer.SCORES[card.rank]
                        > perspective.get_engine().trick_scorer.SCORES[move.card.rank]
                    ):
                        dangerous_cards.append(card)

                u = num_unseen_cards = len(unseen_cards)  # refer to this as u
                d = num_dangerous_cards = len(dangerous_cards)  # refer to this as d

                # Calculate the probability that the opponent does not have a dangerous
                # The opponent has 5 cards in his/her hand, and we want to calculate the
                # probability that none of these cards are in the dangerous_cards list.
                # This is the product of the five conditional probabilities:
                # P(opponent does not have a dangerous) =
                #   P(1st card is not a dangerous card) *
                #   P(2nd card is not a dangerous card) *
                #   P(3rd card is not a dangerous card) *
                #   P(4th card is not a dangerous card) *
                #   P(5th card is not a dangerous card) =

                # We want to avoid the denominators to be 0, so we check for that.
                if u == 0 or u - 1 == 0 or u - 2 == 0 or u - 3 == 0 or u - 4 == 0:
                    probability = 0

                else:
                    probability = (
                        (u - d)
                        / u
                        * (u - d - 1)
                        / (u - 1)
                        * (u - d - 2)
                        / (u - 2)
                        * (u - d - 3)
                        / (u - 3)
                        * (u - d - 4)
                        / (u - 4)
                    )
                # All that is left to do is to check whether the new probability is
                # higher than the earlier value (to calculate the maximum).
                # If it is, we set probability to be the new maximal probability, and the
                # current move our new chosen move.
                if probability > max_probability:
                    max_probability = probability
                    chosen_move = move

            return chosen_move


class ProbabilityRandBot(Bot):
    """
    This is a two-stage bot. In the first stage, it applies a simple probabilistic
    strategy. In the second stage, it plays random.

    Args:
        perspective: An object representing the perspective of the player.
        leader_move: The move of the leader. If this is None, we are the leader.

    Returns:
        A Move object
    """

    def __init__(
        self, rand: random.Random, name: Optional[str] = "ProbabilityRandBot"
    ) -> None:
        super().__init__(name)
        self.rng = rand
        self.bot_phase1: Bot = ProbabilityBot(rand=self.rng, name="ProbabilityBot")
        self.bot_phase2: Bot = RandBot(rand=self.rng, name="Phase2RandBot")

    def get_move(
        self, perspective: PlayerPerspective, leader_move: Optional[Move]
    ) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(perspective, leader_move)
        else:
            raise AssertionError("Phase ain't right.")
