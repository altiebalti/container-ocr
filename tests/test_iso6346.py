import random
import string

import pytest

from app.iso6346 import (LETTER_VALUES, Token, analyze, check_digit, find_candidates,
                         find_size_type, format_number, is_valid_number)


def reference_check_digit(code: str) -> int:
    \
    table = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                     [10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 34, 35, 36, 37, 38]))
    s = sum((int(c) if c.isdigit() else table[c]) * 2 ** i for i, c in enumerate(code))
    return s % 11 % 10


def make_valid(prefix: str, serial: str) -> str:
    return prefix + serial + str(reference_check_digit(prefix + serial))


def test_letter_values_skip_multiples_of_11():
    assert LETTER_VALUES["A"] == 10
    assert LETTER_VALUES["B"] == 12
    assert LETTER_VALUES["L"] == 23
    assert LETTER_VALUES["V"] == 34
    assert LETTER_VALUES["Z"] == 38


def test_known_example_from_standard():
    assert check_digit("CSQU305438") == 3
    assert is_valid_number("CSQU 305438 3")
    assert is_valid_number("csqu-305438-3")
    assert not is_valid_number("CSQU3054384")


def test_matches_reference_on_random_numbers():
    rng = random.Random(1)
    for _ in range(2000):
        code = "".join(rng.choice(string.ascii_uppercase) for _ in range(3)) + rng.choice("UJZ") + \
            "".join(rng.choice(string.digits) for _ in range(6))
        assert check_digit(code) == reference_check_digit(code)


def test_format():
    assert format_number("CSQU3054383") == "CSQU 305438 3"


@pytest.mark.parametrize("words", [
    ["CSQU", "305438", "3"],
    ["CSQU3054383"],
    ["CSQU", "3054383"],
    ["CSQU", "305438-3"],
    ["CSQU", "305438", "|3|"],
    list("CSQU3054383"),
    ["MAX", "GROSS", "30480", "KG", "CSQU", "305438", "3", "45G1"],
])
def test_finds_number_in_different_layouts(words):
    found = find_candidates([Token(w) for w in words])
    assert found and found[0].number == "CSQU3054383" and found[0].valid


def test_corrects_ocr_confusions_only_when_check_digit_confirms():

    number = make_valid("OOLU", "101234")
    noisy = "0OLU" + number[4:].replace("1", "I", 1)
    found = find_candidates([Token(noisy[:4]), Token(noisy[4:10]), Token(noisy[10])])
    assert found[0].number == number
    assert found[0].valid and found[0].corrections == 2

    noisier = noisy[:5] + noisy[5:].replace("0", "O", 1)
    assert find_candidates([Token(noisier)]) == []


def test_rejects_correction_that_does_not_validate():
    number = make_valid("MSCU", "123456")
    wrong = number[:10] + str((int(number[10]) + 1) % 10)
    noisy = wrong[:5] + "O" + wrong[6:]
    assert find_candidates([Token(noisy)]) == []


def test_reports_invalid_check_digit_without_corrections():
    number = make_valid("MSCU", "123456")
    wrong = number[:10] + str((int(number[10]) + 1) % 10)
    result = analyze([Token(wrong[:4]), Token(wrong[4:10]), Token(wrong[10])])
    assert result["status"] == "invalid_check_digit"
    assert result["container"]["expected_check_digit"] == int(number[10])


def test_prefers_valid_candidate():
    good = make_valid("TGHU", "878046")
    bad = make_valid("MSCU", "123456")
    bad = bad[:10] + str((int(bad[10]) + 1) % 10)
    found = find_candidates([Token(bad), Token("and"), Token(good)])
    assert [c.number for c in found] == [good, bad]


def test_box_is_union_of_word_boxes():
    found = find_candidates([Token("CSQU", [10, 20, 60, 40]), Token("305438", [70, 22, 150, 41]),
                             Token("3", [160, 18, 170, 42])])
    assert found[0].box == [10, 18, 170, 42]


def test_not_found():
    result = analyze([Token(w) for w in "MAX GROSS 30480 KG TARE 2200 KG".split()])
    assert result["status"] == "not_found" and result["container"] is None


def test_size_type():
    st = find_size_type([Token("CSQU"), Token("45G1")])
    assert st["code"] == "45G1" and st["length"] == "40 футів" and "high cube" in st["height"]
    assert find_size_type([Token("TARE"), Token("2260")]) is None


def test_analyze_falls_back_to_full_text():
    result = analyze([], "SOME TEXT\nCSQU 305438 3\n22G1")
    assert result["status"] == "valid"
    assert result["container"]["formatted"] == "CSQU 305438 3"
    assert result["size_type"]["code"] == "22G1"


def test_missing_check_digit_is_computed():
    result = analyze([Token("CSQU"), Token("305438"), Token("45G1")])
    assert result["status"] == "check_digit_missing"
    c = result["container"]
    assert c["number"] == "CSQU3054383" and c["check_digit_read"] is False and c["valid"] is False


def test_full_number_beats_partial():
    result = analyze([Token("CSQU"), Token("305438"), Token("3")])
    assert result["status"] == "valid" and result["container"]["check_digit_read"] is True


def test_partial_requires_exact_match():
    assert analyze([Token("CSQU"), Token("3O5438")])["status"] == "not_found"
