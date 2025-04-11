function note() {
    python main.py write "$@"
}

function notes() {
    python main.py read "$@"
}

function test() {
    pytest --log-cli-level=INFO 
}
