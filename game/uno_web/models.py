from dataclasses import dataclass
from typing import List, Dict, Any
import enum

class GameStatus(enum.Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"

@dataclass
class Game:
    id: str
    players: List[str]
    status: GameStatus
    max_players: int = 4

@dataclass
class Player:
    id: str
    name: str
    game_id: str