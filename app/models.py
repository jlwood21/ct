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
    progress: int = 0  # percentage (0-100)

@dataclass
class Artifact:
    name: str
    collected: bool = False
