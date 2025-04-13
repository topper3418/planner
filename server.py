from src import rest_server, config


if __name__ == "__main__":
   rest_server.run(port=config.REST_SERVER_PORT, host='0.0.0.0')
