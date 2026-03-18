# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Game purpose:** A Streamlit number-guessing game where the player picks a difficulty, then guesses a secret number within a limited number of attempts, receiving directional hints after each guess.
- [x] **Bugs found:**
  1. Hint messages were swapped ("Go HIGHER!" when the guess was too high).
  2. Hard difficulty used a smaller range (1-50) than Normal (1-100).
  3. Secret was cast to string on even attempts, breaking comparisons.
  4. Scoring was inconsistent -- "Too High" alternated +5/-5, "Too Low" always -5.
  5. Attempts initialized to 1 instead of 0, losing one attempt on first game.
  6. Info text hardcoded to "between 1 and 100" regardless of difficulty.
  7. "New Game" generated secret in 1-100 range instead of the difficulty range.
- [x] **Fixes applied:**
  - Refactored all game logic (`check_guess`, `parse_guess`, `get_range_for_difficulty`, `update_score`) into `logic_utils.py`.
  - Corrected hint messages to match the direction the player should guess.
  - Changed Hard range to (1, 500).
  - Removed the string-casting hack on even attempts.
  - Simplified scoring to a flat -5 penalty for wrong guesses and fixed the win formula.
  - Fixed attempts initialization to 0.
  - Made info text and "New Game" use the actual difficulty range.
  - Wrote 22 pytest tests covering all logic functions and edge cases.

## 📸 Demo

[Insert a screenshot of your fixed, winning game here]

## 🚀 Stretch Features

[If you choose to complete a stretch challenge, insert a screenshot here]
