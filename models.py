from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TodoRecord:
    remote_id: int
    user_id: int
    name: str
    state: str
    length: int


@dataclass(frozen=True)
class BookAnalysis:
    title: str
    author: str
    first_chapter: str
    paragraph_word_counts: list[int]
    rounded_distribution: dict[int, int]
    total_words: int
    min_words: int
    max_words: int
    average_words: float
    processed_image_path: Path
    chart_path: Path
    text_source: str = "Internet"
    image_source: str = "Internet"
