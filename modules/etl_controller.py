from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
import sys

sys.path.append(str(Path.cwd()) + "/modules")
sys.path.append(str(Path.cwd()) + "/config")

from data_processing import (
    cleanup_flight_data,
    analyse_arrivals,
    analyse_departures,
    filter_dataframe,
    find_most_popular_destinations,
    find_busiest_facilities,
)

from data_fetching import fetch_flights_data
from database_handler import create_tables
from aws_handler import store_to_s3

from config.logging_config import logger
from config.config import DB_URI


class ETLController:
    """
    ETL controller class
    """

    def __init__(self):
        self.engine = create_engine(DB_URI)
        create_tables()  # Ensure tables are created
        self.windowStr = ""

    def extract_data(self) -> list:
        """
        Data extraction method.
        """
        flights, self.windowStr = fetch_flights_data()
        return flights

    def process_data(self, raw_data: list) -> list:
        """
        Data processing method.
        """
        arrivals, departures = cleanup_flight_data(raw_data)
        df_arrivals, df_destinations_arr = analyse_arrivals(arrivals)
        df_departures, df_destinations_dep = analyse_departures(departures)

        processing_results = {
            "arrivals": {
                "most_landed": filter_dataframe(
                    df_arrivals, "state", "LND", "airline", 5
                ),
                "most_diverted": filter_dataframe(
                    df_arrivals, "state", "DIV", "airline", 5
                ),
                "most_popular_destinations": find_most_popular_destinations(
                    df_destinations_arr, 10
                ),
            },
            "departures": {
                "most_delayed": filter_dataframe(
                    df_departures, "state", "DEL", "airline", 5
                ),
                "most_canceled": filter_dataframe(
                    df_departures, "state", "CNX", "airline", 5
                ),
                "most_popular_destinations": find_most_popular_destinations(
                    df_destinations_dep, 10
                ),
            },
            "facilities": find_busiest_facilities(df_arrivals, df_departures, 10)
        }

        return {
            "df_arrivals": df_arrivals,
            "df_destinations_arr": df_destinations_arr,
            "df_departures": df_departures,
            "df_destinations_dep": df_destinations_dep,
            "reports": processing_results,
        }

    def load_data(self, processed_data: list):
        """
        Store data in databse
        """
        names_of_tables = [
            "ARRIVALS",
            "DESTINATIONS_ARRIVALS",
            "DEPARTURES",
            "DESTINATIONS_DEPARTURES",
        ]
        names_of_dfs = list(processed_data.keys())[:-1]  # all keys but the last

        for table_name, key in zip(names_of_tables, names_of_dfs):
            logger.info("Storing " + key + " in table " + table_name)
            try:
                processed_data[key].to_sql(
                    table_name, self.engine, if_exists="replace", index=False
                )
                logger.info(key + " successfully written to database")
            except SQLAlchemyError as e:
                logger.error(f"Error occurred: {e}")

    def aws_upload(self, facilities: dict):
        """
        Method to store the generated reports in AWS
        """
        for key, value in facilities.items():
            a=1
            store_to_s3(key, value, self.windowStr)

    def run_etl_process(self):
        """
        Method that executes the ETL pipeline.
        """
        logger.info("Extracting data")
        raw_flights_data = self.extract_data()

        logger.info("Data processing")
        processing_results = self.process_data(raw_flights_data)

        logger.info("Data storing")
        self.load_data(processing_results)

        logger.info("Uploading to AWS")
        self.aws_upload(processing_results["reports"]["facilities"])

        logger.info("Success")


# Example usage in main.py
if __name__ == "__main__":
    etl_controller = ETLController()
    etl_controller.run_etl_process()
