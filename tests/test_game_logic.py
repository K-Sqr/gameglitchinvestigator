import json
import os

import pytest

from logic_utils import (
    check_guess,
    parse_guess,
    get_range_for_difficulty,
    update_score,
    get_closeness_label,
    load_high_scores,
    save_high_score,
    HIGH_SCORE_FILE,
)


# ============================================================
# check_guess tests
# ============================================================

def test_winning_guess():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_guess_too_high():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_guess_too_low():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_guess_boundary_high():
    outcome, _ = check_guess(51, 50)
    assert outcome == "Too High"


def test_guess_boundary_low():
    outcome, _ = check_guess(49, 50)
    assert outcome == "Too Low"


def test_guess_negative_secret():
    outcome, _ = check_guess(-10, -10)
    assert outcome == "Win"


def test_guess_negative_too_high():
    outcome, _ = check_guess(-1, -10)
    assert outcome == "Too High"


def test_guess_negative_too_low():
    outcome, _ = check_guess(-20, -10)
    assert outcome == "Too Low"


def test_guess_zero():
    outcome, _ = check_guess(0, 0)
    assert outcome == "Win"


def test_guess_very_large_numbers():
    outcome, _ = check_guess(10**9, 10**9)
    assert outcome == "Win"


def test_guess_very_large_too_high():
    outcome, _ = check_guess(10**9, 1)
    assert outcome == "Too High"


def test_guess_very_large_too_low():
    outcome, _ = check_guess(1, 10**9)
    assert outcome == "Too Low"


def test_guess_one_off_above():
    outcome, _ = check_guess(100, 99)
    assert outcome == "Too High"


def test_guess_one_off_below():
    outcome, _ = check_guess(99, 100)
    assert outcome == "Too Low"


# ============================================================
# parse_guess tests
# ============================================================

def test_parse_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_decimal_truncates():
    ok, value, err = parse_guess("3.7")
    assert ok is True
    assert value == 3
    assert err is None


def test_parse_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert "Enter" in err


def test_parse_none():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert value is None


def test_parse_non_numeric():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None
    assert "not a number" in err


def test_parse_negative_number():
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5
    assert err is None


def test_parse_very_large_number():
    ok, value, err = parse_guess("999999999")
    assert ok is True
    assert value == 999999999
    assert err is None


# --- Challenge 1: Advanced edge-case inputs ---

def test_parse_negative_decimal():
    ok, value, err = parse_guess("-3.9")
    assert ok is True
    assert value == -3
    assert err is None


def test_parse_whitespace_only():
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert "not a number" in err


def test_parse_special_characters():
    ok, value, err = parse_guess("!@#$")
    assert ok is False
    assert "not a number" in err


def test_parse_leading_zeros():
    ok, value, err = parse_guess("007")
    assert ok is True
    assert value == 7


def test_parse_plus_sign():
    ok, value, err = parse_guess("+42")
    assert ok is True
    assert value == 42


def test_parse_extremely_large_integer():
    ok, value, err = parse_guess("99999999999999999999")
    assert ok is True
    assert value == 99999999999999999999


def test_parse_float_with_no_integer_part():
    ok, value, err = parse_guess(".5")
    assert ok is True
    assert value == 0


def test_parse_double_dot():
    ok, value, err = parse_guess("1.2.3")
    assert ok is False
    assert "not a number" in err


def test_parse_infinity_string():
    ok, value, err = parse_guess("inf")
    assert ok is False
    assert "not a number" in err


def test_parse_nan_string():
    ok, value, err = parse_guess("NaN")
    assert ok is False
    assert "not a number" in err


# ============================================================
# get_range_for_difficulty tests
# ============================================================

def test_easy_range():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20


def test_normal_range():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 100


def test_hard_range_is_larger_than_normal():
    _, hard_high = get_range_for_difficulty("Hard")
    _, normal_high = get_range_for_difficulty("Normal")
    assert hard_high > normal_high


def test_unknown_difficulty_falls_back():
    low, high = get_range_for_difficulty("Unknown")
    assert low == 1
    assert high == 100


def test_empty_string_difficulty():
    low, high = get_range_for_difficulty("")
    assert low == 1
    assert high == 100


def test_case_sensitive_difficulty():
    low, high = get_range_for_difficulty("easy")
    assert low == 1
    assert high == 100


def test_difficulty_ranges_are_positive():
    for diff in ("Easy", "Normal", "Hard"):
        low, high = get_range_for_difficulty(diff)
        assert low >= 1
        assert high > low


# ============================================================
# update_score tests
# ============================================================

def test_score_win_first_attempt():
    score = update_score(0, "Win", 1)
    assert score == 90


def test_score_win_late_attempt():
    score = update_score(0, "Win", 10)
    assert score == 10


def test_score_win_never_below_ten():
    score = update_score(0, "Win", 100)
    assert score == 10


def test_score_wrong_guess_deducts():
    score = update_score(50, "Too High", 1)
    assert score == 45


def test_score_too_low_deducts():
    score = update_score(50, "Too Low", 1)
    assert score == 45


def test_score_wrong_guess_consistent_regardless_of_parity():
    score_even = update_score(50, "Too High", 2)
    score_odd = update_score(50, "Too High", 3)
    assert score_even == score_odd == 45


def test_score_unknown_outcome_unchanged():
    score = update_score(50, "InvalidOutcome", 1)
    assert score == 50


def test_score_can_go_negative():
    score = update_score(0, "Too High", 1)
    assert score == -5


def test_score_win_second_attempt():
    score = update_score(0, "Win", 2)
    assert score == 80


def test_score_accumulates_penalties():
    score = 100
    for i in range(1, 6):
        score = update_score(score, "Too High", i)
    assert score == 75


def test_score_win_after_penalties():
    score = update_score(-15, "Win", 3)
    assert score == -15 + 70


# ============================================================
# get_closeness_label tests
# ============================================================

def test_closeness_burning_hot():
    label = get_closeness_label(50, 51, 1, 100)
    assert "hot" in label.lower()


def test_closeness_ice_cold():
    label = get_closeness_label(1, 99, 1, 100)
    assert "cold" in label.lower()


def test_closeness_warm():
    label = get_closeness_label(50, 65, 1, 100)
    assert "warm" in label.lower() or "Warm" in label


def test_closeness_zero_range():
    label = get_closeness_label(5, 5, 5, 5)
    assert "Exact" in label


# ============================================================
# High score persistence tests
# ============================================================

@pytest.fixture(autouse=False)
def clean_high_scores(tmp_path, monkeypatch):
    """Redirect HIGH_SCORE_FILE to a temp directory for isolation."""
    tmp_file = str(tmp_path / "high_scores.json")
    monkeypatch.setattr("logic_utils.HIGH_SCORE_FILE", tmp_file)
    yield tmp_file


def test_load_empty_when_no_file(clean_high_scores):
    assert load_high_scores() == {}


def test_save_and_load_high_score(clean_high_scores):
    assert save_high_score("Easy", 80) is True
    scores = load_high_scores()
    assert scores["Easy"] == 80


def test_save_does_not_overwrite_better_score(clean_high_scores):
    save_high_score("Normal", 90)
    assert save_high_score("Normal", 50) is False
    assert load_high_scores()["Normal"] == 90


def test_save_overwrites_worse_score(clean_high_scores):
    save_high_score("Hard", 30)
    assert save_high_score("Hard", 70) is True
    assert load_high_scores()["Hard"] == 70
