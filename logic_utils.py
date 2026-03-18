"""Core game logic for the Glitchy Guesser number-guessing game.

This module contains all pure-logic functions separated from the Streamlit UI
layer, making them independently testable. It also provides persistence helpers
for the high-score tracker.
"""

import json
import os
from typing import Optional

HIGH_SCORE_FILE = "high_scores.json"


def load_high_scores() -> dict:
    """Load the high-score table from disk.

    Reads ``HIGH_SCORE_FILE`` and returns a dictionary mapping difficulty names
    (e.g. ``"Easy"``, ``"Normal"``, ``"Hard"``) to their best recorded scores.
    If the file is missing or corrupted, an empty dict is returned so the game
    can start fresh.

    Returns:
        dict: Mapping of ``{difficulty: best_score}``.
    """
    if not os.path.exists(HIGH_SCORE_FILE):
        return {}
    try:
        with open(HIGH_SCORE_FILE, "r") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, IOError):
        return {}


def save_high_score(difficulty: str, score: int) -> bool:
    """Persist a new high score if it beats the current record.

    Compares *score* against the stored best for *difficulty*. If no record
    exists yet or *score* is strictly greater, the file is updated.

    Args:
        difficulty: The difficulty level name (``"Easy"``, ``"Normal"``, or
            ``"Hard"``).
        score: The player's final score to evaluate.

    Returns:
        bool: ``True`` if a new high score was saved, ``False`` otherwise.
    """
    scores = load_high_scores()
    current_best = scores.get(difficulty, None)
    if current_best is None or score > current_best:
        scores[difficulty] = score
        with open(HIGH_SCORE_FILE, "w") as fh:
            json.dump(scores, fh, indent=2)
        return True
    return False


def get_closeness_label(
    guess: int, secret: int, low: int, high: int
) -> str:
    """Return a Hot/Cold emoji label indicating proximity to the secret.

    Closeness is expressed as the absolute distance between *guess* and
    *secret* divided by the total range (``high - low``). Thresholds:

    * <= 5 %  -- Burning hot
    * <= 15 % -- Very warm
    * <= 30 % -- Warm
    * <= 50 % -- Cool
    * > 50 %  -- Ice cold

    Args:
        guess: The player's guessed number.
        secret: The target number.
        low: Lower bound of the difficulty range (inclusive).
        high: Upper bound of the difficulty range (inclusive).

    Returns:
        str: An emoji-prefixed closeness label.
    """
    total_range = high - low
    if total_range == 0:
        return "🎯 Exact!"
    distance = abs(guess - secret)
    pct = distance / total_range

    if pct <= 0.05:
        return "🔥 Burning hot!"
    if pct <= 0.15:
        return "🟠 Very warm"
    if pct <= 0.30:
        return "🟡 Warm"
    if pct <= 0.50:
        return "🟢 Cool"
    return "🥶 Ice cold"


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive numeric range for a given difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.
            Any unrecognised value falls back to the Normal range.

    Returns:
        tuple[int, int]: ``(low, high)`` bounds for random number generation.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 500)
    """
    # FIX: "Hard" originally returned (1, 50) which was easier than Normal (1, 100).
    # Changed to (1, 500) so Hard is genuinely harder.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 500
    return 1, 100


def parse_guess(raw: Optional[str]) -> tuple[bool, Optional[int], Optional[str]]:
    """Parse raw user input into a validated integer guess.

    Handles ``None``, empty strings, decimals (truncated to int via
    ``int(float(...))``) and non-numeric garbage. Strings like ``"inf"`` and
    ``"NaN"`` are rejected because ``int(float(...))`` raises for those values.
    Values outside +/-1,000,000 are rejected to prevent overflow errors in the
    Streamlit/Arrow rendering pipeline.

    Args:
        raw: The string entered by the player, or ``None`` if nothing was
            submitted.

    Returns:
        tuple: A three-element tuple ``(ok, guess_int, error_message)``.

        * ``ok`` (bool): ``True`` when parsing succeeded.
        * ``guess_int`` (int | None): The parsed integer, or ``None`` on
          failure.
        * ``error_message`` (str | None): A human-readable error, or ``None``
          on success.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    if value > 10**6 or value < -(10**6):
        return False, None, "That number is out of range."

    return True, value, None


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare *guess* to *secret* and return the outcome with a hint message.

    Args:
        guess: The player's guessed number.
        secret: The target number the player is trying to find.

    Returns:
        tuple[str, str]: ``(outcome, message)`` where *outcome* is one of
        ``"Win"``, ``"Too High"``, or ``"Too Low"``, and *message* is a
        user-facing emoji string.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
    """
    # FIX: Original code had swapped emoji messages. Corrected so the message
    # matches the direction the player should actually go.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate the new score after a guess.

    Scoring rules:

    * **Win**: ``100 - 10 * attempt_number`` bonus points (minimum 10).
    * **Wrong guess** (``"Too High"`` or ``"Too Low"``): flat -5 penalty.
    * **Any other outcome**: score unchanged.

    Args:
        current_score: The player's score before this guess.
        outcome: The result string from :func:`check_guess`.
        attempt_number: Which attempt this is (1-based).

    Returns:
        int: The updated score.

    Examples:
        >>> update_score(0, "Win", 1)
        90
        >>> update_score(50, "Too High", 3)
        45
    """
    # FIX: Original scoring was inconsistent. Simplified to a flat -5 penalty
    # for any wrong guess. Fixed win formula from (attempt_number + 1).
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
