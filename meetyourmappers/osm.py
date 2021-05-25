'''OSM specific classes'''

from datetime import datetime, timezone
import csv
from io import StringIO

import iso8601
import requests
from flask import session

from meetyourmappers import app

class MapperMetrics:
    '''Collect metrics of mappers from a CSV file'''

    def __init__(self):
        self._users = {}
        self._totals = {
            "node": 0,
            "way": 0,
            "relation": 0,
            "first": datetime.now(timezone.utc),
            "last": datetime.now(timezone.utc)}
        self._csv = None


    def retrieve_bbox(self, north, south, east, west):
        '''Retrieve data from overpass using a bounding box'''
        overpass_query = app.config["OVERPASS_BOX_QUERY"].format(n=north, s=south, e=east, w=west)
        print("sending to overpass: {}".format(overpass_query))
        resp = requests.post(
            app.config["OVERPASS_API_URL"] if session["use_altserver"] else \
            app.config["ALT_OVERPASS_API_URL"],
            data=overpass_query)
        self._csv = resp.text


    def retrieve_relation(self, relation_id):
        '''Retrieve data from overpass using a relation id'''
        overpass_query = app.config["OVERPASS_REL_QUERY"].format(relation_id)
        print("sending to overpass: {}".format(overpass_query))
        resp = requests.post(
            app.config["OVERPASS_API_URL"] if session["use_altserver"] else \
            app.config["ALT_OVERPASS_API_URL"],
            data=overpass_query)
        self._csv = resp.text


    def parse(self):
        '''Parse the CSV returned from Overpass'''
        reader = csv.reader(StringIO(self._csv))
        map(self._store_row, reader)


    def _store_row(self, row):
        print(row)
        [osm_type, osm_id, user, uid, version, tstamp] = row
        tstamp = iso8601.parse_date(tstamp)
        if user in self._users.keys():
            # user exists
            existing_user = self._users[user]
            existing_user[osm_type] += 1
            existing_user["first"] = min(existing_user["first"], tstamp)
            existing_user["last"] = max(existing_user["last"], tstamp)
        else:
            # user needs to be added to dict
            self._users[user] = {
                "node": 0,
                "way": 0,
                "relation": 0,
                "first": tstamp,
                "last": tstamp}
            self._users[user][osm_type] += 1
            print("adding user {}".format(user))

    @property
    def users(self):
        '''Return the users dict'''
        return self._users

    @property
    def totals(self):
        '''Return the totals dict'''
        return self._totals

    @property
    def csv(self):
        '''Returns the raw CSV we got from Overpass'''
        return self._csv
    