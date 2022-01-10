from pandas.core.frame import DataFrame

# Missing value dictionary for preprocessing
MISSING_VALUE_TABLE = {
    "light_conditions": [-1],
    "special_conditions_at_site": [-1, 9],
    "road_surface_conditions": [-1, 9, 6, 7],
    "junction_control": [-1, 0, 9],
    "junction_detail": [99, -1],
    "time": [],
    "speed_limit": [-1, 660, 630],
}

categorical_attribs = [
    'speed_limit',
    'light_conditions',
    'junction_detail',
    'junction_control',
    'road_surface_conditions',
    'special_conditions_at_site',
    'accident_severity',
]

quantitive_attribs = [
    'time',
    'accident_count',
    'fatality_rate',
]

ID_TO_LIGHT_CONDITIONS = {
    1 : 'Daylight',
    4 : 'Darkness: street lights present and lit',
    5 : 'Darkness: street lights present but unlit',
    6 : 'Darkness: no street lighting',
    7 : 'Darkness: street lighting unknown',
}

ID_TO_JUNCTION_DETAIL = {
    0 : 'Not at or within 20 metres of junction',
    1 : 'Roundabout',
    2 : 'Mini roundabout',
    3 : 'T or staggered junction',
    5 : 'Slip road',
    6 : 'Crossroads',
    7 : 'Junction more than four arms (not RAB)',
    8 : 'Using private drive or entrance',
    9 : 'Other junction',
}

ID_TO_JUNCTION_CONTROL = {
    1 : 'Authorised person',
    2 : 'Automatic traffic signal',
    3 : 'Stop sign', 
    4 : 'Give way or uncontrolled',
}

ID_TO_ROAD_SURFACE_CONDITIONS = {
    1 : 'Dry',
    2 : 'Wet / Damp',
    3 : 'Snow',
    4 : 'Frost / Ice',
    5 : 'Flood (surface water over 3cm deep)',
}

ID_TO_SPECIAL_CONDITIONS_AT_SITE = {
    0 : 'None',
    1 : 'Auto traffic signal out',
    2 : 'Auto traffic signal partially defective',
    3 : 'Permanent road signing or marking defective or obscured',
    4 : 'Roadworks',
    5 : 'Road surface defective',
    6 : 'Oil or diesel',
    7 : 'Mud',
}

ID_TO_POLICE_FORCE_AREA = {
    1 : 'Metropolitan Police',
    3 : 'Cumbria',
    4 : 'Lancashire',
    5 : 'Merseyside',
    6 : 'Greater Manchester',
    7 : 'Cheshire',
    10: 'Northumbria',
    11: 'Durham',
    12: 'North Yorkshire',
    13: 'West Yorkshire',
    14: 'South Yorkshire',
    16: 'Humberside',
    17: 'Cleveland',
    20: 'West Midlands',
    21: 'Staffordshire',
    22: 'West Mercia',
    23: 'Warwickshire',
    30: 'Derbyshire',
    31: 'Nottinghamshire',
    32: 'Lincolnshire',
    33: 'Leicestershire',
    34: 'Northamptonshire',
    35: 'Cambridgeshire',
    36: 'Norfolk',
    37: 'Suffolk',
    40: 'Bedfordshire',
    41: 'Hertfordshire',
    42: 'Essex',
    43: 'Thames Valley',
    44: 'Hampshire',
    45: 'Surrey',
    46: 'Kent',
    47: 'Sussex',
    48: 'City of London',
    50: 'Devon and Cornwall',
    52: 'Avon and Somerset',
    53: 'Gloucestershire',
    54: 'Wiltshire',
    55: 'Dorset',
    60: 'North Wales',
    61: 'Gwent',
    62: 'South Wales',
    63: 'Dyfed-Powys',
}

# Based on this dataset:
# https://www.ons.gov.uk/peoplepopulationandcommunity/crimeandjustice/datasets/policeforceareadatatables
POPULATION_BY_POLICE_FORCE_AREA = {
    'Metropolitan Police': 8991600,
    'Cumbria':              499800,
    'Lancashire':          1515500,
    'Merseyside':          1434300,
    'Greater Manchester':  2848300,
    'Cheshire':            1069600,
    'Northumbria':         1470400,
    'Durham':               640600,
    'North Yorkshire':      831600,
    'West Yorkshire':      2345200,
    'South Yorkshire':     1415100,
    'Humberside':           934400,
    'Cleveland':            569800,
    'West Midlands':       2939900,
    'Staffordshire':       1139800,
    'West Mercia':         1298400,
    'Warwickshire':         583800,
    'Derbyshire':          1064000,
    'Nottinghamshire':     1170500,
    'Lincolnshire':         766300,
    'Leicestershire':      1107600,
    'Northamptonshire':     757200,
    'Cambridgeshire':       859800,
    'Norfolk':              914000,
    'Suffolk':              761200,
    'Bedfordshire':         682300,
    'Hertfordshire':       1195700,
    'Essex':               1856100,
    'Thames Valley':       2431900,
    'Hampshire':           1999100,
    'Surrey':              1199900,
    'Kent':                1868200,
    'Sussex':              1718200,
    'City of London':        10900,
    'Devon and Cornwall':  1785300,
    'Avon and Somerset':   1729500,
    'Gloucestershire':      640700,
    'Wiltshire':            727000,
    'Dorset':               776800,
    'North Wales':          703400,
    'Gwent':                598200,
    'South Wales':         1345300,
    'Dyfed-Powys':          522700,
}

