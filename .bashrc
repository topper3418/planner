source venv/bin/activate

alias planner="python cli.py"
alias nn="planner write"
alias cycle="planner cycle"
alias notes="planner read note"
alias actions="planner read action"
alias todos="planner read todo"
alias observations="planner read observation"
alias curiosities="planner read curiosity"

alias db="sqlite3 data/notes.db"
alias test="pytest --log-cli-level=INFO"
