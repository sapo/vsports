""" Implements the Vsports API. 
Version 1.0.0, January 2025
(c) SAPO, 2025

Init:

    MANDATORY
    - api_key: API key for vsports.
    
    OPTIONAL
    - base_url: Base URL for the vsports API.
    - redis_config: Dictionary containing Redis configuration {'host': str, 'port': int, 'db': int, 'ttl': int (optional)}.
    - timeout: Timeout for the requests.

Caching:
    - The module supports caching using Redis.
    - The cache is enabled by passing a redis_config dictionary to the constructor.
    - All methods accept a boolean usecache parameter that can be set to True to enable caching.
    - The cache key is generated using the endpoint and the parameters of the request.
    - The cache TTL is set to 300 seconds by default but can be configured in the redis_config dictionary.
    - Redis cache uses a "namespace" to avoid conflicts with other keys in the database.
        cache_key = f"vsports:{endpoint}:{json.dumps(params, sort_keys=True)}
    - Cache maybe accessed directly using the _get_cache and _set_cache methods but this is not recommended.

Sample usage:

import json
from vsports import VsportsAPI

MYTOKEN = "your_token_here"
redis_config = {
    "host": "localhost", 
    "port": 6379, 
    "db": 0,
    "ttl": 300}

vsports = VsportsAPI(MYTOKEN, redis_config=redis_config)
result  = vsports.events_by_date("2025-01-24", usecache=True)
if result:
    print(json.dumps(result, indent=2))

result = vsports.teams_by_tournament(118, usecache=True)
if result:
    for team in result:
        print(team['name'])

result = vsports.squads(6, usecache=True)
if result:
    players = [member for member in result["squad"] if member["type"] == "player"]
    for player in players:
        print(f'{player["first_name"]} {player["last_name"]}')

"""

import json
import requests
import redis


class VsportsAPI:
    """ Implements the Vsports API. """

    def __init__(self, api_key, base_url="https://extended.vsports.pt/api",
                 timeout=10, redis_config=None):
        """
        Initialize the VsportsAPI module.

        :param api_key: API key for vsports.
        :param base_url: Base URL for the vsports API.
        :param redis_config: Dictionary containing 
               Redis configuration {'host': str, 'port': int, 'db': int}.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

        if redis_config:
            self.redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
            )
            self.redis_client.ping()
            self.redis_ttl = redis_config.get("ttl", 300)
        else:
            self.redis_client = None

    def __del__(self):
        """Destructor to close Redis connection if it exists."""
        if self.redis_client:
            self.redis_client.close()

    def _get_cache(self, key):
        """ Get data from cache if it exists. """
        if self.redis_client:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)  # type: ignore
        return None

    def _set_cache(self, key, value):
        """ Set data in cache. """
        if self.redis_client:
            self.redis_client.setex(key, self.redis_ttl, json.dumps(value))

    def _request(self, endpoint, method="GET", params=None, **kwargs):
        """ Make a request to the API. but first check if the data is in cache.
            if it is not, make the request and store the data in cache. """
        usecache = kwargs.get("usecache", False)
        if not isinstance(usecache, bool):
            usecache = False

        if usecache and self.redis_client:
            cache_key = f"vsports:{endpoint}:{
                json.dumps(params, sort_keys=True)}"
            cached_response = self._get_cache(cache_key)
            if cached_response:
                return cached_response

        url = f"{self.base_url}/{endpoint}"
        response = requests.request(
            method, url, headers=self.headers, params=params, timeout=self.timeout)

        if response.status_code == 200:
            data = response.json()
            if usecache and self.redis_client:
                self._set_cache(cache_key, data)
            return data
        else:
            response.raise_for_status()

    def tournaments(self, tournament_id=None, **kwargs):
        """Returns the list of all active tournaments or 
           the data for a tournament identified by its ID."""
        if tournament_id:
            return self._request(f"tournaments/{tournament_id}", **kwargs)
        return self._request("tournaments", **kwargs)

    def teams(self, team_id, **kwargs):
        """Returns data for a team identified by its ID."""
        return self._request(f"teams/{team_id}", **kwargs)

    def teams_by_tournament(self, tournament_id, **kwargs):
        """Returns the teams associated with a tournament identified by its ID."""
        return self._request(f"teams/by/tournament/{tournament_id}", **kwargs)

    def events_by_date(self, start_date, end_date=None, page=None, page_size=None, **kwargs):
        """Returns a complete list of events or the data for an event identified by its ID."""
        if not end_date:
            end_date = start_date

        params = {k: v for k, v in
                  {"start_date": start_date, "end_date": end_date,
                   "page": page, "page_size": page_size}.items() if v is not None}

        return self._request("events", params=params, **kwargs)

    def events(self, event_id=None, **kwargs):
        """Returns a complete list of events or the data for an event identified by its ID."""
        if event_id:
            return self._request(f"events/{event_id}", **kwargs)
        return self._request("events", **kwargs)

    def events_detailed(self, event_id=None, **kwargs):
        """Returns a detailed list of events or the data for an event identified by its ID."""
        if event_id:
            return self._request(f"events/{event_id}/detailed", **kwargs)
        return self._request("events/detailed", **kwargs)

    def events_occurrences(self, event_id, **kwargs):
        """Returns the occurrences for one or more events identified by their IDs."""
        return self._request(f"events/{event_id}/occurrences", **kwargs)

    def events_by_tournament(self, tournament_id, **kwargs):
        """Returns the events associated with a tournament identified by its ID."""
        return self._request(f"events/by/tournament/{tournament_id}", **kwargs)

    def events_by_tournament_periods(self, tournament_id, **kwargs):
        """Returns the events associated with a 
           tournament identified by its ID, grouped by periods."""
        return self._request(f"events/by/tournament/{tournament_id}/periods", **kwargs)

    def events_by_tournament_detailed(self, tournament_id, **kwargs):
        """Returns the events associated with a 
           tournament identified by its ID, with detailed information."""
        return self._request(f"events/by/tournament/{tournament_id}/detailed", **kwargs)

    def persons(self, person_id, **kwargs):
        """Returns data for a person identified by its ID."""
        return self._request(f"persons/{person_id}", **kwargs)

    def squads(self, team_id, **kwargs):
        """Returns the squad for a team identified by its ID."""
        return self._request(f"squads/{team_id}", **kwargs)

    def squads_detailed(self, team_id, **kwargs):
        """Returns the squad for a team identified by its ID, with detailed information."""
        return self._request(f"squads/{team_id}/detailed", **kwargs)

    def squads_by_tournament(self, team_id, tournament_id, **kwargs):
        """Returns the squad for a team identified by its ID and 
           associated with a tournament identified by its ID."""
        return self._request(f"squads/{team_id}/by/tournament/{tournament_id}", **kwargs)

    def squads_by_tournament_detailed(self, team_id, tournament_id, **kwargs):
        """Returns the squad for a team identified by its ID and 
           associated with a tournament identified by its ID, with detailed information."""
        return self._request(f"squads/{team_id}/by/tournament/{tournament_id}/detailed", **kwargs)

    def standings_by_tournament(self, tournament_id, **kwargs):
        """Returns the standings for a tournament identified by its ID."""
        return self._request(f"standings/by/tournament/{tournament_id}", **kwargs)

    def standings_by_tournament_live(self, tournament_id, **kwargs):
        """Returns the live standings for a tournament identified by its ID."""
        return self._request(f"standings/by/tournament/{tournament_id}/live", **kwargs)

    def venues(self, venue_id, **kwargs):
        """Returns data for a venue identified by its ID."""
        return self._request(f"venues/{venue_id}", **kwargs)

    def venues_by_team(self, team_id, **kwargs):
        """Returns the venues associated with a team identified by its ID."""
        return self._request(f"venues/by/team/{team_id}", **kwargs)
