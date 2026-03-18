from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score


# --- check_guess tests ---

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


# --- parse_guess tests ---

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


# --- get_range_for_difficulty tests ---

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


# --- update_score tests ---

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
