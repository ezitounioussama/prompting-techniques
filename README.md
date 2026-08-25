# Basic Prompting Techniques — Zero-Shot vs Few-Shot

Classify 16 emails as Work / Personal / Spam, twice: once with an instruction only, once with
three worked examples in front of it. Running it against a local model at temperature 0 means the
comparison is measured rather than described — 62.5% for zero-shot against 93.8% for few-shot,
and reruns reproduce it.

The result that surprised me is where the gap sits. The exercise notes suggest few-shot helps most
on ambiguous input; the numbers say the opposite. On the four genuinely hard emails both
techniques tied at 75%. The whole gap was on the easy twelve — 58.3% against 100% — where
zero-shot failed *while explaining its reasoning*, calling a free-iPhone giveaway "Personal". What
examples reliably fix is the output format: 16/16 few-shot replies needed no parsing, against
0/16 for zero-shot.

`llama3.2:3b` via local Ollama, standard library only, no API key.

```bash
ollama serve && ollama pull llama3.2:3b
python3 run_prompts.py
```

## Also in this repo

- **[RESULTS.md](RESULTS.md)** — both prompts, all 16 classifications, the accuracy and format
  breakdowns, when to use which technique, and the two bugs found while building
- [`docs/output.txt`](docs/output.txt) — raw terminal log

---

Author: **Oussama Ezitouni**
