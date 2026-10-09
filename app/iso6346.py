"""
Пошук і перевірка номерів контейнерів за стандартом ISO 6346.

Номер контейнера: 3 літери коду власника + категорія (U, J або Z) + 6 цифр серійного
номера + 1 контрольна цифра, наприклад CSQU 305438 3.

Контрольна цифра: кожен з перших 10 символів переводиться в число (цифри як є, літери
A=10, B=12, ... Z=38 з пропуском кратних 11), множиться на 2^позиція, сума береться за
модулем 11, а результат 10 записується як 0.
"""
from __future__ import annotations

import re
import string
from dataclasses import dataclass, field

# --------------------------------------------------------------------------- значення літер


def _letter_values() -> dict[str, int]:
    values, v = {}, 10
    for ch in string.ascii_uppercase:
        if v % 11 == 0:          # 11, 22, 33 пропускаються
            v += 1
        values[ch] = v
        v += 1
    return values


LETTER_VALUES = _letter_values()

CATEGORIES = {
    "U": "вантажний контейнер",
    "J": "знімне обладнання для контейнера",
    "Z": "трейлер або шасі",
}

# Типові помилки OCR: у позиціях, де мають бути літери, цифри читаються як схожі літери,
# і навпаки. Виправлення приймаються, лише якщо після них контрольна цифра сходиться.
TO_LETTER = {"0": "O", "1": "I", "2": "Z", "4": "A", "5": "S", "6": "G", "7": "T", "8": "B"}
TO_DIGIT = {"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1", "Z": "2", "A": "4",
            "S": "5", "G": "6", "T": "7", "B": "8"}
TO_CATEGORY = {"V": "U", "2": "Z"}
MAX_CORRECTIONS = 2


def check_digit(first10: str) -> int:
    """Контрольна цифра для перших 10 символів номера (наприклад 'CSQU305438' -> 3)."""
    if len(first10) != 10:
        raise ValueError("expected 10 characters, got %d" % len(first10))
    total = 0
    for i, ch in enumerate(first10.upper()):
        value = int(ch) if ch.isdigit() else LETTER_VALUES[ch]
        total += value * (1 << i)
    return total % 11 % 10


def is_valid_number(number: str) -> bool:
    number = re.sub(r"[^A-Za-z0-9]", "", number).upper()
    if not re.fullmatch(r"[A-Z]{3}[UJZ]\d{7}", number):
        return False
    return check_digit(number[:10]) == int(number[10])


def format_number(number: str) -> str:
    return "%s %s %s" % (number[:4], number[4:10], number[10])


# --------------------------------------------------------------------------- кандидати


@dataclass
class Token:
    """Слово з OCR і його прямокутник [x0, y0, x1, y1] у пікселях (якщо відомий)."""
    text: str
    box: list[int] | None = None


@dataclass
class Candidate:
    number: str                 # 11 символів після виправлень
    raw: str                    # як прочитав OCR (токени через пробіл)
    corrections: int            # скільки символів виправлено
    valid: bool                 # чи сходиться контрольна цифра
    expected_check_digit: int
    order: int                  # позиція в тексті (для впорядкування)
    box: list[int] | None = None
    check_digit_read: bool = True   # False - контрольну цифру не прочитано, її обчислено

    @property
    def category(self) -> str:
        return self.number[3]

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "formatted": format_number(self.number),
            "owner_code": self.number[:3],
            "category": self.category,
            "category_name": CATEGORIES.get(self.category, ""),
            "serial": self.number[4:10],
            "check_digit": int(self.number[10]),
            "expected_check_digit": self.expected_check_digit,
            "check_digit_read": self.check_digit_read,
            "valid": self.valid,
            "raw": self.raw,
            "corrected": self.corrections > 0,
            "box": self.box,
        }


def _normalize(chars: str) -> tuple[str, int] | None:
    """Привести 11 символів до формату AAAU0000000 з мінімумом виправлень.
    Повертає (номер, кількість виправлень) або None, якщо це не схоже на номер."""
    out, fixes = [], 0
    for i, ch in enumerate(chars):
        if i < 3:
            if ch.isalpha():
                out.append(ch)
            elif ch in TO_LETTER:
                out.append(TO_LETTER[ch])
                fixes += 1
            else:
                return None
        elif i == 3:
            if ch in CATEGORIES:
                out.append(ch)
            elif ch in TO_CATEGORY:
                out.append(TO_CATEGORY[ch])
                fixes += 1
            else:
                return None
        else:
            if ch.isdigit():
                out.append(ch)
            elif ch in TO_DIGIT:
                out.append(TO_DIGIT[ch])
                fixes += 1
            else:
                return None
        if fixes > MAX_CORRECTIONS:
            return None
    return "".join(out), fixes


def _union(boxes: list[list[int] | None]) -> list[int] | None:
    boxes = [b for b in boxes if b]
    if not boxes:
        return None
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def _alnum(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def find_candidates(tokens: list[Token], max_tokens: int = 16) -> list[Candidate]:
    """Шукає номери в послідовності слів OCR.

    Номер може бути розбитий на кілька слів ('CSQU' '305438' '3'), написаний разом
    ('CSQU3054383') або вертикально, по одній літері в рядку. Тому перебираються всі вікна
    з сусідніх слів, у яких разом рівно 11 літер/цифр.
    """
    alnum = [_alnum(t.text) for t in tokens]
    best: dict[str, Candidate] = {}
    for i in range(len(tokens)):
        if not alnum[i]:
            continue
        acc = ""
        for j in range(i, min(len(tokens), i + max_tokens)):
            acc += alnum[j]
            if len(acc) > 11:
                break
            if len(acc) < 11:
                continue
            norm = _normalize(acc)
            if norm is None:
                break
            number, fixes = norm
            expected = check_digit(number[:10])
            valid = expected == int(number[10])
            if fixes and not valid:
                break        # виправлення без підтвердження контрольною цифрою не приймаємо
            cand = Candidate(
                number=number,
                raw=" ".join(t.text for t in tokens[i:j + 1] if _alnum(t.text)),
                corrections=fixes,
                valid=valid,
                expected_check_digit=expected,
                order=i,
                box=_union([t.box for t in tokens[i:j + 1]]),
            )
            prev = best.get(number)
            if prev is None or _rank(cand) < _rank(prev):
                best[number] = cand
            break
    return sorted(best.values(), key=_rank)


PARTIAL_RE = re.compile(r"[A-Z]{3}[UJZ]\d{6}")


def find_partial(tokens: list[Token], max_tokens: int = 14) -> list[Candidate]:
    """Код власника і серійний номер без контрольної цифри (її часто не видно або OCR
    не читає цифру в рамці). Без контрольної цифри виправлення не перевірити, тому
    приймаються лише точні збіги, а контрольна цифра обчислюється."""
    alnum = [_alnum(t.text) for t in tokens]
    found: dict[str, Candidate] = {}
    for i in range(len(tokens)):
        if not alnum[i]:
            continue
        acc = ""
        for j in range(i, min(len(tokens), i + max_tokens)):
            acc += alnum[j]
            if len(acc) > 10:
                break
            if len(acc) == 10:
                if PARTIAL_RE.fullmatch(acc) and acc not in found:
                    digit = check_digit(acc)
                    found[acc] = Candidate(
                        number=acc + str(digit),
                        raw=" ".join(t.text for t in tokens[i:j + 1] if _alnum(t.text)),
                        corrections=0, valid=False, expected_check_digit=digit, order=i,
                        box=_union([t.box for t in tokens[i:j + 1]]), check_digit_read=False)
                break
    return sorted(found.values(), key=lambda c: (c.category != "U", c.order))


def _rank(c: Candidate):
    return (not c.valid, c.corrections, c.category != "U", c.order)


def tokens_from_text(text: str) -> list[Token]:
    """Якщо OCR не дав окремих слів, ділимо повний текст за пробілами (без координат)."""
    return [Token(w) for w in text.split()]


# --------------------------------------------------------------------------- код розміру і типу

LENGTHS = {"1": "10 футів", "2": "20 футів", "3": "30 футів", "4": "40 футів", "L": "45 футів"}
HEIGHTS = {"0": "8 футів", "2": "8 футів 6 дюймів", "4": "9 футів",
           "5": "9 футів 6 дюймів (high cube)", "6": "понад 9 футів 6 дюймів"}
TYPES = {
    "G": "універсальний (general purpose)",
    "V": "вентильований",
    "B": "для сипучих вантажів (bulk)",
    "S": "для спецвантажів (named cargo)",
    "R": "рефрижератор",
    "H": "ізотермічний",
    "U": "з відкритим верхом (open top)",
    "P": "платформа / flat rack",
    "T": "танк-контейнер",
    "A": "для повітряно-наземних перевезень",
}
SIZE_TYPE_RE = re.compile(r"^([1234L])([02456])([GVBSRHUPTA])(\d)$")


def find_size_type(tokens: list[Token]) -> dict | None:
    """Код розміру і типу (наприклад 45G1), який зазвичай нанесено під номером."""
    for t in tokens:
        m = SIZE_TYPE_RE.match(_alnum(t.text))
        if m and len(_alnum(t.text)) == 4:
            length, height, kind, _ = m.groups()
            return {
                "code": m.group(0),
                "length": LENGTHS[length],
                "height": HEIGHTS[height],
                "type": TYPES[kind],
                "box": t.box,
            }
    return None


# --------------------------------------------------------------------------- підсумок


def analyze(tokens: list[Token], text: str = "") -> dict:
    """Повний розбір результату OCR: найкращий номер, інші кандидати, код типу."""
    if not tokens and text:
        tokens = tokens_from_text(text)
    candidates = find_candidates(tokens)
    if not candidates and text:
        # запасний варіант: слова з повного тексту (інший порядок і розбиття)
        candidates = find_candidates(tokens_from_text(text))
    if not candidates:
        candidates = find_partial(tokens) or (find_partial(tokens_from_text(text)) if text else [])
    best = candidates[0] if candidates else None
    if best is None:
        status = "not_found"
    elif not best.check_digit_read:
        status = "check_digit_missing"
    elif best.valid:
        status = "valid"
    else:
        status = "invalid_check_digit"
    return {
        "status": status,
        "container": best.to_dict() if best else None,
        "candidates": [c.to_dict() for c in candidates[:5]],
        "size_type": find_size_type(tokens) or (find_size_type(tokens_from_text(text)) if text else None),
    }
