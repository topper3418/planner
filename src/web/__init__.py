import os
from flask import Flask, jsonify, render_template, request, Blueprint

from ..logging import get_logger
from ..settings import get_setting, write_setting
from ..db import init_db
from .api import api_bp

logger = get_logger(__name__)


rest_server = Flask(__name__)

logger.debug


@rest_server.route("/")
def index():
    return render_template("index.html")


rest_server.register_blueprint(api_bp)


if __name__ == "__main__":
    rest_server.run(debug=True)
