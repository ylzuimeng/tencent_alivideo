# INPUTS

A PRD and plan have been provided to you. Read these to understand the task.

You've also been passed a file containing the last few commits.
Review these to understand what work has been done.

If these are no more tasks to complete, output <promise>NO More TASKS</promise>.


# EXPLORATION

Explore the repo and fill your context window with relevant information that will allow you to complete the task.

# EXECUTION

Complete the task.

If anything blocks your completion of the task, output <promise>ABORT</promise>.

# FEEDBACK LOOPS

Before committing, run the feedback loops:

- Check that the feature works by starting the dev server locally via `python app.py` and testing the relevant routes/APIs.
- `pytest` to run the tests (if test files exist)
- `python -m py_compile <file>` to verify syntax of changed Python files

# COMMIT

Make a git commit. The commit message must:

1. Start with `RALPH:` prefix
2. Include task completed + PRD reference
3. Key decisions made
4. Files changed
5. Blockers or notes for next iteration

Keep it concise.

# FINAL RULES

ONLY WORK ON A SINGLE TASK.