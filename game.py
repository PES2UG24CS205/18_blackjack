from cards import Deck, hand_value, is_blackjack

STARTING_CHIPS = 100
MIN_BET = 1
DEALER_STANDS_ON = 17  # dealer draws below 17, stands on all 17s

HIT, STAND, QUIT = {"h", "hit"}, {"s", "stand"}, {"q", "quit"}

# outcome -> (payout multiplier applied to the wager, message)
OUTCOMES = {
    "blackjack":        (1.5, "Blackjack! You win 3:2."),
    "dealer_blackjack": (-1,  "Dealer has blackjack. You lose."),
    "player_bust":      (-1,  "Bust. You lose."),
    "dealer_bust":      (1,   "Dealer busts. You win."),
    "win":              (1,   "You win."),
    "lose":             (-1,  "Dealer wins."),
    "push":             (0,   "Push. Bet returned."),
    "abandoned":        (0,   "Round abandoned. Bet returned."),
    "void":             (0,   "Deck ran out. Round void, bet returned."),
}


class DeckEmpty(Exception):
    """Raised when a card is needed but the deck has none left."""


def fmt(hand):
    return " ".join(f"{r}{s}" for r, s in hand)


def card_str(card):
    return f"{card[0]}{card[1]}"


def ask(prompt):
    """input() that treats Ctrl+D / Ctrl+C as 'quit' instead of crashing."""
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "q"


class Blackjack:
    def __init__(self, chips=STARTING_CHIPS):
        self.chips = chips      # lives on the game object, so it carries across rounds
        self.wager = 0
        self.settled = True     # no round in progress yet

    # ---------- wager ----------
    def ask_wager(self):
        """Ask until a valid wager is entered. Returns the wager, or None to quit.
        Invalid input never touches self.chips."""
        while True:
            raw = ask(f"Chips: {self.chips}. Wager ({MIN_BET}-{self.chips}) or [q]uit: ")
            if raw in QUIT:
                return None
            try:
                amount = int(raw)
            except ValueError:
                print("Invalid wager: enter a whole number. Chips unchanged.")
                continue
            if amount < MIN_BET:
                print(f"Invalid wager: minimum is {MIN_BET}. Chips unchanged.")
            elif amount > self.chips:
                print(f"Invalid wager: you only have {self.chips}. Chips unchanged.")
            else:
                print(f"Bet placed: {amount}.")
                return amount

    # ---------- settlement ----------
    def settle(self, outcome):
        """The only place chips change. Guarded so a round can settle exactly once."""
        if self.settled:
            raise RuntimeError("Round already settled")
        multiplier, message = OUTCOMES[outcome]
        change = int(self.wager * multiplier)  # 3:2 rounds down on odd wagers
        self.chips += change
        self.settled = True
        sign = "+" if change > 0 else ""
        print(f"{message} ({sign}{change}) Chips: {self.chips}")

    # ---------- cards ----------
    @staticmethod
    def draw(deck):
        card = deck.draw()
        if card is None:
            raise DeckEmpty
        return card

    def show(self, player, dealer, hide=True):
        if hide:
            print(f"Dealer: {card_str(dealer[0])} ??")
        else:
            print("Dealer:", fmt(dealer), "=", hand_value(dealer))
        print("Player:", fmt(player), "=", hand_value(player))

    # ---------- one round ----------
    def round(self):
        """Returns False if the player chose to quit, True otherwise."""
        wager = self.ask_wager()
        if wager is None:
            return False
        self.wager = wager
        self.settled = False
        try:
            return self.play_hand(Deck())
        except DeckEmpty:
            self.settle("void")
            return True

    def play_hand(self, deck):
        player, dealer = [], []
        for _ in range(2):  # deal alternately: player, dealer, player, dealer
            player.append(self.draw(deck))
            dealer.append(self.draw(deck))
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
            key = ask("[h]it [s]tand [q]uit: ")
            if key in QUIT:
                self.settle("abandoned")
                return False
            if key in STAND:
                print(f"You stand on {hand_value(player)}.")
                break
            if key in HIT:
                card = self.draw(deck)
                player.append(card)
                print(f"You draw {card_str(card)} -> {hand_value(player)}")
            else:
                print("Invalid command: use h, s or q.")
        else:
            if hand_value(player) == 21:
                print("21! Standing automatically.")

        if hand_value(player) > 21:
            self.show(player, dealer, hide=False)
            self.settle("player_bust")
            return True  # dealer does not play

        # 3. Dealer turn
        print(f"Dealer reveals {card_str(dealer[1])}.")
        self.show(player, dealer, hide=False)
        while hand_value(dealer) < DEALER_STANDS_ON:
            card = self.draw(deck)
            dealer.append(card)
            print(f"Dealer draws {card_str(card)} -> {hand_value(dealer)}")
        if hand_value(dealer) <= 21:
            print(f"Dealer stands on {hand_value(dealer)}.")

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

    # ---------- game loop ----------
    def play_again(self):
        while True:
            answer = ask("Play again? [y/n]: ")
            if answer in {"y", "yes"}:
                return True
            if answer in {"n", "no", "q", "quit"}:
                return False
            print("Please answer y or n.")

    def run(self):
        print("Blackjack — starting chips:", self.chips)
        while self.chips >= MIN_BET:
            if not self.round():
                break
            if self.chips < MIN_BET:
                print("Out of chips. Game over.")
                break
            if not self.play_again():
                break
        print("Final chips:", self.chips)
