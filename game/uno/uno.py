import random
from enum import Enum
from typing import List, Optional

class CardColor(Enum):
    RED = "红"
    YELLOW = "黄"
    GREEN = "绿"
    BLUE = "蓝"
    WILD = "万能"

class CardType(Enum):
    NUMBER = "数字"
    SKIP = "跳过"
    REVERSE = "反转"
    DRAW_TWO = "+2"
    WILD = "变色"
    WILD_DRAW_FOUR = "+4"

class Card:
    def __init__(self,color:CardColor,card_type:CardType,number:Optional[int]=None):
        self.color = color
        self.type = card_type
        self.number = number

    def __str__(self):
        if self.type == CardType.NUMBER:
            return f"{self.color.value}{self.number}"
        elif self.type == CardType.WILD or self.type == CardType.WILD_DRAW_FOUR:
            return f"{self.type.value}"
        else:
            return f"{self.color.value}{self.type.value}"

    def __repr__(self):
        return self.__str__()

    def can_play_on(self,other:"Card")->bool:
        if self.color == CardColor.WILD:
            return True
        if self.color == other.color:
            return True
        if self.type == other.type and self.type != CardType.NUMBER:
            return True
        if self.type == CardType.NUMBER == other.type and self.number == other.number:
            return True
        return False

class Player:
    def __init__(self,name:str):
        self.name = name
        self.hand:List[Card] = []

    def draw_card(self,card:Card):
        self.hand.append(card)

    def play_card(self, card_index:int)->Card:
        return self.hand.pop(card_index)

    def has_playable_card(self,top_card:Card)->bool:
        return any(card.can_play_on(top_card) for card in self.hand)

    def __str__(self):
        return f"{self.name} ({len(self.hand)}张牌)"

class UNOGame:
    def __init__(self,player_names:list[str]):
        self.players = [Player(name) for name in player_names]
        self.deck = self.create_deck()
        self.discard_pile:List[Card] = []
        self.current_player_index = 0
        self.direction = 1 # 1表示顺时针,-1表示逆时针。
        self.game_over = False
        self.current_color = None

        self.setup_game()

    def creat_deck(self)->list[Card]:
        deck = []
        # 创建数字牌（除0外，每一种颜色的数字都有两张）
        for color in [CardColor.RED, CardColor.YELLOW, CardColor.GREEN, CardColor.BLUE]:
            # 创建数字0的卡牌
            deck.aappend(Card(color, CardType.NUMBER, 0))
            # 创建数字1~9
            for _ in range(2):
                for number in range(1, 10):
                    deck.append(Card(color, CardType.NUMBER, number))
            # 创建功能牌
            for _ in range(2):
                deck.append(Card(color, CardType.SKIP))
                deck.append(Card(color, CardType.REVERSE))
                deck.append(Card(color, CardType.DRAW_TWO))
        # 创建万能牌
        for _ in range(4):
            deck.append(Card(CardColor.WILD, CardType.WILD))
            deck.append(Card(CardColor.WILD, CardType.WILD_DRAW_FOUR))

        random.shuffle(deck)
        return deck
    def setup_gane(self):
        # 每个玩家发7张牌
        for player in self.players:
            for _ in range(7):
                if self.deck:
                    player.draw_card(self.deck.pop())

        # 从牌堆顶部翻一张牌作为起始牌
        while True:
            if not self.deck:
                self.reshuffle_discard_pile()

            top_card = self.deck.pop()
            if top_card.type == CardType.NUMBER:
                self.discard_pile.append(top_card)
                self.current_color = top_card.color
                break

        # 随机决定起始玩家(我怀疑减一是多余的，但我没有证据)
        self.current_player_index = random.randint(0, len(self.players) - 1)

    def reshuffle_discard_pile(self):
        """重新洗牌弃牌堆 (除了最上面一张) """
        if len(self.discard_pile) <= 1:
            # 如果弃牌堆没有足够的牌，重新创建一副牌
            self.deck = self.creat_deck()
            return

        # 保留最上面的一张牌，其余的牌加入洗洗牌
        top_card = self.discard_pile.pop()
        self.deck = self.discard_pile
        random.shuffle(self.deck)
        self.discard_pile = [top_card]

    def next_player(self):
        """移动到下一个玩家"""
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)

    def play_turn(self, card_index:Optional[int] = None, chosen_color:Optional[CardColor] = None):
        """执行一个回合"""
        current_player = self.players[self.current_player_index]
        top_card = self.discard_pile[-1]

        if card_index is not None and 0 <= card_index < len(current_player.hand):
            card = current_player.hand[card_index]
            if card.can_play_on(top_card) or (self.current_color and card.color == self.current_color):
                played_card = current_player.play_card(card_index)
                self.discard_pile.append(played_card)

                if played_card.type == CardType.SKIP:
                    self.next_player()
                elif played_card.type == CardType.REVERSE:
                    self.direction *= -1
                elif played_card.type == CardType.DRAW_TWO:
                    self.next_player()
                    self.draw_cards_for_player(2)
                elif played_card.type == CardType.WILD_DRAW_FOUR:
                    self.next_player()
                    self.draw_cards_for_player(4)

                if played_card.color == CardColor.WILD:
                    colors = [c for c in CardColor if c != CardColor.WILD]
                    self.current_color = colors[int(input("0-红,1-黄,2-绿,3-蓝"))]
                else:
                    self.current_color = played_card.color

                if len(current_player.hand) == 0:
                    self.game_over = True
                    print(f"游戏结束, {current_player.name}获胜")
                    return

                self.next_player()
            else:
                print("你不能出这张牌")
        else:
            # 如果不能出牌或没有指定出牌，就抽一张牌
            if not self.deck:
                self.reshuffle_discard_pile()

            if self.deck:
                drawn_card = 


if __name__ == "__main__":
    print([c for c in CardColor])