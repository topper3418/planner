from src import rest_server, config, db


if __name__ == "__main__":
    db.init_db()
    rest_server.run(port=config.SERVER_PORT, host="0.0.0.0", debug=True)
