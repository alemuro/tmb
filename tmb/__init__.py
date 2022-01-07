import requests
import json
import unittest
import os
from datetime import datetime

TMB_BASE_URL = "https://api.tmb.cat/v1"


class TMB():
    """ Class that gets generic data from TMB, like bus lines, bus stops, and so on"""

    def __init__(self, app_id, app_key):
        """ Initializes the class using the APP ID and APP KEY """
        self._app_id = app_id
        self._app_key = app_key

    def get_bus_lines(self):
        url = f"{TMB_BASE_URL}/transit/linies/bus?app_id={self._app_id}&app_key={self._app_key}"
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

    def get_metro_lines(self):
        url = f"{TMB_BASE_URL}/transit/linies/metro?app_id={self._app_id}&app_key={self._app_key}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        res_json = res.json()

        metro_lines = []

        for metro_line in res_json['features']:
            metro_lines.append({
                "code": metro_line['properties']['CODI_LINIA'],
                "name": metro_line['properties']['NOM_LINIA'],
                "description": f"{metro_line['properties']['ORIGEN_LINIA']} / {metro_line['properties']['DESTI_LINIA']}",
            })

        metro_lines.sort(key=lambda x:x['name'])
        return metro_lines

    def get_bus_stops(self, line):
        # Get bus lines
        url = f"{TMB_BASE_URL}/transit/linies/bus?app_id={self._app_id}&app_key={self._app_key}"
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
        url = f"{TMB_BASE_URL}/transit/linies/bus/{line_code}/parades?app_id={self._app_id}&app_key={self._app_key}"
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

        return bus_stops


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


class TMBTest(unittest.TestCase):
    def test_get_bus_lines(self):
        tmb = TMB(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        bus_lines = tmb.get_bus_lines()
        print(bus_lines)
        for line in bus_lines:
            assert "code" in line
            assert "name" in line
            assert "description" in line

    def test_get_metro_lines(self):
        tmb = TMB(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        metro_lines = tmb.get_metro_lines()
        print(metro_lines)
        for line in metro_lines:
            assert "code" in line
            assert "name" in line
            assert "description" in line

    def test_get_bus_stops(self):
        tmb = TMB(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        bus_stops = tmb.get_bus_stops("V25")
        print(bus_stops)
        for stop in bus_stops:
            assert "code" in stop
            assert "name" in stop
            assert "description" in stop


class IBusTest(unittest.TestCase):
    def test_get_stop_forecast(self):
        ibus = IBus(os.getenv('IBUS_ID'), os.getenv('IBUS_KEY'))
        forecast = ibus.get_stop_forecast('366', 'V21')
        assert forecast != None

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
