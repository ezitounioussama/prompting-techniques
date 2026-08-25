# Basic Prompting Techniques — Zero-Shot vs Few-Shot

Email classification (Work / Personal / Spam) with two prompting techniques, run against a local
model so the comparison is measured rather than described.

> **[RESULTS.md](RESULTS.md) — the full measured comparison.** Accuracy, output-format counts,
> and the two bugs found while building it.

| | |
|---|---|
| Model | `llama3.2:3b` via local Ollama |
| Temperature | `0.0` — reruns reproduce the numbers |
| Dependencies | **none** — standard library only |

## Files

| File | Contents |
|---|---|
| **[`RESULTS.md`](RESULTS.md)** | **All measured results — start here** |
| `prompts.py` | The two prompts and the 16-email test set |
| `run_prompts.py` | Runs both techniques and reports accuracy |
| `llm.py` | Minimal Ollama client (`urllib`, no packages) |
| `docs/output.txt` | Raw terminal log of the run |

## Running it

```bash
ollama serve            # if not already running
ollama pull llama3.2:3b

python3 run_prompts.py
```

## Headline result

| Technique | Overall | Clear (12) | Ambiguous (4) | Replies needing no parsing |
|---|---|---|---|---|
| Zero-shot | 62.5% | 58.3% | 75.0% | 0/16 |
| Few-shot | **93.8%** | **100.0%** | 75.0% | **16/16** |

## The two techniques

**Zero-shot** — instruction only, no examples:

```
Classify the following email as Work, Personal, or Spam:

"Don't forget the team meeting at 2 PM. Please bring your project updates."
```

Model replied `"I would classify this email as Work. The content of the email is related to a work
meeting..."` — right answer, wrapped in a paragraph.

**Few-shot** — three worked examples, then the real one:

```
Email: "Dinner at 8 tonight? I'll bring the wine."
Category: Personal
...
Email: "Are you free for lunch this weekend?"
Category:
```

Model replied `Personal`. Right answer, and nothing to parse.

## Three findings that go beyond the exercise notes

**The gap was on the clear emails, not the ambiguous ones** — 58.3% vs 100.0% on the easy 12, and a
dead 75%/75% tie on the 4 hard ones. The exercise notes predict the opposite. Zero-shot failed
*while explaining itself*: it called a free-iPhone giveaway "Personal" and a holiday message "Work".

**Examples fix the format, not the judgement.** Both techniques missed the same ambiguous email
(*"Hey! Long time. Quick one - can you send over the invoice for last month?"* → both said
Personal, gold says Work). When a human labeller has to think, three examples will not settle it —
that needs sharper label definitions or chain-of-thought.

**A few-shot prompt is a completion, not a chat turn.** Sent through the normal chat path,
llama3.2:3b answered `"Here are the classifications:"` and re-listed the worked examples, never
reaching the real email. It needed Ollama's `raw: true` (bypass the chat template) plus a stop
sequence to return `Personal`. Same prompt, same model — the technique was fine, the delivery was
wrong.

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

---

Author: **Oussama Ezitouni**
