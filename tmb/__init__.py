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

    def __get_url(self, path):
        url = f"{TMB_BASE_URL}/{path}?app_id={self._app_id}&app_key={self._app_key}"
        return url

    def get_stop_forecast(self, stop, line = ""):
        """ Get remaining minutes for next bus for a given stop """

        url = self.__get_url(f"ibus/stops/{stop}")
        if line != "":
            url = self.__get_url(f"ibus/lines/{line}/stops/{stop}")

        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()
        next_buses = res_json['data']['ibus']
        if len(next_buses) > 0:
            return next_buses
        return None

    def get_bus_lines(self):
        url = self.__get_url("transit/linies/bus")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()

        bus_lines = []

        for bus_line in res_json['features']:
            bus_lines.append({
                "code": bus_line['properties']['CODI_LINIA'],
                "name": bus_line['properties']['NOM_LINIA'],
                "description": f"{bus_line['properties']['ORIGEN_LINIA']} / {bus_line['properties']['DESTI_LINIA']}",
            })

        bus_lines.sort(key=lambda x:x['name'])
        return bus_lines

    def get_bus_stops(self, line):
        # Get bus lines
        url = self.__get_url("transit/linies/bus")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()

        line_code = -1
        for bus_line in res_json['features']:
            if bus_line['properties']['NOM_LINIA'] == line:
                line_code = bus_line['properties']['CODI_LINIA']
                break

        if line_code == -1:
            raise Exception("Invalid line!")

        # Get bus stops
        url = self.__get_url(f"transit/linies/bus/{line_code}/parades")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()

        bus_stops = []
        for stop in res_json['features']:
            bus_stops.append({
                "code": stop['properties']['CODI_PARADA'],
                "line": stop['properties']['NOM_LINIA'],
                "name": stop['properties']['NOM_PARADA'],
                "description": stop['properties']['ADRECA'],
            })

        bus_stops.sort(key=lambda x:x['code'])

        return bus_stops


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
        stops = ibus.get_stop_forecast('366', 'V21')
        assert len(stops) == 1
        assert stops != None
        for stop in stops:
            assert 'routeId' in stop
            assert 't-in-min' in stop
            assert 't-in-s' in stop
            assert 'text-ca' in stop

    def test_get_stop_all_lines_forecast(self):
        ibus = IBus(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        stops = ibus.get_stop_forecast('366')
        assert len(stops) == 2
        assert stops != None
        for stop in stops:
            assert 'line' in stop
            assert 'routeId' in stop
            assert 't-in-min' in stop
            assert 't-in-s' in stop
            assert 'text-ca' in stop

    def test_get_itineraries(self):
        origin = "41.3755204,2.1498870"
        planner = Planner(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        plans = planner.get_itineraries(origin, '41.3878951,2.1308587')
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
        assert 'overview' in plan
        assert 'description' in plan
        assert 'durationInMinutes' in plan
        assert 'durationInSeconds' in plan
        assert 'transitTime' in plan
        assert 'waitingTime' in plan
        assert 'walkDistance' in plan
        assert 'transfers' in plan

    def test_get_bus_lines(self):
        tmb = IBus(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        bus_lines = tmb.get_bus_lines()
        for line in bus_lines:
            assert "code" in line
            assert "name" in line
            assert "description" in line

    def test_get_bus_stops(self):
        tmb = IBus(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        bus_stops = tmb.get_bus_stops("V25")
        for stop in bus_stops:
            assert "code" in stop
            assert "name" in stop
            assert "description" in stop
