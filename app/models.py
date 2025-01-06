from dataclasses import dataclass
import datetime

@dataclass
class Mission:
    title: str
    description: str
    completed: bool = False

@dataclass
class Skill:
    name: str
    level: int = 1
    progress: int = 0  # 0-100

@dataclass
class Artifact:
    name: str
    collected: bool = False

@dataclass
class Reflection:
    date: str  # "YYYY-MM-DD"
    content: str

@dataclass
class Challenge:
    title: str
    deadline: str   # "YYYY-MM-DD"
    progress: int
    goal: int

@dataclass
class Profile:
    name: str