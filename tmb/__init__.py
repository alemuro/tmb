import requests
import json

TMB_BASE_URL = "https://api.tmb.cat/v1"

class IBus():
    """ Class that interacts with TMB iBus service """

    def __init__(self, app_id, app_key):
        """ Initializes the class using the APP ID and APP KEY """
        self._app_id = app_id
        self._app_key = app_key

    def get_stop_forecast(self, stop, line):
        """ Get remaining minutes for next bus for a given stop """
        url = f"{TMB_BASE_URL}/ibus/lines/{line}/stops/{stop}?app_id={self._app_id}&app_key={self._app_key}"
        res = requests.get(url)
        res.raise_for_status()
        res_json = res.json()
        next_buses = res_json['data']['ibus']
        if len(next_buses) > 0:
            next_bus = next_buses[0]
            return next_bus['t-in-min']
        return None