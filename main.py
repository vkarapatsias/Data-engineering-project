from flask import Flask, request, jsonify
from flasgger import Swagger
from modules.etl_controller import ETLController

app = Flask(__name__)
swagger = Swagger(app)


@app.route("/extract_data", methods=["POST"])
def data_extraction():
    """
    Data extraction endpoint
    ---
    tags:
      - ETL
    responses:
      200:
        description: Data extracted successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: Data extracted successfully.
            data:
              type: array
              items:
                type: object
      400:
        description: Error occurred during data extraction
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: Error message
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
    ---
    tags:
      - ETL
    parameters:
      - name: data
        in: body
        required: true
        schema:
          type: array
          items:
            type: object
    responses:
      200:
        description: Data processed and stored successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: Data were processed and stored successfully in the provided database
      400:
        description: Error occurred during data processing or storing
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: Error message
    """
    try:
        etl_controller = ETLController()
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
    Run the full ETL pipeline.
    ---
    tags:
      - ETL
    responses:
      200:
        description: ETL process completed successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: ETL process completed
    """
    etl_controller = ETLController()
    etl_controller.run_etl_process()
    return jsonify({"status": "ETL process completed"}), 200


@app.route("/", methods=["GET"])
def is_online():
    """
    Health check endpoint.
    ---
    tags:
      - Health Check
    responses:
      200:
        description: App is running
        schema:
          type: object
          properties:
            status:
              type: string
              example: App is running.
    """
    return jsonify({"status": "App is running."}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
