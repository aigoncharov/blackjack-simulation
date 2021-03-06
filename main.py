import random
import math
import matplotlib.pyplot as plt
import json

ITERATIONS = 10000

#  "Answer to the Ultimate Question of Life, the Universe, and Everything"
# Should be a decent seed, don't you think?
RANDOM_SEED = 42

HOUSE_DEAL_MIN_THRESHOLD = 17

BLACKJACK = 21

# Premium bet multiplier paid when player has a blackjack
BLACKJACK_REWARD_MULTIPLIER = 1.5

BET = 1

CARD_SUITS = ('spades', 'hearts', 'clubs', 'diamonds')
CARD_RANKS = ('ace', 'king', 'queen', 'jack', 10, 9, 8, 7, 6, 5, 4, 3, 2)

STANDARD_DECK = []
for suit in CARD_SUITS:
    for rank in CARD_RANKS:
        STANDARD_DECK.append({'suit': suit, 'rank': rank})

# Many casinos shuffle in several decks at once. Might be useful, if we think of simulating card counting in the future.
DECKS_CNT = 6

# Thresholds of what is considered a good/fair/poor upcard in a dealer's hand
GOOD_UPCARD_THRESHOLD = 7
POOR_UPCARD_THRESHOLD = 4

# Thresholds defining how many points we need to have depending on the dealer's upcard type
UPCARD_THRESHOLDS_LIST = [
    {
        'good': 16,
        'fair': 11,
        'poor': 10
    },
    {
        'good': 17,
        'fair': 11,
        'poor': 10
    },
    {
        'good': 18,
        'fair': 11,
        'poor': 10
    },
    {
        'good': 19,
        'fair': 11,
        'poor': 10
    },
    {
        'good': 16,
        'fair': 12,
        'poor': 11
    },
    {
        'good': 17,
        'fair': 12,
        'poor': 11
    },
    {
        'good': 18,
        'fair': 12,
        'poor': 11
    },
    {
        'good': 19,
        'fair': 12,
        'poor': 11
    },
    {
        'good': 16,
        'fair': 13,
        'poor': 12
    },
    {
        'good': 17,
        'fair': 13,
        'poor': 12
    },
    {
        'good': 18,
        'fair': 13,
        'poor': 12
    },
    {
        'good': 19,
        'fair': 13,
        'poor': 12
    },
    {
        'good': 16,
        'fair': 14,
        'poor': 13
    },
    {
        'good': 17,
        'fair': 14,
        'poor': 13
    },
    {
        'good': 18,
        'fair': 14,
        'poor': 13
    },
    {
        'good': 19,
        'fair': 14,
        'poor': 13
    },
]


def get_points_for_card(card):
    if card['rank'] == 'ace':
        return (1, 11)
    if isinstance(card['rank'], int):
        return (card['rank'],)
    return (10,)


class Hand:
    def __init__(self):
        self.hand = []
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

    def get_max_points(self):
        for points in reversed(self.points):
            if (points > BLACKJACK):
                continue
            return points

        return BLACKJACK + 1

    def has_points(self, points_target):
        return points_target in self.points

    def __getitem__(self, key):
        return self.hand[key]


class Player:
    def __init__(self):
        self.hand = Hand()
        self.bet = BET

    def get_initial_cards(self, cards):
        for card in cards:
            self.hand.add_card(card)

    def hit(self, card):
        self.hand.add_card(card)

    def double(self, card):
        self.hand.add_card(card)
        self.bet += self.bet


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
        while (self.hand.get_max_points() < HOUSE_DEAL_MIN_THRESHOLD):
            card = self.__deck.pop()
            self.hand.add_card(card)

    def __shuffle(self):
        random.shuffle(self.__deck)


class BasicStrategy:
    def __init__(self, house, player, upcard_thresholds):
        self.house = house
        self.player = player
        self.upcard_thresholds = upcard_thresholds

    def run(self):
        # Deal initial hands
        player_cards = self.house.deal_initial_cards()
        self.player.get_initial_cards(player_cards)

        # Watch out for a blackjack
        if (self.player.hand.get_max_points() == BLACKJACK):
            if (self.house.hand.get_max_points() == BLACKJACK):
                return 0

            return self.player.bet * BLACKJACK_REWARD_MULTIPLIER

        house_upcard_type = self.__get_house_upcard_type()
        player_points_threshold = self.upcard_thresholds[house_upcard_type]

        # Hit player until they met their threshold
        while (self.player.hand.get_max_points() < player_points_threshold):
            card = self.house.hit_player()

            if (self.__should_double_down()):
                self.player.double(card)
            else:
                self.player.hit(card)

        # Complete house's hand until it meets a threshold
        self.house.complete_hand()

        # Define winner and return the outcome of the game
        if (self.player.hand.get_max_points() > BLACKJACK):
            if (self.house.hand.get_max_points() > BLACKJACK):
                return 0
            return -self.player.bet

        if (self.house.hand.get_max_points() > BLACKJACK):
            return self.player.bet

        if (self.player.hand.get_max_points() > self.house.hand.get_max_points()):
            return self.player.bet
        else:
            return -self.player.bet

    def __get_house_upcard_type(self):
        points = get_points_for_card(self.house.hand[0])
        max_points = points[-1]

        if max_points >= GOOD_UPCARD_THRESHOLD:
            return 'good'

        if max_points >= POOR_UPCARD_THRESHOLD:
            return 'poor'

        return 'fair'

    def __should_double_down(self):
        return self.player.hand.get_max_points() == 11 or (self.player.hand.get_max_points() == 10 and self.house.hand.get_max_points() < 10) or (self.player.hand.get_max_points() == 9 and self.house.hand.get_max_points() < 6)


class Simulation:
    def __init__(self, iterations, upcard_thresholds):
        self.iterations = iterations
        self.upcard_thresholds = upcard_thresholds
        self.running_total = []
        self.total = 0

    def simulate(self):
        for i in range(self.iterations):
            game_result = self.__simulate_one_game(i)

            running_total = self.running_total[-1] if len(
                self.running_total) > 0 else 0
            self.running_total.append(running_total + game_result)
            self.total += game_result

    def __simulate_one_game(self, i):
        house = House(STANDARD_DECK)
        player = Player()

        basicStrategy = BasicStrategy(house, player, self.upcard_thresholds)

        return basicStrategy.run()


def main():
    print('Starting blackjack simulation')

    random.seed(RANDOM_SEED)  # This helps reproducing the results

    upcard_thresholds_list = UPCARD_THRESHOLDS_LIST
    upcard_thresholds_results = []

    print('Simulating for the list of dealer upcard thresholds: {}'.format(
        upcard_thresholds_list))

    max_total = -math.inf
    max_total_thresholds = None

    for upcard_thresholds in upcard_thresholds_list:
        print('Simulating {} times for the thresholds: {}'.format(ITERATIONS,
                                                                  upcard_thresholds))

        simulation = Simulation(ITERATIONS, upcard_thresholds)

        simulation.simulate()

        upcard_thresholds_results.append({
            'total': simulation.total,
            'running_total': simulation.running_total
        })

        print('Player\'s total expected return is {}. Average return per game is {:.2f}'.format(
            simulation.total, simulation.total / ITERATIONS))

        if simulation.total > max_total:
            max_total = simulation.total
            max_total_thresholds = upcard_thresholds

    print('The best player\'s return ({} total, {:.2f} average per game) is observed with the thresholds {}'.format(
        max_total, max_total / ITERATIONS, max_total_thresholds))

    print('Printing results')

    fig1, ax1 = plt.subplots(figsize=(16, 12))

    for i, upcard_thresholds_result in enumerate(upcard_thresholds_results):
        ax1.plot([iteration + 1 for iteration in range(ITERATIONS)],
                 upcard_thresholds_result['running_total'], label=json.dumps(upcard_thresholds_list[i]))

    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Total return')
    ax1.set_title("Blackjack simulated total return")

    ax1.legend()

    fig1.savefig('blackjack_simulated_total_return.png')
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(16, 12))

    for i, upcard_thresholds_result in enumerate(upcard_thresholds_results):
        ax2.plot([iteration + 1 for iteration in range(ITERATIONS)],
                 [item / (i + 1) for i, item in enumerate(upcard_thresholds_result['running_total'])], label=json.dumps(upcard_thresholds_list[i]))

    ax2.set_xlabel('Iteration')
    ax2.set_ylabel('Average return per game')
    ax2.set_title("Blackjack simulated average return per game")

    ax2.legend()

    # Limit Y axis to increase readability
    ax2.set_ylim([-0.5, 0.5])

    fig2.savefig('blackjack_simulated_avg_return_per_game.png')
    plt.close(fig2)

    print('Blackjack simulation is complete!')


main()
