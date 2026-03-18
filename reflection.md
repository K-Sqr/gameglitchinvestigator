# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it looked like a normal Streamlit number-guessing app, but playing it revealed serious problems almost immediately. The hint messages were backwards: when my guess was too high, the game told me to "Go HIGHER!" and when my guess was too low it said "Go LOWER!", leading me in the wrong direction every time. On even-numbered attempts, the secret number was silently converted to a string before comparison, causing the hint logic to produce unpredictable results due to int-vs-string comparison. The scoring system was also erratic -- "Too High" guesses alternated between adding and subtracting 5 points depending on attempt parity, while "Too Low" always subtracted 5, so the score swung wildly without a clear pattern. The "Hard" difficulty used a range of 1-50, which is actually easier than "Normal" (1-100), and the info bar always said "between 1 and 100" regardless of difficulty. Finally, clicking "New Game" generated a new secret in the range 1-100 instead of using the selected difficulty range, and the attempt counter started at 1 instead of 0, costing the player an attempt on the very first game.

---

## 2. How did you use AI as a teammate?

I used Cursor (Copilot) as my primary AI tool throughout this project. I gave it context of both `app.py` and `logic_utils.py` and asked it to identify bugs, propose fixes, and generate tests.

**Correct suggestion:** The AI correctly identified that the hint messages in `check_guess` were swapped -- `"Go HIGHER!"` was displayed when the guess was too high, and `"Go LOWER!"` when too low. I verified this by reading the original code: when `guess > secret`, the function returned the emoji message `"📈 Go HIGHER!"`, which is the opposite of what the player should do. After applying the fix, I ran `pytest` and confirmed the test `test_guess_too_high` passed with `"LOWER"` in the message.

**Incorrect/misleading suggestion:** When I first asked the AI to analyze the scoring bug, it initially suggested the scoring logic was entirely correct and that the alternating +5/-5 for "Too High" was an intentional difficulty mechanic. This was misleading -- the asymmetry between "Too High" and "Too Low" scoring had no game-design justification and just confused players. I verified this was a bug by manually tracing through several game scenarios and confirming the score swung unpredictably. I overrode the AI's assessment and simplified scoring to a flat -5 for any wrong guess.

---

## 3. Debugging and testing your fixes

I decided a bug was fixed by using two layers of verification: automated pytest tests for the logic functions, and manual playtesting via the Streamlit app. If both agreed, the fix was solid.

For the swapped-hints bug, I wrote `test_guess_too_high` which calls `check_guess(60, 50)` and asserts the outcome is `"Too High"` and the message contains `"LOWER"`. Before the fix, this test would have failed because the message contained `"HIGHER"` instead. After fixing `check_guess` in `logic_utils.py`, all 22 tests passed, including this one. I also ran the Streamlit app and confirmed that guessing above the secret now correctly displays "Go LOWER!".

The AI helped generate the initial test structure. I used it to create tests for `parse_guess`, `get_range_for_difficulty`, and `update_score` -- covering edge cases like negative numbers, decimals, very large numbers, and empty strings. I reviewed each generated test to make sure the assertions matched the corrected logic, not the original buggy behavior.

---

## 4. What did you learn about Streamlit and state?

Streamlit works differently from a traditional web app. Every time the user interacts with a widget (clicks a button, types in a text field), Streamlit reruns the entire Python script from top to bottom. This means any regular Python variable gets reset to its initial value on every interaction. To keep data alive across reruns -- like the secret number, the player's score, or the attempt counter -- you have to store it in `st.session_state`, which is a dictionary that Streamlit preserves between reruns. If you accidentally initialize a session state variable without checking `if "key" not in st.session_state` first, you will overwrite it every rerun and lose the player's progress. This is exactly what makes Streamlit state bugs so sneaky: the code looks correct line-by-line, but the rerun behavior changes everything.

---

## 5. Looking ahead: your developer habits

One habit I want to carry forward is writing targeted tests immediately after fixing a bug, before moving on to the next issue. In this project, writing `test_guess_too_high` right after fixing the swapped hints gave me instant confidence the fix was correct and would not regress. This "fix, then test, then move on" loop kept my debugging focused.

Next time I work with AI, I will be more skeptical of AI suggestions that say code is "working as intended." The scoring bug was a clear example where the AI initially defended broken logic as an intentional design choice. I learned to always trace through the code manually with concrete inputs before accepting an AI's analysis.

This project taught me that AI-generated code can look perfectly reasonable while hiding subtle bugs that only reveal themselves at runtime. The lesson is clear: never trust AI code without running it, testing it, and reading it critically yourself.
