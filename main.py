from flask import Flask, jsonify
from modules.etl_controller import ETLController

app = Flask(__name__)


@app.route('/run_etl', methods=['POST'])
def run_etl():
    """
    Main endpoint of app
    """
    etl_controller = ETLController()
    etl_controller.run_etl_process()
    return jsonify({"status": "ETL process started"}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
