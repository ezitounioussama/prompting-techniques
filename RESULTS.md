# Results — Zero-Shot vs Few-Shot Prompting

Captured from a real run. Model `qwen3:8b` on local Ollama (thinking disabled), `temperature=0` so a rerun
reproduces these numbers. Raw log: [`docs/output.txt`](docs/output.txt).

```bash
ollama serve
python3 run_prompts.py
```

---

## Part 1 — the two prompts from the exercise

### Zero-shot

Prompt:

```
Classify the following email as Work, Personal, or Spam:

"Don't forget the team meeting at 2 PM. Please bring your project updates."
```

Reply:

```
I would classify this email as Work. The content of the email is related to a work meeting
and a specific task (project updates), which suggests that it is a professional communication
from a colleague or supervisor.
```

Parsed label **Work** — matches the expected output. Note the reply is a paragraph, not a label.

### Few-shot

Prompt:

```
Classify each email into one of the following categories: Work, Personal, or Spam.

Email: "Dinner at 8 tonight? I'll bring the wine."
Category: Personal

Email: "You have won a free iPhone! Click here to claim your prize."
Category: Spam

Email: "The Q2 financial report is due by end of day tomorrow."
Category: Work

Email: "Are you free for lunch this weekend?"
Category:
```

Reply:

```
Personal
```

**Personal** — matches, and the reply is already exactly a label. Nothing to parse.

---

## Part 2 — the same 16 emails through both techniques

12 clear emails (4 per label) and 4 deliberately ambiguous ones.

```
      expected  zero-shot   few-shot    email
       Work      Work    ok  Work    ok  Don't forget the team meeting at 2 PM...
       Work      Work    ok  Work    ok  Please review the attached contract...
       Work      Work    ok  Work    ok  Reminder: submit your timesheet...
       Work      Work    ok  Work    ok  The deployment is scheduled for 6 PM...
       Personal  Work    MISS Personalok  Are you free for lunch this weekend?
       Personal  Personalok  Personalok  Mum's birthday is on Sunday...
       Personal  Work    MISS Personalok  That film was terrible. Never letting you pick again.
       Personal  Work    MISS Personalok  Landed safely, the flat is lovely...
       Spam      PersonalMISS Spam    ok  You have won a free iPhone!...
       Spam      Spam    ok  Spam    ok  URGENT: your account will be suspended...
       Spam      Spam    ok  Spam    ok  Hot singles in your area...
       Spam      PersonalMISS Spam    ok  Make $5000 a week from home...
  HARD Personal  Personalok  Personalok  Can you cover my shift Saturday?...
  HARD Work      Work    ok  Work    ok  Congratulations! You've been selected to present...
  HARD Work      PersonalMISS PersonalMISS Hey! Long time. Quick one - can you send over the invoice...
  HARD Spam      Spam    ok  Spam    ok  Your package could not be delivered. Pay the 1.99 fee...
```

### Accuracy

| Technique | Overall | Clear (12) | Ambiguous (4) |
|---|---|---|---|
| Zero-shot | **68.8%** (11/16) | 66.7% | 75.0% |
| Few-shot | **93.8%** (15/16) | **100.0%** | 75.0% |

### Output format

| Technique | Replies that were already just a label |
|---|---|
| Zero-shot | **1 / 16** |
| Few-shot | **16 / 16** |

---

## What the numbers actually say

### 1. Few-shot won overall — 93.8% against 68.8%

### 2. The gap is on the CLEAR emails, not the ambiguous ones

This is the opposite of what the exercise notes predict.

| | zero-shot | few-shot | gap |
|---|---|---|---|
| Clear | 66.7% | 100.0% | **+33.3** |
| Ambiguous | 75.0% | 75.0% | **0.0** |

Zero-shot did not fail because the emails were hard. It failed on easy ones while explaining
itself in prose: it labelled *"You have won a free iPhone! Click here to claim your prize."* as
**Personal**, and *"Landed safely, the flat is lovely. Photos when I find wifi."* as **Work**. A
3B model has the knowledge — what it lacks is a fixed target to answer into.

### 3. On the ambiguous emails the two techniques tied at 75%

Examples fix the **format**, not the **judgement**. Both techniques missed the same email:

> "Hey! Long time. Quick one - can you send over the invoice for last month?"

Both answered **Personal**; the gold label says **Work**. That one is genuinely arguable, and
that is the real lesson about edge cases: when a human labeller has to stop and think, three
examples will not settle it. That needs a sharper definition of the labels (does "work" mean the
topic or the relationship?) or chain-of-thought so the model reasons before answering.

### 4. Format was the most reliable win, and it was total

Zero-shot answered in a sentence every single time, so all 16 replies needed regex parsing.
Few-shot returned a bare label all 16 times. The few-shot prompt never says *"answer in one word"* —
the three examples make the shape obvious. That is what makes it safe to consume from code:

```python
label = ask(prompt)          # few-shot: "Work"
label = parse(ask(prompt))   # zero-shot: "I would classify this email as Work. The content..."
```

### 5. A few-shot prompt is a completion, not a chat turn

Found while building this, and the biggest practical gotcha. Sent through the normal chat path,
The model replied:

```
Here are the classifications:

1. "Dinner at 8 tonight? I'll bring the wine."
Category: Personal

2. "You have won a free iPhone! Click here to claim your prize."
Category: Spam
...
```

It re-listed the worked examples and never reached the real email. Two fixes were needed:

- **`raw: true`** in the Ollama request, which bypasses the chat template so the model *continues*
  the pattern instead of talking about it
- **a stop sequence** (`["\nEmail:", "\n"]`) so it halts after the one label

Same prompt, same model, same temperature — the output went from a wall of re-listed examples to
`Personal`. The technique was never wrong; the delivery was.

---

## Two bugs found and fixed while building this

Both are recorded because in each case the code ran fine and produced a plausible, wrong answer.

**1. Few-shot scored 0% on Work.** The label extractor took the *first* label it found in the
reply. When the model echoed the worked examples, the first label it printed was example 1's
(`Personal`), so every Work email came back Personal. Fixed by parsing after the final
`Category:` and taking the *last* label.

**2. The written conclusions contradicted the measurement.** A first draft asserted "both
techniques handle clear emails well" and "the gap shows up on ambiguous emails". The run then
measured 66.7% vs 100.0% on clear emails and a dead tie on the ambiguous ones. The conclusion
section is now generated from the numbers, so the prose cannot drift from the result.

---

Author: **Oussama Ezitouni**

---

## When to use which

| | Zero-shot | Few-shot |
|---|---|---|
| Prompt cost | Cheapest — no examples | Larger, examples in every call |
| Setup | Nothing to prepare | Need labelled examples |
| Output format | Prose, needs parsing | Follows the example format |
| Custom or fuzzy labels | Weak — the model guesses your meaning | Strong — examples define the labels |
| Genuinely ambiguous input | Unreliable | Also unreliable |
| Best for | One-off questions, exploring, no labelled data | Anything consumed by code, or domain-specific labels |

Examples should be short, one per label so no class is over-represented, and diverse enough to
show the boundaries rather than three variations of the same email.
