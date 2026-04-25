# Zone boundaries for coordinate-based lookup
ZONE_BOUNDARIES = {
    'zone1_arid': {
        'lat': (23.0, 30.5),
        'lon': (68.0, 76.5),
        'description': 'Arid and Semi-arid'
    },
    'zone2_coastal_west': {
        'lat': (8.0, 21.0),
        'lon': (72.0, 78.0),
        'description': 'Tropical Coastal West'
    },
    'zone3_coastal_east': {
        'lat': (8.0, 22.0),
        'lon': (78.0, 88.0),
        'description': 'Tropical Coastal East'
    },
    'zone4_deccan': {
        'lat': (14.0, 22.0),
        'lon': (74.0, 82.0),
        'description': 'Tropical Interior Deccan'
    },
    'zone5_north': {
        'lat': (22.0, 32.0),
        'lon': (74.0, 90.0),
        'description': 'Humid Subtropical North'
    },
    'zone6_highland': {
        'lat': (29.0, 36.0),
        'lon': (74.0, 82.0),
        'description': 'Highland and Alpine'
    }
}

# 25 cities with zone, coordinates, altitude
CITY_DATA = {
    # Zone 1 — Arid
    'Jaisalmer':  {'zone': 'zone1_arid', 'lat': 26.9, 'lon': 70.9, 'alt': 225},
    'Jodhpur':    {'zone': 'zone1_arid', 'lat': 26.3, 'lon': 73.0, 'alt': 231},
    'Bikaner':    {'zone': 'zone1_arid', 'lat': 28.0, 'lon': 73.3, 'alt': 234},
    'Ahmedabad':  {'zone': 'zone1_arid', 'lat': 23.0, 'lon': 72.6, 'alt': 53},

    # Zone 2 — Coastal West
    'Mumbai':     {'zone': 'zone2_coastal_west', 'lat': 19.1, 'lon': 72.9, 'alt': 14},
    'Goa':        {'zone': 'zone2_coastal_west', 'lat': 15.5, 'lon': 73.8, 'alt': 7},
    'Kochi':      {'zone': 'zone2_coastal_west', 'lat': 9.9,  'lon': 76.3, 'alt': 3},
    'Mangalore':  {'zone': 'zone2_coastal_west', 'lat': 12.9, 'lon': 74.9, 'alt': 22},

    # Zone 3 — Coastal East
    'Chennai':    {'zone': 'zone3_coastal_east', 'lat': 13.1, 'lon': 80.3, 'alt': 6},
    'Visakhapatnam': {'zone': 'zone3_coastal_east', 'lat': 17.7, 'lon': 83.3, 'alt': 45},
    'Bhubaneswar':{'zone': 'zone3_coastal_east', 'lat': 20.3, 'lon': 85.8, 'alt': 45},
    'Kolkata':    {'zone': 'zone3_coastal_east', 'lat': 22.6, 'lon': 88.4, 'alt': 9},

    # Zone 4 — Deccan
    'Bangalore':  {'zone': 'zone4_deccan', 'lat': 12.9, 'lon': 77.6, 'alt': 920},
    'Hyderabad':  {'zone': 'zone4_deccan', 'lat': 17.4, 'lon': 78.5, 'alt': 542},
    'Pune':       {'zone': 'zone4_deccan', 'lat': 18.5, 'lon': 73.9, 'alt': 560},
    'Nagpur':     {'zone': 'zone4_deccan', 'lat': 21.1, 'lon': 79.1, 'alt': 310},
    'Bhopal':     {'zone': 'zone4_deccan', 'lat': 23.3, 'lon': 77.4, 'alt': 523},

    # Zone 5 — North
    'Delhi':      {'zone': 'zone5_north', 'lat': 28.6, 'lon': 77.2, 'alt': 216},
    'Lucknow':    {'zone': 'zone5_north', 'lat': 26.8, 'lon': 80.9, 'alt': 123},
    'Jaipur':     {'zone': 'zone5_north', 'lat': 26.9, 'lon': 75.8, 'alt': 431},
    'Patna':      {'zone': 'zone5_north', 'lat': 25.6, 'lon': 85.1, 'alt': 53},
    'Indore':     {'zone': 'zone5_north', 'lat': 22.7, 'lon': 75.9, 'alt': 553},

    # Zone 6 — Highland
    'Shimla':     {'zone': 'zone6_highland', 'lat': 31.1, 'lon': 77.2, 'alt': 2200},
    'Leh':        {'zone': 'zone6_highland', 'lat': 34.2, 'lon': 77.6, 'alt': 3524},
    'Dehradun':   {'zone': 'zone6_highland', 'lat': 30.3, 'lon': 78.0, 'alt': 640},
}


def get_zone_from_coordinates(lat, lon):
    """For unknown cities — find zone from coordinates"""
    for zone, bounds in ZONE_BOUNDARIES.items():
        if (bounds['lat'][0] <= lat <= bounds['lat'][1] and
                bounds['lon'][0] <= lon <= bounds['lon'][1]):
            return zone
    return None  # outside India or unrecognized


def get_city_info(city_name):
    """For known cities — get zone and coordinates directly"""
    return CITY_DATA.get(city_name, None)



# """
# ZONE_BOUNDARIES       → lat/lon limits of each zone
#                         used for unknown cities

# CITY_DATA             → 25 cities with zone, lat, 
#                         lon, altitude hardcoded
#                         used in setup.py

# get_zone_from_coordinates() → unknown city comes in
#                               find its zone from lat/lon

# get_city_info()       → known city comes in
#                         return its zone + coordinates
# """