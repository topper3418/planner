function note() {
    python main.py write "$@"
}

function notes() {
    python main.py read "$@"
}

alias test="pytest --log-cli-level=INFO"
