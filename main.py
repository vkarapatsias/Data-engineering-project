from modules.etl_controller import ETLController


def run_pipeline():
    """
    Run the full ETL pipeline.
    """
    etl_controller = ETLController()
    etl_controller.run_etl_process()


if __name__ == "__main__":
    run_pipeline()
