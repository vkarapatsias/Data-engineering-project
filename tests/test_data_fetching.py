import unittest
from modules.data_fetching import fetch_flights_data, fetch_airline, fetch_destination


class TestSchipholDataFetcher(unittest.TestCase):

    def test_fetch_flights_data(self):
        flights = fetch_flights_data(window_hours=0.5)
        self.assertIsInstance(flights, list)
        self.assertGreater(len(flights), 0, "Expected non-empty list of flights")

    def test_fetch_airline(self):
        airline_data = fetch_airline("KLM")
        self.assertIsInstance(airline_data, dict)
        self.assertIn(
            "publicName", airline_data, "Expected 'publicName' in airline data"
        )

    def test_fetch_destination(self):
        destination_data = fetch_destination("AMS")
        self.assertIsInstance(destination_data, dict)
        self.assertIn("city", destination_data, "Expected 'city' in destination data")


if __name__ == "__main__":
    unittest.main()
