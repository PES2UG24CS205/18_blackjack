from cards import Deck, hand_value, is_blackjack

BET = 10
DEALER_STANDS_ON = 17  # dealer draws below 17, stands on all 17s

# outcome -> (chip change, message)
OUTCOMES = {
    "blackjack":        (BET * 3 // 2, "Blackjack! You win 3:2."),
    "dealer_blackjack": (-BET,         "Dealer has blackjack. You lose."),
    "player_bust":      (-BET,         "Bust. You lose."),
    "dealer_bust":      (BET,          "Dealer busts. You win."),
    "win":              (BET,          "You win."),
    "lose":             (-BET,         "Dealer wins."),
    "push":             (0,            "Push. Bet returned."),
}


def fmt(hand):
    return " ".join(f"{r}{s}" for r, s in hand)


class Blackjack:
    def __init__(self):
        self.chips = 100

    def show(self, player, dealer, hide=True):
        if hide:
            up_rank, up_suit = dealer[0]
            print(f"Dealer: {up_rank}{up_suit} ??")
        else:
            print("Dealer:", fmt(dealer), "=", hand_value(dealer))
        print("Player:", fmt(player), "=", hand_value(player))

    def settle(self, outcome):
        """The only place chips change. Every round path calls this once, then returns."""
        change, message = OUTCOMES[outcome]
        self.chips += change
        print(f"{message} Chips: {self.chips}")

    def round(self):
        deck = Deck()
        player, dealer = [], []
        for _ in range(2):  # deal alternately: player, dealer, player, dealer
            player.append(deck.draw())
            dealer.append(deck.draw())
        self.show(player, dealer)

        # 1. Naturals end the round immediately
        player_bj, dealer_bj = is_blackjack(player), is_blackjack(dealer)
        if player_bj or dealer_bj:
            self.show(player, dealer, hide=False)
            if player_bj and dealer_bj:
                self.settle("push")
            elif player_bj:
                self.settle("blackjack")
            else:
                self.settle("dealer_blackjack")
            return True

        # 2. Player turn (auto-stops at 21; no more input once bust)
        while hand_value(player) < 21:
            key = input("[h]it [s]tand [q]uit: ").strip().lower()
            if key == "q":
                print("Round abandoned. No chips changed.")
                return False
            elif key == "s":
                break
            elif key == "h":
                card = deck.draw()
                player.append(card)
                print(f"You draw {card[0]}{card[1]}.")
                self.show(player, dealer)
            else:
                print("Invalid command. Use h, s or q.")

        if hand_value(player) > 21:
            self.show(player, dealer, hide=False)
            self.settle("player_bust")
            return True  # dealer does not play

        # 3. Dealer turn
        self.show(player, dealer, hide=False)
        while hand_value(dealer) < DEALER_STANDS_ON:
            card = deck.draw()
            dealer.append(card)
            print(f"Dealer draws {card[0]}{card[1]} -> {hand_value(dealer)}")

        # 4. Compare
        pv, dv = hand_value(player), hand_value(dealer)
        if dv > 21:
            self.settle("dealer_bust")
        elif pv > dv:
            self.settle("win")
        elif pv < dv:
            self.settle("lose")
        else:
            self.settle("push")
        return True

    def run(self):
        print("Blackjack — starting chips:", self.chips)
        while self.chips > 0:
            if not self.round():
                return
            if self.chips <= 0:
                print("Out of chips. Game over.")
                return
            if input("Play again? [y/n]: ").strip().lower() != "y":
                return
