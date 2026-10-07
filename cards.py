import random

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["C", "D", "H", "S"]


class Deck:
    def __init__(self):
        self.cards = [(rank, suit) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() if self.cards else None


def hand_value(hand):
    value = 0
    aces = 0
    for rank, _ in hand:
        if rank == "A":
            value += 11
            aces += 1
        elif rank in {"J", "Q", "K"}:
            value += 10
        else:
            value += int(rank)

    # Downgrade Aces from 11 to 1 only as needed to avoid busting
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def is_blackjack(hand):
    """A natural: exactly two cards totalling 21 (Ace + 10-value card)."""
    return len(hand) == 2 and hand_value(hand) == 21
