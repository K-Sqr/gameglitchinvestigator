import random
import streamlit as st
import pandas as pd

# FIX: Refactored core logic into logic_utils.py using Copilot Agent mode.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    load_high_scores,
    save_high_score,
    get_closeness_label,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮", layout="wide")

st.title("🎮 Game Glitch Investigator")
st.caption("A number-guessing game -- now fully debugged and enhanced!")

# ── Sidebar: Settings ──────────────────────────────────────
st.sidebar.header("⚙️ Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# ── Sidebar: High Scores ───────────────────────────────────
st.sidebar.divider()
st.sidebar.header("🏆 High Scores")
high_scores = load_high_scores()
for diff in ("Easy", "Normal", "Hard"):
    best = high_scores.get(diff, "—")
    st.sidebar.metric(label=diff, value=best)

# ── Session state initialization ───────────────────────────
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: attempts was initialized to 1 instead of 0.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# ── Main area ──────────────────────────────────────────────
main_col, history_col = st.columns([2, 1])

with main_col:
    st.subheader("Make a guess")

    # FIX: Info text now uses actual difficulty range instead of hardcoded "1 and 100".
    st.info(
        f"Guess a number between **{low}** and **{high}**. "
        f"Attempts left: **{attempt_limit - st.session_state.attempts}**"
    )

    with st.expander("Developer Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)

    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.button("Submit Guess ")
    with col2:
        new_game = st.button("New Game ")
    with col3:
        show_hint = st.checkbox("Show hint", value=True)

    if new_game:
        st.session_state.attempts = 0
        # FIX: New Game now uses selected difficulty range.
        st.session_state.secret = random.randint(low, high)
        st.session_state.score = 0
        st.session_state.status = "playing"
        st.session_state.history = []
        st.success("New game started.")
        st.rerun()

    if st.session_state.status != "playing":
        if st.session_state.status == "won":
            st.success("You already won! Start a new game to play again.")
        else:
            st.error("Game over. Start a new game to try again.")
        st.stop()

    if submit:
        st.session_state.attempts += 1

        ok, guess_int, err = parse_guess(raw_guess)

        if not ok:
            st.session_state.history.append(
                {"guess": raw_guess, "outcome": "Invalid", "hint": err}
            )
            st.error(err)
        else:
            # FIX: Removed string-casting of secret on even attempts.
            outcome, message = check_guess(guess_int, st.session_state.secret)

            closeness = get_closeness_label(
                guess_int, st.session_state.secret, low, high
            )

            st.session_state.history.append(
                {"guess": guess_int, "outcome": outcome, "hint": closeness}
            )

            if show_hint:
                if outcome == "Too High":
                    st.error(f"📉 **Too High!** Go lower. {closeness}")
                elif outcome == "Too Low":
                    st.warning(f"📈 **Too Low!** Go higher. {closeness}")
                else:
                    st.success(message)

            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )

            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                is_new_best = save_high_score(difficulty, st.session_state.score)
                st.success(
                    f"🎉 You won! The secret was **{st.session_state.secret}**. "
                    f"Final score: **{st.session_state.score}**"
                )
                if is_new_best:
                    st.info("🏆 New high score!")
            else:
                if st.session_state.attempts >= attempt_limit:
                    st.session_state.status = "lost"
                    st.error(
                        f"Out of attempts! "
                        f"The secret was **{st.session_state.secret}**. "
                        f"Score: **{st.session_state.score}**"
                    )

# ── Sidebar-style column: Guess History ────────────────────
with history_col:
    st.subheader("📜 Guess History")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df.index = range(1, len(df) + 1)
        df.index.name = "#"
        st.dataframe(df, use_container_width=True)
    else:
        st.caption("No guesses yet. Make your first move!")

st.divider()
st.caption("Debugged, tested, and enhanced -- by a human working with AI.")
