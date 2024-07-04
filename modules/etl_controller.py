from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import os
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
from config.config import *


class ETLController:
    """
    ETL controller class
    """

    def __init__(self):
        self.windowStr = ""

    def extract_data(self) -> list:
        """
        Data extraction method.
        """
        # Check if ENV variables were provided
        if SCHIPHOL_API_APP_ID is None or SCHIPHOL_API_APP_KEY is None:
            errMsg = (
                "Some of the environment variables 'SCHIPHOL_API_APP_ID' and "
                + "'SCHIPHOL_API_APP_KEY' are not set."
            )
            logger.error(errMsg)
            raise Exception(errMsg)
        try:
            flights, self.windowStr = fetch_flights_data()
        except Exception as exc:
            logger.error(f"Error fetching data {exc}")
            return {}

        logger.info(f"Successfully fetched {len(flights)} raw data entries.")
        return flights

    def process_data(self, raw_data: list) -> list:
        """
        Data processing method.
        """
        arrivals, departures = cleanup_flight_data(raw_data)
        df_arrivals, df_destinations_arr = analyse_arrivals(arrivals)
        df_departures, df_destinations_dep = analyse_departures(departures)

        try:
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
                "facilities": find_busiest_facilities(
                    df_arrivals, df_departures, 10, self.windowStr
                ),
            }
        except Exception as exc:
            logger.error(f"Couldn't process data due to error: {exc}")
            raise Exception(f"Couldn't process data due to error: {exc}")

        logger.info(f"Successfully processed data.")
        return {
            "df_arrivals": df_arrivals,
            "df_destinations_arr": df_destinations_arr,
            "df_departures": df_departures,
            "df_destinations_dep": df_destinations_dep,
            "reports": processing_results,
        }

    def load_data(self, processed_data: list):
        """
        Store data in database
        """

        if (
            DB_PREFIX is None
            or DB_IP_ADDRESS is None
            or DB_USER is None
            or DB_PASSWORD is None
            or DB_NAME is None
        ):
            errMsg = (
                "Some of the environment variables 'DB_PREFIX', 'DB_IP_ADDRESS',"
                + "'DB_USER', 'DB_PASSWORD' and 'DB_NAME' are not set."
            )
            logger.error(errMsg)
            raise Exception(errMsg)

        # Ensure tables are created
        self.engine = create_engine(DB_URI)
        create_tables()

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
        for key, df in facilities.items():
            if df.empty:
                logger.info(f"Dataframe for {key} is empty.")
            store_to_s3(key, df, self.windowStr)

    def run_etl_process(self):
        """
        Method that executes the ETL pipeline.
        """
        logger.info("Extracting data")
        raw_flights_data = self.extract_data()

        logger.info("Data processing")
        processing_results = self.process_data(raw_flights_data)

        if processing_results is not None:
            logger.info("Data storing")
            self.load_data(processing_results)

            logger.info("Uploading to AWS")
            self.aws_upload(processing_results["reports"]["facilities"])
        else:
            logger.info("Processing failed due to error. Skipping data storing.")

        logger.info("Success")


# Example usage in main.py
if __name__ == "__main__":
    etl_controller = ETLController()
    etl_controller.run_etl_process()
