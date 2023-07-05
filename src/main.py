import os
import psycopg2
from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time


class Main:
    def __init__(self):
        self._hub_connection = None 
        self.HOST = os.environ['HOST']
        self.TOKEN = os.environ['TOKEN']
        self.TICKETS = os.environ['TICKETS']
        self.T_MAX = os.environ['T_MAX']
        self.T_MIN = os.environ['T_MIN']
        # Setup your database here
        self.DATABASE = "postgresql+psycopg2://postgres:LOG6802023@localhost/postgres"

    def __del__(self):
        if self._hub_connection != None:
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
        self._hub_connection.on_error(lambda data: print(f"||| An exception was thrown closed: {data.error}"))

    def onSensorDataReceived(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            dp = float(data[0]["data"])
            self.send_temperature_to_fastapi(date, dp)
            self.analyzeDatapoint(date, dp)
        except Exception as err:
            print(err)

    def analyzeDatapoint(self, date, data):
        if float(data) >= float(self.T_MAX):
            self.sendActionToHvac(date, "TurnOnAc", self.TICKETS)
        elif float(data) <= float(self.T_MIN):
            self.sendActionToHvac(date, "TurnOnHeater", self.TICKETS)

    def sendActionToHvac(self, date, action, nbTick):
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
            pass
        except requests.exceptions.RequestException as e:
            print("Error while sending event to the database:", e)
            pass


if __name__ == "__main__":
    main = Main()
    main.start()
