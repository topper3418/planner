from src import rest_server, config, db, init_settings_db


if __name__ == "__main__":
    init_settings_db()
    db.init_db()
    rest_server.run(port=config.SERVER_PORT, host="0.0.0.0", debug=True)
