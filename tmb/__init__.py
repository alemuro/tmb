import requests
import json
import unittest
import os
from datetime import datetime

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
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()
        next_buses = res_json['data']['ibus']
        if len(next_buses) > 0:
            next_bus = next_buses[0]
            return next_bus['t-in-min']
        return None


class Planner():
    """ Class that interacts with TMB Planner service """

    def __init__(self, app_id, app_key):
        """ Initializes the class using the APP ID and APP KEY """
        self._app_id = app_id
        self._app_key = app_key

    def get_shortest_itinerary(self, from_coords, to_coords):
        """ Get shortest itinary from `from_coords` to `to_coords` """
        itineraries = self.get_itineraries(from_coords, to_coords)
        selected_itinerary = itineraries[0]
        for itinerary in itineraries:
            if itinerary['durationInMinutes'] < selected_itinerary['durationInMinutes']:
                selected_itinerary = itinerary

        return selected_itinerary

    def get_itineraries(self, from_coords, to_coords):
        """ Get list of itineraries to go from `from_coords` to `to_coords` """
        now = datetime.now()
        d = now.strftime("%m-%d-%Y")
        time = "06:00pm"
        time = now.strftime("%I:%M%p")
        arriveBy = "false"
        mode = "TRANSIT,WALK"
        url = f"{TMB_BASE_URL}/planner/plan?fromPlace={from_coords}&toPlace={to_coords}&date={d}&time={time}&arriveBy={arriveBy}&mode={mode}&app_id={self._app_id}&app_key={self._app_key}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()

        plans = []

        for it in res_json['plan']['itineraries']:
            overview = ""
            description = ""
            first = True
            for legs in it['legs']:
                if legs['mode'] == "WALK":
                    continue
                if first == False:
                    overview += ", "
                    description += ", "
                overview += legs['route']
                description += f"{legs['route']} ({legs['from']['name']} - {legs['to']['name']})"
                first = False

            durationMinutes = round(it['duration'] / 60)
            walkDistance = round(it['walkDistance'])

            plan = {
                'overview': overview,
                'description': description,
                'durationInMinutes': durationMinutes,
                'durationInSeconds': it['duration'],
                'transitTime': it['transitTime'],
                'waitingTime': it['waitingTime'],
                'walkDistance': walkDistance,
                'transfers': it['transfers'],
            }

            plans.append(plan)

        return plans


class IBusTest(unittest.TestCase):
    def test_get_stop_forecast(self):
        ibus = IBus(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        forecast = ibus.get_stop_forecast('366', 'V21')
        print(forecast)
        assert forecast != None

    def test_get_itineraries(self):
        origin = "41.3755204,2.1498870"
        planner = Planner(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        plans = planner.get_itineraries(origin, '41.3878951,2.1308587')
        print(plans)
        for plan in plans:
            assert 'overview' in plan
            assert 'description' in plan
            assert 'durationInMinutes' in plan
            assert 'durationInSeconds' in plan
            assert 'transitTime' in plan
            assert 'waitingTime' in plan
            assert 'walkDistance' in plan
            assert 'transfers' in plan

    def test_get_shortest_itinerary(self):
        origin = "41.3755204,2.1498870"
        planner = Planner(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        plan = planner.get_shortest_itinerary(origin, '41.3878951,2.1308587')
        print(plan)
        assert 'overview' in plan
        assert 'description' in plan
        assert 'durationInMinutes' in plan
        assert 'durationInSeconds' in plan
        assert 'transitTime' in plan
        assert 'waitingTime' in plan
        assert 'walkDistance' in plan
        assert 'transfers' in plan
