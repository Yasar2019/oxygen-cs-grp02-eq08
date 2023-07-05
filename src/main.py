import os
import json
import time
import logging
import psycopg2
from signalrcore.hub_connection_builder import HubConnectionBuilder
import requests


class Main:
    def __init__(self):
        self._hub_connection = None
        self.HOST = os.getenv("HOST", "http://localhost:5000")
        self.TOKEN = os.getenv("TOKEN")
        if self.TOKEN is None:
            raise ValueError("The TOKEN environment variable is not defined")
        self.TICKETS = os.getenv("TICKETS", "1")
        self.T_MAX = os.getenv("T_MAX", "30")
        self.T_MIN = os.getenv("T_MIN", "10")
        # Setup your database here
        self.DATABASE = "postgresql+psycopg2://postgres:LOG6802023@localhost/postgres"

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def setup(self):
        self.setSensorHub()

    def start(self):
        self.setup()
        self._hub_connection.start()

        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setSensorHub(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on("ReceiveSensorData", self.onSensorDataReceived)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def onSensorDataReceived(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            dp = float(data[0]["data"])
            # self.send_temperature_to_fastapi(date, dp)
            self.analyze_datapoint(date, dp)
        except Exception as err:
            print(err)

    def analyze_datapoint(self, date, data):
        if float(data) >= float(self.T_MAX):
            self.send_action_to_hvac(date, "TurnOnAc", self.TICKETS)
        elif float(data) <= float(self.T_MIN):
            self.send_action_to_hvac(date, "TurnOnHeater", self.TICKETS)

    def send_action_to_hvac(self, date, action, nbTick):
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{nbTick}")
        details = json.loads(r.text)
        print(details)

    def send_event_to_database(self, timestamp, event):
        try:
            connection = psycopg2.connect(self.DATABASE)
            cursor = connection.cursor()

            sql = "INSERT INTO events (timestamp, event) VALUES (%s, %s)"
            values = (timestamp, event)
            cursor.execute(sql, values)

            connection.commit()
            cursor.close()
            connection.close()

        except requests.exceptions.RequestException as e:
            print("Error while sending event to the database:", e)


if __name__ == "__main__":
    main = Main()
    main.start()
