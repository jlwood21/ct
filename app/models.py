from dataclasses import dataclass

@dataclass
class Mission:
    title: str
    description: str
    completed: bool = False

@dataclass
class Skill:
    name: str
    level: int = 1
    progress: int = 0

@dataclass
class Artifact:
    name: str
    collected: bool = False

@dataclass
class Reflection:
    date: str
    content: str

@dataclass
class Challenge:
    title: str
    deadline: str
    progress: int
    goal: int

@dataclass
class Profile:
    name: str
    title: str = "Stargazer"
    avatar_color: str = "white"