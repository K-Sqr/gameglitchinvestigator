def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIX: "Hard" originally returned (1, 50) which was easier than Normal (1, 100).
    # Changed to (1, 500) so Hard is genuinely harder.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 500
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
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

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome: "Win", "Too High", or "Too Low"
    """
    # FIX: Original code had swapped emoji messages -- "Go HIGHER!" was shown when
    # the guess was too high, and "Go LOWER!" when too low. Corrected so the message
    # matches the direction the player should actually go.
    # Also removed the TypeError fallback that did string comparison, which produced
    # unreliable results when the secret was cast to str on even attempts.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # FIX: Original scoring was inconsistent -- "Too High" alternated between +5 and
    # -5 based on attempt parity, while "Too Low" always deducted 5. Simplified to a
    # flat -5 penalty for any wrong guess. Also fixed win formula which used
    # (attempt_number + 1), over-penalizing the player by one step.
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
