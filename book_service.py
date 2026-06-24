from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Iterable

import matplotlib.pyplot as plt
import requests
from PIL import Image, ImageOps

from config import (
    ASSETS_DIR,
    BACKUP_BOOK_IMAGE_PATH,
    BACKUP_BOOK_TEXT_PATH,
    BOOK_IMAGE_CACHE_PATH,
    BOOK_IMAGE_URL,
    BOOK_IMAGE_URLS,
    BOOK_TEXT_CACHE_PATH,
    BOOK_TEXT_URL,
    BOOK_TEXT_URLS,
    NETWORK_TIMEOUT,
    OUTPUT_DIR,
    USER_AGENT,
)
from models import BookAnalysis


class BookError(RuntimeError):
    pass


WORD_PATTERN = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[’'-][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*")


def _unique_urls(urls: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(url for url in urls if url))


def _download_bytes(
    urls: Iterable[str],
    *,
    accept: str,
    cache_path: Path,
    backup_path: Path,
    resource_name: str,
) -> tuple[bytes, str]:
    """Télécharge une ressource, puis utilise cache/copie locale si le réseau échoue."""
    errors: list[str] = []
    headers = {"User-Agent": USER_AGENT, "Accept": accept}

    for url in _unique_urls(urls):
        try:
            response = requests.get(url, timeout=NETWORK_TIMEOUT, headers=headers)
            response.raise_for_status()
            content = response.content
            if not content:
                raise ValueError("réponse vide")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(content)
            return content, f"Internet — {url}"
        except (requests.RequestException, OSError, ValueError) as exc:
            errors.append(f"{url} : {exc}")

    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path.read_bytes(), "Cache local d’un téléchargement précédent"

    if backup_path.exists() and backup_path.stat().st_size > 0:
        return backup_path.read_bytes(), "Copie locale de secours Project Gutenberg"

    details = "\n".join(errors[-3:]) or "aucune adresse disponible"
    raise BookError(
        f"Téléchargement de {resource_name} impossible et aucune copie locale n'est disponible.\n{details}"
    )


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise BookError("Le fichier texte téléchargé utilise un encodage non reconnu.")


def download_text(url: str = BOOK_TEXT_URL) -> str:
    """Fonction publique conservée pour les tests et les usages simples."""
    urls = (url, *BOOK_TEXT_URLS) if url else BOOK_TEXT_URLS
    data, _ = _download_bytes(
        urls,
        accept="text/plain,text/*;q=0.9,*/*;q=0.5",
        cache_path=BOOK_TEXT_CACHE_PATH,
        backup_path=BACKUP_BOOK_TEXT_PATH,
        resource_name="du livre",
    )
    return _decode_text(data)


def _download_text_with_source() -> tuple[str, str]:
    data, source = _download_bytes(
        BOOK_TEXT_URLS,
        accept="text/plain,text/*;q=0.9,*/*;q=0.5",
        cache_path=BOOK_TEXT_CACHE_PATH,
        backup_path=BACKUP_BOOK_TEXT_PATH,
        resource_name="du livre",
    )
    return _decode_text(data), source


def parse_metadata(text: str) -> tuple[str, str]:
    title_match = re.search(r"(?im)^Title:\s*(.+?)\s*$", text)
    author_match = re.search(r"(?im)^Author:\s*(.+?)\s*$", text)
    title = title_match.group(1).strip() if title_match else "Alice's Adventures in Wonderland"
    author = author_match.group(1).strip() if author_match else "Lewis Carroll"
    return title, author


def extract_first_chapter(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    marker_pairs = [
        (r"(?im)^\s*CHAPTER\s+I(?:\.|\s|$).*$", r"(?im)^\s*CHAPTER\s+II(?:\.|\s|$).*$"),
        (r"(?im)^\s*CHAPTER\s+1(?:\.|\s|$).*$", r"(?im)^\s*CHAPTER\s+2(?:\.|\s|$).*$"),
    ]
    candidates: list[str] = []
    for start_pattern, end_pattern in marker_pairs:
        starts = list(re.finditer(start_pattern, normalized))
        ends = list(re.finditer(end_pattern, normalized))
        for start in starts:
            end = next((item for item in ends if item.start() > start.start()), None)
            if end is not None:
                candidates.append(normalized[start.start():end.start()].strip())

    if candidates:
        chapter = max(candidates, key=len)
        if len(chapter) > 30:
            return chapter
    raise BookError("Le premier chapitre n'a pas pu être identifié dans le texte.")


def split_paragraphs(chapter: str) -> list[str]:
    blocks = re.split(r"\n\s*\n+", chapter.strip())
    paragraphs: list[str] = []
    for block in blocks:
        joined = re.sub(r"\s*\n\s*", " ", block).strip()
        upper = joined.upper()
        if upper.startswith("CHAPTER I") or upper.startswith("CHAPTER 1"):
            continue
        if len(WORD_PATTERN.findall(joined)) >= 2:
            paragraphs.append(joined)
    if not paragraphs:
        raise BookError("Aucun paragraphe exploitable n'a été détecté.")
    return paragraphs


def count_words(paragraph: str) -> int:
    return len(WORD_PATTERN.findall(paragraph))


def round_down_to_ten(value: int) -> int:
    return (value // 10) * 10


def build_distribution(counts: list[int]) -> dict[int, int]:
    return dict(sorted(Counter(round_down_to_ten(value) for value in counts).items()))


def save_distribution_chart(distribution: dict[int, int], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(9, 5.2))
    labels = [str(key) for key in distribution]
    values = list(distribution.values())
    axis.bar(labels, values)
    axis.set_title("Distribution des longueurs des paragraphes")
    axis.set_xlabel("Nombre de mots arrondi à la dizaine inférieure")
    axis.set_ylabel("Nombre de paragraphes")
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)
    return destination


def _process_image_bytes(data: bytes, logo_path: Path, destination: Path) -> Path:
    try:
        from io import BytesIO

        with Image.open(BytesIO(data)) as source:
            base = ImageOps.fit(source.convert("RGB"), (900, 1200), method=Image.Resampling.LANCZOS)

        if not logo_path.exists():
            raise BookError(f"Logo local introuvable : {logo_path}")

        with Image.open(logo_path) as logo_source:
            logo = logo_source.convert("RGBA")
            logo.thumbnail((240, 240), Image.Resampling.LANCZOS)
            logo = logo.rotate(18, expand=True, resample=Image.Resampling.BICUBIC)

        overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
        x = base.width - logo.width - 28
        y = base.height - logo.height - 28
        overlay.alpha_composite(logo, (x, y))
        result = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
        result.save(destination, quality=92)
        return destination
    except BookError:
        raise
    except (OSError, ValueError) as exc:
        raise BookError(f"Traitement de l'image impossible : {exc}") from exc


def _download_and_process_image_with_source(
    image_urls: Iterable[str] = BOOK_IMAGE_URLS,
    logo_path: Path | None = None,
    destination: Path | None = None,
    force_local_backup: bool = False,
) -> tuple[Path, str]:
    logo_path = logo_path or ASSETS_DIR / "logo_bw.png"
    destination = destination or OUTPUT_DIR / "alice_processed.jpg"
    destination.parent.mkdir(parents=True, exist_ok=True)

    if force_local_backup and BACKUP_BOOK_IMAGE_PATH.exists():
        data = BACKUP_BOOK_IMAGE_PATH.read_bytes()
        source = "Copie locale de secours Project Gutenberg"
    else:
        data, source = _download_bytes(
            image_urls,
            accept="image/*",
            cache_path=BOOK_IMAGE_CACHE_PATH,
            backup_path=BACKUP_BOOK_IMAGE_PATH,
            resource_name="de l'image",
        )

    return _process_image_bytes(data, logo_path, destination), source


def download_and_process_image(
    image_url: str = BOOK_IMAGE_URL,
    logo_path: Path | None = None,
    destination: Path | None = None,
) -> Path:
    path, _ = _download_and_process_image_with_source(
        image_urls=(image_url, *BOOK_IMAGE_URLS),
        logo_path=logo_path,
        destination=destination,
    )
    return path


def analyse_book(text: str | None = None) -> BookAnalysis:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if text is None:
        text, text_source = _download_text_with_source()
    else:
        text_source = "Texte fourni à la fonction"

    title, author = parse_metadata(text)
    chapter = extract_first_chapter(text)
    paragraphs = split_paragraphs(chapter)
    counts = [count_words(paragraph) for paragraph in paragraphs]
    distribution = build_distribution(counts)
    chart_path = save_distribution_chart(
        distribution, OUTPUT_DIR / "paragraph_distribution.png"
    )

    # Si Gutenberg est inaccessible pour le texte, on évite d'attendre une seconde
    # série de timeouts sur le même domaine pour l'image.
    text_is_online = text_source.startswith("Internet")
    processed_image_path, image_source = _download_and_process_image_with_source(
        force_local_backup=not text_is_online
    )

    return BookAnalysis(
        title=title,
        author=author,
        first_chapter=chapter,
        paragraph_word_counts=counts,
        rounded_distribution=distribution,
        total_words=sum(counts),
        min_words=min(counts),
        max_words=max(counts),
        average_words=mean(counts),
        processed_image_path=processed_image_path,
        chart_path=chart_path,
        text_source=text_source,
        image_source=image_source,
    )
