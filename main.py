from flask import Flask, request, jsonify
from modules.etl_controller import ETLController

app = Flask(__name__)


@app.route("/extract_data", methods=["POST"])
def data_extraction():
    """
    Data extraction endpoint
    """
    try:
        etl_controller = ETLController()
        raw_flights_data = etl_controller.extract_data()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    return (
        jsonify(
            {
                "status": "Data extracted successfully.",
                "data": raw_flights_data,
            }
        ),
        200,
    )


@app.route("/process-and-load-data", methods=["POST"])
def process_data_endpoint():
    """
    Data processing and loading endpoint.
    """
    try:
        etl_controller = ETLController()
        # Parse the JSON data from the request
        data = request.get_json()
        result = etl_controller.process_data(data)
        etl_controller.load_data(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    return (
        jsonify(
            {
                "status": "Data were processed and stored successfully in the "
                + "provided database"
            }
        ),
        200,
    )


@app.route("/run_pipeline", methods=["POST"])
def run_pipeline():
    """
    Main endpoint of app responsible for:
        - data extraction
        - data processing
        - store data in db
        - store processing results AWS
    """
    etl_controller = ETLController()
    etl_controller.run_etl_process()
    return jsonify({"status": "ETL process completed"}), 200


@app.route("/", methods=["POST"])
def is_online():
    """
    Endpoint to indicate that the app is online
    """
    return jsonify({"status": "App is running."}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
