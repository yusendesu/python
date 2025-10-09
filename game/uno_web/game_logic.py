import random
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional


class CardColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    WILD = "wild"


class CardValue(Enum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    SKIP = "skip"
    REVERSE = "reverse"
    DRAW_TWO = "draw_two"
    WILD = "wild"
    WILD_DRAW_FOUR = "wild_draw_four"


class Card:
    def __init__(self, color: CardColor, value: CardValue):
        self.color = color
        self.value = value
        self.points = self.calculate_points()

    def calculate_points(self) -> int:
        if self.value in [CardValue.SKIP, CardValue.REVERSE, CardValue.DRAW_TWO]:
            return 20
        elif self.value in [CardValue.WILD, CardValue.WILD_DRAW_FOUR]:
            return 50
        else:
            return int(self.value.value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'color': self.color.value,
            'value': self.value.value,
            'points': self.points,
            'image_src': f"images/{self.color.value}{self.get_image_suffix()}.png"
        }

    def get_image_suffix(self) -> str:
        value_map = {
            CardValue.SKIP: "10",
            CardValue.REVERSE: "11",
            CardValue.DRAW_TWO: "12",
            CardValue.WILD: "13",
            CardValue.WILD_DRAW_FOUR: "14"
        }
        return value_map.get(self.value, self.value.value)


class Player:
    def __init__(self, name: str, session_id: str):
        self.name = name
        self.session_id = session_id
        self.hand: List[Card] = []
        self.said_uno = False
        self.score = 0

    def add_card(self, card: Card):
        self.hand.append(card)
        self.said_uno = False

    def remove_card(self, index: int) -> Card:
        return self.hand.pop(index)

    def get_hand_info(self) -> List[Dict[str, Any]]:
        return [card.to_dict() for card in self.hand]


class UNOGame:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: List[Player] = []
        self.deck: List[Card] = []
        self.play_pile: List[Card] = []
        self.discard_pile: List[Card] = []
        self.current_player_index = 0
        self.direction = 1  # 1 for clockwise, -1 for counterclockwise
        self.started = False
        self.current_color = None
        self.initialize_deck()

    def initialize_deck(self):
        """创建完整的UNO牌组"""
        self.deck = []

        # 添加数字牌 (0-9) 和功能牌
        for color in [CardColor.RED, CardColor.GREEN, CardColor.BLUE, CardColor.YELLOW]:
            # 数字牌
            for value in [CardValue.ZERO, CardValue.ONE, CardValue.TWO, CardValue.THREE,
                          CardValue.FOUR, CardValue.FIVE, CardValue.SIX,
                          CardValue.SEVEN, CardValue.EIGHT, CardValue.NINE]:
                if value == CardValue.ZERO:
                    self.deck.append(Card(color, value))
                else:
                    self.deck.append(Card(color, value))
                    self.deck.append(Card(color, value))

            # 功能牌 (每种2张)
            for value in [CardValue.SKIP, CardValue.REVERSE, CardValue.DRAW_TWO]:
                self.deck.append(Card(color, value))
                self.deck.append(Card(color, value))

        # 万能牌 (每种4张)
        for _ in range(4):
            self.deck.append(Card(CardColor.WILD, CardValue.WILD))
            self.deck.append(Card(CardColor.WILD, CardValue.WILD_DRAW_FOUR))

        self.shuffle_deck()

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def add_player(self, name: str, session_id: str) -> Tuple[bool, int]:
        """添加玩家到游戏"""
        if len(self.players) >= 4:
            return False, -1

        player_id = len(self.players)
        self.players.append(Player(name, session_id))
        return True, player_id

    def remove_player(self, name: str):
        """移除玩家"""
        self.players = [p for p in self.players if p.name != name]

    def start_game(self):
        """开始游戏"""
        if len(self.players) < 2:
            return False

        # 给每个玩家发7张牌
        for player in self.players:
            for _ in range(7):
                if self.deck:
                    player.add_card(self.deck.pop())

        # 开始第一张牌
        while self.deck:
            card = self.deck.pop()
            if card.color != CardColor.WILD:
                self.play_pile.append(card)
                self.current_color = card.color
                break

        self.started = True
        self.current_player_index = random.randint(0, len(self.players) - 1)
        return True

    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]

    def next_player(self):
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)

    def can_play_card(self, card: Card, top_card: Card) -> bool:
        """检查是否可以出牌"""
        if card.color == CardColor.WILD:
            return True
        if card.color == self.current_color:
            return True
        if card.value == top_card.value:
            return True
        return False

    def play_card(self, player_name: str, card_index: int, chosen_color: str = None) -> Tuple[bool, str]:
        """玩家出牌"""
        player = next((p for p in self.players if p.name == player_name), None)
        if not player or player != self.get_current_player():
            return False, "不是你的回合"

        if card_index < 0 or card_index >= len(player.hand):
            return False, "无效的卡牌索引"

        card = player.hand[card_index]
        top_card = self.play_pile[-1] if self.play_pile else None

        if not top_card or not self.can_play_card(card, top_card):
            return False, "不能出这张牌"

        # 移除手牌并放到出牌堆
        played_card = player.remove_card(card_index)
        self.play_pile.append(played_card)

        # 处理特殊卡牌效果
        message = self.handle_special_card(played_card, chosen_color)

        # 检查UNO状态
        if len(player.hand) == 1 and not player.said_uno:
            # 没喊UNO，罚抽2张牌
            for _ in range(2):
                if self.deck:
                    player.add_card(self.deck.pop())
            message = "没喊UNO！罚抽2张牌"

        # 轮到下一位玩家
        self.next_player()

        return True, message

    def handle_special_card(self, card: Card, chosen_color: str) -> str:
        """处理特殊卡牌效果"""
        message = ""

        if card.color == CardColor.WILD:
            if chosen_color:
                self.current_color = CardColor(chosen_color)
            else:
                self.current_color = CardColor.RED  # 默认颜色
            message = f"颜色变为{self.current_color.value}"

        elif card.value == CardValue.SKIP:
            self.next_player()
            message = "跳过下一位玩家"

        elif card.value == CardValue.REVERSE:
            self.direction *= -1
            message = "方向反转"

        elif card.value == CardValue.DRAW_TWO:
            next_player = self.players[(self.current_player_index + self.direction) % len(self.players)]
            for _ in range(2):
                if self.deck:
                    next_player.add_card(self.deck.pop())
            self.next_player()  # 跳过被罚抽牌的玩家
            message = f"{next_player.name}抽2张牌"

        elif card.value == CardValue.WILD_DRAW_FOUR:
            next_player = self.players[(self.current_player_index + self.direction) % len(self.players)]
            for _ in range(4):
                if self.deck:
                    next_player.add_card(self.deck.pop())
            self.next_player()
            if chosen_color:
                self.current_color = CardColor(chosen_color)
            message = f"{next_player.name}抽4张牌，颜色变为{self.current_color.value}"

        else:
            self.current_color = card.color

        return message

    def draw_card(self, player_name: str) -> Optional[Card]:
        """玩家抽牌"""
        player = next((p for p in self.players if p.name == player_name), None)
        if not player or player != self.get_current_player():
            return None

        if not self.deck:
            self.reshuffle_discard_pile()

        if self.deck:
            card = self.deck.pop()
            player.add_card(card)
            self.next_player()
            return card

        return None

    def reshuffle_discard_pile(self):
        """重新洗牌弃牌堆"""
        if len(self.play_pile) > 1:
            # 保留最上面的牌
            top_card = self.play_pile.pop()
            self.deck = self.play_pile + self.discard_pile
            self.play_pile = [top_card]
            self.discard_pile = []
            self.shuffle_deck()

    def say_uno(self, player_name: str):
        """玩家喊UNO"""
        player = next((p for p in self.players if p.name == player_name), None)
        if player and len(player.hand) == 1:
            player.said_uno = True

    def check_round_winner(self) -> bool:
        """检查是否有玩家赢得回合"""
        return any(len(player.hand) == 0 for player in self.players)

    def get_round_winner(self) -> str:
        """获取回合胜利者"""
        for player in self.players:
            if len(player.hand) == 0:
                return player.name
        return ""

    def calculate_scores(self):
        """计算回合分数"""
        winner = self.get_round_winner()
        if winner:
            winner_player = next((p for p in self.players if p.name == winner), None)
            if winner_player:
                for player in self.players:
                    if player != winner_player:
                        round_score = sum(card.points for card in player.hand)
                        winner_player.score += round_score

    def start_new_round(self):
        """开始新回合"""
        self.calculate_scores()

        # 重置游戏状态但保留分数
        self.deck = []
        self.play_pile = []
        self.discard_pile = []
        self.initialize_deck()

        # 清空玩家手牌
        for player in self.players:
            player.hand = []
            player.said_uno = False

        # 重新发牌
        for player in self.players:
            for _ in range(7):
                if self.deck:
                    player.add_card(self.deck.pop())

        # 开始第一张牌
        while self.deck:
            card = self.deck.pop()
            if card.color != CardColor.WILD:
                self.play_pile.append(card)
                self.current_color = card.color
                break

        self.current_player_index = random.randint(0, len(self.players) - 1)

    def get_players_info(self) -> List[Dict[str, Any]]:
        return [{
            'name': player.name,
            'hand_count': len(player.hand),
            'score': player.score,
            'said_uno': player.said_uno
        } for player in self.players]

    def get_game_state(self, player_id: int = None) -> Dict[str, Any]:
        """获取游戏状态"""
        state = {
            'players': self.get_players_info(),
            'current_player': self.players[self.current_player_index].name,
            'play_pile_top': self.play_pile[-1].to_dict() if self.play_pile else None,
            'current_color': self.current_color.value if self.current_color else None,
            'deck_count': len(self.deck),
            'direction': self.direction,
            'started': self.started
        }

        # 如果是特定玩家，返回其手牌信息
        if player_id is not None and 0 <= player_id < len(self.players):
            state['your_hand'] = self.players[player_id].get_hand_info()
            state['your_turn'] = (self.players[player_id] == self.get_current_player())

        return state

    def get_scores(self) -> Dict[str, int]:
        return {player.name: player.score for player in self.players}