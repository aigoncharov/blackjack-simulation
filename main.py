import random

SIMULATIONS_CNT = 1

#  "Answer to the Ultimate Question of Life, the Universe, and Everything"
# SHould be a decent seed, don't you think?
RANDOM_SEED = 42

HOUSE_DEAL_MIN_THRESHOLD = 17

BLACKJACK = 21

BET = 1

CARD_SUITS = ('spades', 'hearts', 'clubs', 'diamonds')
CARD_RANKS = ('ace', 'king', 'queen', 'jack', 10, 9, 8, 7, 6, 5, 4, 3, 2)

STANDARD_DECK = []
for suit in CARD_SUITS:
    for rank in CARD_RANKS:
        STANDARD_DECK.append({'suit': suit, 'rank': rank})

DECKS_CNT = 6


def get_points_for_card(card):
    if card['rank'] == 'ace':
        return (1, 11)
    if isinstance(card['rank'], int):
        return (card['rank'],)
    return (10,)


class Hand:
    def __init__(self):
        self.hand = None
        self.points = [0]

    def add_card(self, card):
        self.hand.append(card)
        card_points = get_points_for_card(card)

        new_hand_points = []
        for new_card_points in card_points:
            for current_hand_points in self.points:
                new_hand_points.append(new_card_points + current_hand_points)
        self.points = new_hand_points

        self.points.sort()


class Player:
    def __init__(self):
        self.hand = Hand()
        self.bet = BET

    def get_initial_cards(self, cards):
        for card in cards:
            self.hand.add_card(card)

    def hit(self, card):
        self.hand.add_card(card)

    def stand(self):
        pass

    def double(self, card):
        self.hand.add_card(card)
        self.bet += self.bet

    def surrender(self):
        self.bet /= 2


class House:
    def __init__(self, deck):
        self.__deck = deck.copy()
        self.hand = Hand()

        self.__shuffle()

    def deal_initial_cards(self):
        house_first_card = self.__deck.pop()
        player_first_card = self.__deck.pop()
        house_second_card = self.__deck.pop()
        player_second_card = self.__deck.pop()

        self.hand.add_card(house_first_card)
        self.hand.add_card(house_second_card)

        return (player_first_card, player_second_card)

    def hit_player(self):
        card = self.__deck.pop()
        return card

    def complete_hand(self):
        max_points = self.hand.points[-1]

        while (max_points < HOUSE_DEAL_MIN_THRESHOLD):
            card = self.__deck.pop()
            self.hand.add_card(card)

    def __shuffle(self):
        random.shuffle(self.__deck)


def simulate(i):
    # Setup and start the simulation
    print('Blackjack -> iteration #{}'.format(i))
    print('Using {} decks'.format(DECKS_CNT))

    house = House()


random.seed(RANDOM_SEED)  # This helps reproducing the results

for i in range(SIMULATIONS_CNT):
    simulate(i)
