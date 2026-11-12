# Decision inventory (read-only)

You are judging, before any code is written, how many decisions an implementer of the requirement below must make
where the nearest repository code would lead them to the wrong answer.

Rules:
- Read only the repository folder given in your task. Do not open any other folder on this machine, do not search the
  web, and do not edit, build or run anything. Use Read, Grep and Glob (or read-only shell commands such as git log,
  git grep, sed -n inside that folder).
- Cite file:line for every claim. A claim you cannot cite is not a finding.

## What to list
Every decision an implementer must make for the requirement:
- where to compute, and where to keep the result (does a saved file, report, restart or second command read it?);
- which helper, idiom or identity to use (copy the sibling code or not; which key, unit, name);
- which caller contexts reach the code (inside a framework window, a handler, a late registration, an error path);
- which entry paths reach the promise (another command, a saved file, the base side of a comparison, a fast path that
  answers early, a second kind of the same object);
- intermediate steps that change a value before it is used;
- what happens next to every exception or failure: unknown, missing, failed, partial, older state, and an undo or
  cleanup that itself fails.

## Per decision, one row
| # | Decision | Nearest repo idiom or helper (file:line) and what it would decide | Right or wrong for the requirement (one concrete input where the two differ) | Kind | Fair route (the requirement's words, or a repo line, that make the right answer findable) |

Kinds: K1 misleading nearby idiom or helper (copying the nearest code gives the wrong answer; the right helper sits
far away); K2 caller-context branch (the same API behaves differently by caller state); K3 second path or shortcut
(a path that skips the shared site); K4 intermediate semantics (a step inside one site changes the value first);
K5 identity or timing (which object, at which moment); K6 exception neighbour (the state next to an exception or
failure is not the exception). Write "none" when the nearest code decides it right.

A decision is wrong-by-default only when a strong implementer who copies the nearest repo code, or follows the
obvious reading, gets a different observable result from the correct one on a fair input, and the correct answer is
findable from the requirement plus the repository.

## Result
- GREEN: 2 or more wrong-by-default decisions, of different kinds or on different paths, each with a fair route.
- AMBER: exactly 1.
- RED: 0 (the nearest repo code decides every decision right).

End with: the result, the wrong-by-default decisions in one line each (kind, file:line, separating input), and the
decisions you rated "none" in one line each. Write the report to the output path given in your task.
