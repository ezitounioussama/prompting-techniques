"""The two prompts, plus the test set used to compare them.

Kept apart from the runner so the wording is easy to read and change — the whole
point of the exercise is that the wording is what changes the result.
"""

LABELS = ("Work", "Personal", "Spam")

# ---------------------------------------------------------------------------
# Zero-shot: instruction only, no examples.
# ---------------------------------------------------------------------------

ZERO_SHOT = """Classify the following email as Work, Personal, or Spam:

"{email}"
"""

# ---------------------------------------------------------------------------
# Few-shot: three worked examples, then the real one.
#
# The examples do two jobs at once, and both matter:
#   1. they show what the labels mean here
#   2. they show the OUTPUT FORMAT — "Category: <one word>" and nothing else
# The second job is usually the bigger win. The instruction never says "reply
# with one word", yet the pattern makes it obvious.
#
# The three examples are one per label, so no class is left unillustrated and
# none is over-represented.
# ---------------------------------------------------------------------------

FEW_SHOT = """Classify each email into one of the following categories: Work, Personal, or Spam.

Email: "Dinner at 8 tonight? I'll bring the wine."
Category: Personal

Email: "You have won a free iPhone! Click here to claim your prize."
Category: Spam

Email: "The Q2 financial report is due by end of day tomorrow."
Category: Work

Email: "{email}"
Category:"""


# The two emails from the exercise brief.
BRIEF_CASES = [
    {
        "email": "Don't forget the team meeting at 2 PM. Please bring your project updates.",
        "expected": "Work",
        "technique": "zero-shot",
    },
    {
        "email": "Are you free for lunch this weekend?",
        "expected": "Personal",
        "technique": "few-shot",
    },
]


# A wider set, so the comparison is a measurement rather than two anecdotes.
# Four per label, and the last four are deliberately ambiguous — the brief notes
# that zero-shot struggles on edge cases, and these are how that gets tested.
TEST_SET = [
    # --- clear Work ---
    {"email": "Don't forget the team meeting at 2 PM. Please bring your project updates.",
     "expected": "Work", "hard": False},
    {"email": "Please review the attached contract before Friday's client call.",
     "expected": "Work", "hard": False},
    {"email": "Reminder: submit your timesheet before the payroll cutoff.",
     "expected": "Work", "hard": False},
    {"email": "The deployment is scheduled for 6 PM. Standby for the release notes.",
     "expected": "Work", "hard": False},

    # --- clear Personal ---
    {"email": "Are you free for lunch this weekend?",
     "expected": "Personal", "hard": False},
    {"email": "Mum's birthday is on Sunday, are you bringing the cake or am I?",
     "expected": "Personal", "hard": False},
    {"email": "That film was terrible. Never letting you pick again.",
     "expected": "Personal", "hard": False},
    {"email": "Landed safely, the flat is lovely. Photos when I find wifi.",
     "expected": "Personal", "hard": False},

    # --- clear Spam ---
    {"email": "You have won a free iPhone! Click here to claim your prize.",
     "expected": "Spam", "hard": False},
    {"email": "URGENT: your account will be suspended. Verify your password now.",
     "expected": "Spam", "hard": False},
    {"email": "Hot singles in your area are waiting. Unsubscribe never.",
     "expected": "Spam", "hard": False},
    {"email": "Make $5000 a week from home. No experience needed!!!",
     "expected": "Spam", "hard": False},

    # --- ambiguous: the edge cases the brief warns about ---
    # Work vocabulary, but it is a colleague asking a social favour.
    {"email": "Can you cover my shift Saturday? I'll owe you a coffee.",
     "expected": "Personal", "hard": True},
    # Reads like marketing, but it is a genuine work invitation.
    {"email": "Congratulations! You've been selected to present at the annual conference. "
              "Confirm your slot with HR.",
     "expected": "Work", "hard": True},
    # Personal tone wrapped around a real business request.
    {"email": "Hey! Long time. Quick one - can you send over the invoice for last month?",
     "expected": "Work", "hard": True},
    # Looks like a real service notice, but it is a phishing attempt.
    {"email": "Your package could not be delivered. Pay the 1.99 customs fee at this link "
              "to reschedule.",
     "expected": "Spam", "hard": True},
]
