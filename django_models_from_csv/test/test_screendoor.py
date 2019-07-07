from unittest.mock import patch, Mock

from django.test import TestCase
import requests
from tablib import Dataset

from django_models_from_csv.utils.screendoor import ScreendoorImporter


LIST_FORMS = [
  {
    "id": 6076,
    "field_data": [
      {
        "id": "xyejrz01",
        "size": "medium",
        "type": "field",
        "label": "What's your email address?",
        "required": True,
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "gw0fisz8",
        "size": "small",
        "type": "field",
        "blind": False,
        "label": "Your first name",
        "required": False,
        "admin_only": False,
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "89i3s4r9",
        "type": "field",
        "blind": False,
        "label": "Your last name",
        "options": [
          {
            "label": "",
            "checked": False
          },
          {
            "label": "",
            "checked": False
          }
        ],
        "required": False,
        "admin_only": False,
        "field_type": "text",
        "include_blank_option": False,
        "hasDependentShortcuts": False
      },
      {
        "id": "zmfl6vor",
        "size": "medium",
        "type": "field",
        "label": "What city do you live in?",
        "required": False,
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "j74rigc6",
        "type": "field",
        "label": "Which county do you live in?",
        "value": "Alameda",
        "options": [
          {
            "label": "Alameda",
            "checked": False
          },
          {
            "label": "Alpine",
            "checked": False
          },
          {
            "label": "Amador",
            "checked": False
          },
          {
            "label": "Butte",
            "checked": False
          },
          {
            "label": "Calaveras",
            "checked": False
          },
          {
            "label": "Colusa",
            "checked": False
          },
          {
            "label": "Contra Costa",
            "checked": False
          },
          {
            "label": "Del Norte",
            "checked": False
          },
          {
            "label": "El Dorado",
            "checked": False
          },
          {
            "label": "Fresno",
            "checked": False
          },
          {
            "label": "Glenn",
            "checked": False
          },
          {
            "label": "Humboldt",
            "checked": False
          },
          {
            "label": "Imperial",
            "checked": False
          },
          {
            "label": "Inyo",
            "checked": False
          },
          {
            "label": "Kern",
            "checked": False
          },
          {
            "label": "Kings",
            "checked": False
          },
          {
            "label": "Lake",
            "checked": False
          },
          {
            "label": "Lassen",
            "checked": False
          },
          {
            "label": "Los Angeles",
            "checked": False
          },
          {
            "label": "Madera",
            "checked": False
          },
          {
            "label": "Marin",
            "checked": False
          },
          {
            "label": "Mariposa",
            "checked": False
          },
          {
            "label": "Mendocino",
            "checked": False
          },
          {
            "label": "Merced",
            "checked": False
          },
          {
            "label": "Modoc",
            "checked": False
          },
          {
            "label": "Mono",
            "checked": False
          },
          {
            "label": "Monterey",
            "checked": False
          },
          {
            "label": "Napa",
            "checked": False
          },
          {
            "label": "Nevada",
            "checked": False
          },
          {
            "label": "Orange",
            "checked": False
          },
          {
            "label": "Placer",
            "checked": False
          },
          {
            "label": "Plumas",
            "checked": False
          },
          {
            "label": "Riverside",
            "checked": False
          },
          {
            "label": "Sacramento",
            "checked": False
          },
          {
            "label": "San Benito",
            "checked": False
          },
          {
            "label": "San Bernardino",
            "checked": False
          },
          {
            "label": "San Diego",
            "checked": False
          },
          {
            "label": "San Francisco",
            "checked": False
          },
          {
            "label": "San Joaquin",
            "checked": False
          },
          {
            "label": "San Luis Obispo",
            "checked": False
          },
          {
            "label": "San Mateo",
            "checked": False
          },
          {
            "label": "Santa Barbara",
            "checked": False
          },
          {
            "label": "Santa Clara",
            "checked": False
          },
          {
            "label": "Santa Cruz",
            "checked": False
          },
          {
            "label": "Shasta",
            "checked": False
          },
          {
            "label": "Sierra",
            "checked": False
          },
          {
            "label": "Siskiyou",
            "checked": False
          },
          {
            "label": "Solano",
            "checked": False
          },
          {
            "label": "Sonoma",
            "checked": False
          },
          {
            "label": "Stanislaus",
            "checked": False
          },
          {
            "label": "Sutter",
            "checked": False
          },
          {
            "label": "Tehama",
            "checked": False
          },
          {
            "label": "Trinity",
            "checked": False
          },
          {
            "label": "Tulare",
            "checked": False
          },
          {
            "label": "Tuolumne",
            "checked": False
          },
          {
            "label": "Ventura",
            "checked": False
          },
          {
            "label": "Yolo",
            "checked": False
          },
          {
            "label": "Yuba",
            "checked": False
          },
          {
            "label": "Other",
            "checked": False
          }
        ],
        "required": False,
        "conditions": [],
        "field_type": "dropdown",
        "include_blank_option": False,
        "hasDependentShortcuts": False
      },
      {
        "id": "uhmrq5tt",
        "size": "medium",
        "type": "field",
        "label": "Please tell us where you live.",
        "required": False,
        "conditions": [
          {
            "value": "Other",
            "action": "show",
            "method": "eq",
            "response_field_id": "j74rigc6"
          }
        ],
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "qc3dnp53",
        "type": "field",
        "label": "Tell us about yourself.",
        "value": {
          "checked": []
        },
        "options": [
          {
            "label": "I am or was incarcerated in a California county jail",
            "checked": False
          },
          {
            "label": "I'm a family member of someone who is or was incarcerated",
            "checked": False
          },
          {
            "label": "I know someone who is or was incarcerated",
            "checked": False
          },
          {
            "label": "My client is someone who is or was incarcerated",
            "checked": False
          }
        ],
        "required": True,
        "field_type": "radio",
        "include_other_option": True,
        "hasDependentShortcuts": False
      },
      {
        "id": "ebylx5ma",
        "size": "medium",
        "type": "field",
        "label": "When did you spend time in the system?",
        "required": False,
        "conditions": [
          {
            "value": "I am or was incarcerated in a California county jail",
            "action": "show",
            "method": "eq",
            "response_field_id": "qc3dnp53"
          }
        ],
        "field_type": "text",
        "description": "",
        "hasDependentShortcuts": False
      },
      {
        "id": "7uijs8vk",
        "size": "medium",
        "type": "field",
        "label": "Please tell us where.",
        "required": False,
        "conditions": [
          {
            "action": "show",
            "method": "present",
            "response_field_id": "ebylx5ma"
          }
        ],
        "field_type": "text",
        "description": "Can you tell us the facility name, and city/state?",
        "hasDependentShortcuts": False
      },
      {
        "id": "om2nonpp",
        "type": "field",
        "label": "Is the person you're writing about currently incarcerated?",
        "value": {
          "checked": []
        },
        "options": [
          {
            "label": "Yes",
            "checked": False
          },
          {
            "label": "No",
            "checked": False
          }
        ],
        "required": False,
        "conditions": [
          {
            "value": "I am or was incarcerated in a California county jail",
            "action": "show",
            "method": "not",
            "response_field_id": "qc3dnp53"
          }
        ],
        "field_type": "radio",
        "hasDependentShortcuts": False
      },
      {
        "id": "272fofp6",
        "size": "medium",
        "type": "field",
        "label": "How much time is the person serving?",
        "required": False,
        "conditions": [
          {
            "value": "Yes",
            "action": "show",
            "method": "eq",
            "response_field_id": "om2nonpp"
          }
        ],
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "u2jm5r4y",
        "size": "medium",
        "type": "field",
        "label": "When was the person in the system?",
        "required": False,
        "conditions": [
          {
            "value": "No",
            "action": "show",
            "method": "eq",
            "response_field_id": "om2nonpp"
          }
        ],
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "f3hxvy5w",
        "size": "medium",
        "type": "field",
        "label": "Please tell us where.",
        "required": False,
        "conditions": [
          {
            "value": "Yes",
            "action": "show",
            "method": "eq",
            "response_field_id": "om2nonpp"
          }
        ],
        "field_type": "text",
        "description": "Can you tell us the facility name, and city/state?",
        "hasDependentShortcuts": False
      },
      {
        "id": "b2737g2k",
        "type": "field",
        "label": "Which of the following do you want to share about? Check as many boxes as you'd like.",
        "value": {
          "checked": []
        },
        "options": [
          {
            "label": "Crowding in jails",
            "checked": False
          },
          {
            "label": "Inmate treatment",
            "checked": False
          },
          {
            "label": "Access to resources in jails",
            "checked": False
          },
          {
            "label": "Something else",
            "checked": False
          }
        ],
        "required": False,
        "conditions": [],
        "field_type": "checkboxes",
        "description": "",
        "hasDependentShortcuts": False
      },
      {
        "id": "e7ysl3ph",
        "size": "medium",
        "type": "field",
        "label": "What do you want to share about crowding in California county jails?",
        "required": False,
        "conditions": [
          {
            "value": "Crowding in jails",
            "action": "show",
            "method": "contains",
            "response_field_id": "b2737g2k"
          }
        ],
        "field_type": "paragraph",
        "hasDependentShortcuts": False
      },
      {
        "id": "i9jwhanh",
        "size": "medium",
        "type": "field",
        "label": "What do you want to share about inmate treatment in California county jails?",
        "required": False,
        "conditions": [
          {
            "value": "Inmate treatment",
            "action": "show",
            "method": "contains",
            "response_field_id": "b2737g2k"
          }
        ],
        "field_type": "paragraph",
        "hasDependentShortcuts": False
      },
      {
        "id": "sf7vwnas",
        "size": "medium",
        "type": "field",
        "label": "What do you want to share about access to resources in California county jails?",
        "required": False,
        "conditions": [
          {
            "value": "Access to resources in jails",
            "action": "show",
            "method": "contains",
            "response_field_id": "b2737g2k"
          }
        ],
        "field_type": "paragraph",
        "hasDependentShortcuts": False
      },
      {
        "id": "720omdzq",
        "size": "medium",
        "type": "field",
        "label": "What do you want to share about California county jails?",
        "required": False,
        "conditions": [
          {
            "value": "Something else",
            "action": "show",
            "method": "contains",
            "response_field_id": "b2737g2k"
          }
        ],
        "field_type": "paragraph",
        "hasDependentShortcuts": False
      },
      {
        "id": "76bnr9v8",
        "type": "field",
        "label": "Do you have any documents, photos, recordings or files to share with us?",
        "required": False,
        "field_type": "file",
        "description": "Please attach any files here. ",
        "hasDependentShortcuts": False
      },
      {
        "id": "s6la0qv2",
        "size": "medium",
        "type": "field",
        "blind": False,
        "label": "Following up",
        "required": True,
        "admin_only": False,
        "conditions": [
          {
            "action": "show",
            "method": "eq",
            "response_field_id": "720omdzq"
          }
        ],
        "field_type": "section_break",
        "description": "",
        "hasDependentShortcuts": False
      },
      {
        "id": "ab9z0508",
        "type": "field",
        "label": "We may have follow-up questions for you. What's the best way to reach you?",
        "value": {
          "checked": []
        },
        "options": [
          {
            "label": "Phone",
            "checked": False
          },
          {
            "label": "Email",
            "checked": False
          },
          {
            "label": "Other",
            "checked": False
          },
          {
            "label": "Don't contact me",
            "checked": False
          }
        ],
        "required": False,
        "field_type": "checkboxes",
        "hasDependentShortcuts": False
      },
      {
        "id": "93za6j1k",
        "size": "medium",
        "type": "field",
        "label": "Please enter your phone number.",
        "required": False,
        "conditions": [
          {
            "value": "Phone",
            "action": "show",
            "method": "contains",
            "response_field_id": "ab9z0508"
          }
        ],
        "field_type": "text",
        "hasDependentShortcuts": False
      },
      {
        "id": "lkuuse2q",
        "size": "medium",
        "type": "field",
        "label": "Please enter your other contact information.",
        "required": False,
        "conditions": [
          {
            "value": "Other",
            "action": "show",
            "method": "contains",
            "response_field_id": "ab9z0508"
          }
        ],
        "field_type": "text",
        "hasDependentShortcuts": False
      }
    ]
  }
]

LIST_RESPONSES = [
  {
    "id": 2232054,
    "sequential_id": 5,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "kHXYrTJbtkdc",
    "submitted_at": "2019-02-12T23:13:27.871Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I know someone who is or was incarcerated"
        ],
        "other_checked": False
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "No"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": "decades ago",
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": None,
      "720omdzq": "Lorem ipsum dolor sit amet",
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-12T23:11:19.314Z",
    "updated_at": "2019-05-02T21:19:58.900Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Some County",
      "p-family"
    ],
    "responder_language": "en",
    "responder": {
      "name": "First",
      "email": "email@domain.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "embedded",
      "hostname": "www.propublica.org"
    }
  },
  {
    "id": 2232134,
    "sequential_id": 6,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "yp5MISp1OvUZ",
    "submitted_at": "2019-02-13T00:01:04.929Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "My client is someone who is or was incarcerated"
        ],
        "other_checked": False
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "No"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": "2016",
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-12T23:58:41.120Z",
    "updated_at": "2019-05-02T21:19:58.943Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-family",
      "p-lawyer",
      "t-medical issue"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Firstname",
      "email": "email@something.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "embedded",
      "hostname": "www.propublica.org"
    }
  },
  {
    "id": 2232203,
    "sequential_id": 7,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "mKMDIXLWsAaY",
    "submitted_at": "2019-02-13T01:02:07.552Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "County",
      "j74rigc6": "City",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I'm a family member of someone who is or was incarcerated"
        ],
        "other_checked": False
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "Yes"
        ]
      },
      "272fofp6": "presentence detention",
      "u2jm5r4y": None,
      "f3hxvy5w": "Main County Main Jail, City CA ",
      "b2737g2k": {
        "checked": [
          "Access to resources in jails",
          "Inmate treatment",
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T00:52:52.218Z",
    "updated_at": "2019-05-02T21:19:58.966Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-family",
      "Inmate treatment"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Firstname",
      "email": "email@something"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2232419,
    "sequential_id": 8,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "EtiEuWbnVYth",
    "submitted_at": "2019-02-13T03:45:05.005Z",
    "responses": {
      "xyejrz01": "differentfake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "2012 2013 2014 2015-2016 2017",
      "7uijs8vk": "Some county jail correctional center",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Crowding in jails",
          "Inmate treatment",
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T03:41:30.684Z",
    "updated_at": "2019-05-02T21:19:59.072Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated",
      "Overcrowding",
      "Resources",
      "t-mental health"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "name@domain.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2232472,
    "sequential_id": 9,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "JW75YHbLRPRn",
    "submitted_at": "2019-02-13T04:51:21.785Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "First",
      "89i3s4r9": "Last",
      "zmfl6vor": "Sacramento ",
      "j74rigc6": "Sacramento",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [],
        "other_text": "Worked at on the Project",
        "other_checked": True
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "No"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": None,
      "720omdzq": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T04:38:16.277Z",
    "updated_at": "2019-05-02T21:19:59.095Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Some County"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name ",
      "email": "namespace@domain.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "embedded",
      "hostname": "www.propublica.org"
    }
  },
  {
    "id": 2232518,
    "sequential_id": 10,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "lIVKLoUDo7jA",
    "submitted_at": "2019-02-13T06:14:27.513Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "Dec 2020 - April 2023",
      "7uijs8vk": "Another County Jail/ Prison, City ST",
      "om2nonpp": {
        "checked": [
          "Yes"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Access to resources in jails",
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "76bnr9v8": [
        {
          "id": "4_IX6SYNPtqK8nXv3q_XbCw2cuMGVL8z",
          "filename": "Tami_appeal_letter.docx"
        }
      ],
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email",
          "Phone"
        ]
      },
      "93za6j1k": "9999999999",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T05:40:52.046Z",
    "updated_at": "2019-05-02T21:19:59.182Z",
    "status": "For ProPublica",
    "labels": [
      "p-incarcerated",
      "c\u2013Ventura Co",
      "Resources",
      "t-medical issue"
    ],
    "responder_language": "en",
    "responder": {
      "name": "AB",
      "email": "something@something.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2232536,
    "sequential_id": 11,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "CftBCfGhTLU4",
    "submitted_at": "2019-02-13T06:21:40.594Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Mark",
      "89i3s4r9": "Olague",
      "zmfl6vor": "Hesperia ",
      "j74rigc6": "San Bernardino",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "My whole life from 21 to 40",
      "7uijs8vk": "Los Angeles, san Bernardino ",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Access to resources in jails",
          "Inmate treatment",
          "Crowding in jails",
          "Something else"
        ]
      },
      "e7ysl3ph": "Alot of people in county jail dont belong there. Majority is people on drugs. Why should tax payers  be held responsible. The probation dept has too much authority. \n\n",
      "i9jwhanh": None,
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T06:15:24.055Z",
    "updated_at": "2019-05-02T21:19:59.215Z",
    "status": "For ProPublica",
    "labels": [
      "p-incarcerated",
      "c\u2013San Bernardino Co"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Fake",
      "email": "fake@gmail.com "
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2232616,
    "sequential_id": 12,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "YEnmG12Yf4Eq",
    "submitted_at": "2019-02-13T08:57:18.367Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Elk Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "Summer 2017",
      "7uijs8vk": "Downtown Sacramento",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitl... ",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T08:47:29.406Z",
    "updated_at": "2019-05-02T21:19:59.277Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated",
      "Inmate treatment",
      "t-medical issue"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "name@nam.e"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2232676,
    "sequential_id": 13,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "Mizv6NRV5IYe",
    "submitted_at": "2019-02-13T12:00:38.740Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Carly",
      "89i3s4r9": "Sullivan",
      "zmfl6vor": "Sacramento",
      "j74rigc6": "Sacramento",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "2012 2013 2014 2017 2018 ",
      "7uijs8vk": "detention center in",
      "om2nonpp": {
        "checked": [
          "Yes"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": "Sacramento county main jail",
      "b2737g2k": {
        "checked": [
          "Crowding in jails",
          "Inmate treatment",
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit ",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit ",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Phone",
          "Email"
        ]
      },
      "93za6j1k": "19999999999",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T11:46:41.757Z",
    "updated_at": "2019-05-02T21:19:59.344Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated",
      "Overcrowding",
      "Resources",
      "Gripping story",
      "Flagged for Jason & Ryan"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "fa@k.e"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2232695,
    "sequential_id": 14,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "nfxFNKiQ4lpn",
    "submitted_at": "2019-02-13T12:12:00.361Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "November 4, 2010",
      "7uijs8vk": "Big County Main Jail",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elit I\u2019ve never Lorem ipsum dolor sit amet, consectetur adipiscing elit ",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T12:06:22.687Z",
    "updated_at": "2019-05-02T21:19:59.368Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "name@name.name"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2233133,
    "sequential_id": 15,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "pTu75ldaqsKU",
    "submitted_at": "2019-02-13T16:42:19.651Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "fake",
      "89i3s4r9": "fake",
      "zmfl6vor": "County ",
      "j74rigc6": "Placer",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "October-December 2017",
      "7uijs8vk": "South placer jail",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Access to resources in jails",
          "Crowding in jails"
        ]
      },
      "e7ysl3ph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit\u2019s Lorem ipsum dolor sit amet, consectetur adipiscing elit ",
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit \u2019s Lorem ipsum dolor sit amet, consectetur adipiscing elit\u2019t ",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T16:34:13.683Z",
    "updated_at": "2019-05-02T21:19:59.404Z",
    "status": "For ProPublica",
    "labels": [
      "p-incarcerated",
      "c\u2013Placer Co",
      "Overcrowding",
      "Resources",
      "Inmate treatment",
      "Flagged for Jason & Ryan",
      "t-medical issue"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Hi",
      "email": "email@domain.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2233184,
    "sequential_id": 16,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "Lo43XxLyWLJi",
    "submitted_at": "2019-02-13T17:27:55.536Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Los Cityname",
      "j74rigc6": "Los Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [],
        "other_text": "Lorem ipsum dolor sit amet, consectetur & adipiscing elit",
        "other_checked": True
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "No"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": "Myself",
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": None,
      "720omdzq": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Phone",
          "Email"
        ]
      },
      "93za6j1k": "9999999999",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T17:09:14.581Z",
    "updated_at": "2019-05-02T21:19:59.455Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Los Angeles Co"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "fak@e.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2233674,
    "sequential_id": 17,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "ftwxpOK9C6E2",
    "submitted_at": "2019-02-13T21:10:55.340Z",
    "responses": {
      "xyejrz01": "first.fake@email.org",
      "gw0fisz8": "first",
      "89i3s4r9": "Name",
      "zmfl6vor": "County",
      "j74rigc6": "San Bernardino",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "November 2018 to December 2018",
      "7uijs8vk": "Glen Helen Rehabilitation Center",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": None,
      "720omdzq": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Phone",
          "Email"
        ]
      },
      "93za6j1k": "6666666666",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-13T20:57:35.649Z",
    "updated_at": "2019-05-02T21:19:59.537Z",
    "status": "For ProPublica",
    "labels": [
      "p-incarcerated",
      "c\u2013San Bernardino Co"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "na.me@email.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2234047,
    "sequential_id": 18,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "DB2sSD7jNY13",
    "submitted_at": "2019-02-14T01:43:34.326Z",
    "responses": {
      "xyejrz01": "name.fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": None,
      "zmfl6vor": "Cityname ",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [],
        "other_text": "I was a nurse in alameda county jails ",
        "other_checked": True
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "No"
        ]
      },
      "272fofp6": None,
      "u2jm5r4y": "N/a",
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit ",
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T01:39:32.276Z",
    "updated_at": "2019-05-02T21:19:59.581Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013San Francisco Co",
      "Resources",
      "p-employee",
      "t-medical issue"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "name@another.domain"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "embedded",
      "hostname": "www.propublica.org"
    }
  },
  {
    "id": 2234103,
    "sequential_id": 19,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "qYdZrLTTu4aW",
    "submitted_at": "2019-02-14T02:40:32.893Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I'm a family member of someone who is or was incarcerated"
        ],
        "other_checked": False
      },
      "ebylx5ma": None,
      "7uijs8vk": None,
      "om2nonpp": {
        "checked": [
          "Yes"
        ]
      },
      "272fofp6": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "u2jm5r4y": None,
      "f3hxvy5w": "Sacramento County, sac. Ca",
      "b2737g2k": {
        "checked": [
          "Access to resources in jails",
          "Inmate treatment"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit 1/3  ....",
      "sf7vwnas": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Phone"
        ]
      },
      "93za6j1k": "777-888-9999",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T02:24:06.914Z",
    "updated_at": "2019-05-02T21:19:59.607Z",
    "status": "For ProPublica",
    "labels": [
      "p-family",
      "c\u2013Yolo Co",
      "Inmate treatment",
      "Flagged for Jason & Ryan",
      "t-mental health"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "hello@email.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2234228,
    "sequential_id": 20,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "0uaQPuuyqbBv",
    "submitted_at": "2019-02-14T04:21:27.594Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "KEVIN",
      "89i3s4r9": "CARTER",
      "zmfl6vor": "San Jacinto",
      "j74rigc6": "Riverside",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "January 2019",
      "7uijs8vk": "Southewest ,Banning .california",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Crowding in jails"
        ]
      },
      "e7ysl3ph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email",
          "Phone"
        ]
      },
      "93za6j1k": "9999999999",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T04:13:32.664Z",
    "updated_at": "2019-05-02T21:19:59.631Z",
    "status": "For ProPublica",
    "labels": [
      "p-incarcerated",
      "c\u2013Riverside Co",
      "Inmate treatment",
      "Flagged for Jason & Ryan"
    ],
    "responder_language": "en",
    "responder": {
      "name": "NAME",
      "email": "email@domain.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2238133,
    "sequential_id": 21,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "xsdXQr1zhHlo",
    "submitted_at": "2019-02-14T15:41:20.702Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "April 1861 to Oct 1865",
      "7uijs8vk": "A County (AAAC)",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Access to resources in jails"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Phone"
        ]
      },
      "93za6j1k": "999.888.4444",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T15:37:51.356Z",
    "updated_at": "2019-05-02T21:19:59.721Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "fake@email.domain "
    },
    "deleted_at": None,
    "submission_source": {
      "type": "embedded",
      "hostname": "www.propublica.org"
    }
  },
  {
    "id": 2238092,
    "sequential_id": 22,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "bOSRXYO6ZgA6",
    "submitted_at": "2019-02-14T15:51:12.939Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Jon",
      "89i3s4r9": "Inskeep",
      "zmfl6vor": "Elk Grove",
      "j74rigc6": "Sacramento",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "2005",
      "7uijs8vk": None,
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Crowding in jails",
          "Inmate treatment",
          "Access to resources in jails",
          "Something else"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": None,
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Phone",
          "Email"
        ]
      },
      "93za6j1k": "777-777-7777 home number, no text",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T15:28:47.156Z",
    "updated_at": "2019-05-02T21:19:59.687Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated",
      "Flagged for Jason & Ryan",
      "t-medical issue"
    ],
    "responder_language": "en",
    "responder": {
      "name": "N",
      "email": "email2@domain.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2238158,
    "sequential_id": 23,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "AhJUQUbRtjrA",
    "submitted_at": "2019-02-14T16:07:42.666Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "2009,2010,2011",
      "7uijs8vk": "County jail Sacramento, rccc",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment",
          "Crowding in jails"
        ]
      },
      "e7ysl3ph": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email",
          "Phone"
        ]
      },
      "93za6j1k": "9999999999",
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T15:45:43.452Z",
    "updated_at": "2019-05-02T21:19:59.758Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated",
      "Inmate treatment",
      "Gripping story",
      "Flagged for Jason & Ryan",
      "t-medical issue",
      "t-mental health"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "Name@email.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  },
  {
    "id": 2238512,
    "sequential_id": 24,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "gN7mgij3KftA",
    "submitted_at": "2019-02-14T17:59:25.648Z",
    "responses": {
      "xyejrz01": "Leila.fake@email.org",
      "gw0fisz8": "Leila",
      "89i3s4r9": "Bodolay",
      "zmfl6vor": "Grover Beach",
      "j74rigc6": "San Luis Obispo",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "September 2014.",
      "7uijs8vk": "A county jail",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elit\u201cI\u2019m A\u201d one \u201chaha aaabe\u201d then  Lorem ipsum dolor sit amet, consectetur adipiscing elit \u201csll\u201d",
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T17:23:28.561Z",
    "updated_at": "2019-05-02T21:19:59.782Z",
    "status": "For ProPublica",
    "labels": [
      "p-incarcerated",
      "c\u2013San Luis Obispo Co",
      "Inmate treatment",
      "Gripping story",
      "Flagged for Jason & Ryan"
    ],
    "responder_language": "en",
    "responder": {
      "name": "person",
      "email": "person.name@email.tld"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "embedded",
      "hostname": "www.propublica.org"
    }
  },
  {
    "id": 2238780,
    "sequential_id": 25,
    "project_id": 6619,
    "form_id": 6076,
    "initial_response_id": None,
    "pretty_id": "067iO06Icl5W",
    "submitted_at": "2019-02-14T19:11:57.734Z",
    "responses": {
      "xyejrz01": "fake@email.org",
      "gw0fisz8": "Firstname",
      "89i3s4r9": "Lastname",
      "zmfl6vor": "Cityname",
      "j74rigc6": "Countyname",
      "uhmrq5tt": None,
      "qc3dnp53": {
        "checked": [
          "I am or was incarcerated in a California county jail"
        ],
        "other_checked": False
      },
      "ebylx5ma": "April 1993",
      "7uijs8vk": "Sacramento county",
      "om2nonpp": None,
      "272fofp6": None,
      "u2jm5r4y": None,
      "f3hxvy5w": None,
      "b2737g2k": {
        "checked": [
          "Inmate treatment"
        ]
      },
      "e7ysl3ph": None,
      "i9jwhanh": "Lorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elitLorem ipsum dolor sit amet, consectetur adipiscing elit",
      "sf7vwnas": None,
      "720omdzq": None,
      "76bnr9v8": None,
      "s6la0qv2": None,
      "ab9z0508": {
        "checked": [
          "Email"
        ]
      },
      "93za6j1k": None,
      "lkuuse2q": None
    },
    "rating_aggregates": {},
    "average_rating": None,
    "num_ratings": 0,
    "created_at": "2019-02-14T18:57:50.942Z",
    "updated_at": "2019-05-02T21:19:59.825Z",
    "status": "For ProPublica",
    "labels": [
      "c\u2013Sacramento County",
      "p-incarcerated",
      "t-medical issue",
      "t-mental health"
    ],
    "responder_language": "en",
    "responder": {
      "name": "Name",
      "email": "something@gmail.org"
    },
    "deleted_at": None,
    "submission_source": {
      "type": "frontend",
      "hostname": "forms.fm"
    }
  }
]


class ScreendoorTestCase(TestCase):
    @patch.object(requests, "get")
    def test_can_fetch_form_without_form_id(self, mockget):
        mockresponse = Mock()
        mockget.return_value = mockresponse
        mockresponse.json.return_value = LIST_FORMS
        importer = ScreendoorImporter(api_key="KEY", base_url="https://fake.tld")
        data = importer.get_form(9999)
        self.assertTrue("field_data" in data)
        self.assertEqual(len(data["field_data"]), 23)

    @patch.object(requests, "get")
    def test_can_fetch_form_with_form_id(self, mockget):
        mockresponse = Mock()
        mockget.return_value = mockresponse
        mockresponse.json.return_value = LIST_FORMS[0]
        importer = ScreendoorImporter(api_key="KEY", base_url="https://fake.tld")
        data = importer.get_form(9999, form_id=120)
        self.assertTrue("field_data" in data)
        self.assertEqual(len(data["field_data"]), 23)

    @patch.object(requests, "get")
    def test_can_build_pk_to_header_map(self, mockget):
        mockresponse = Mock()
        mockget.return_value = mockresponse
        mockresponse.json.return_value = LIST_FORMS[0]
        importer = ScreendoorImporter(api_key="KEY", base_url="https://fake.tld")
        data = importer.get_form(9999, form_id=120)
        maps = importer.get_header_maps(data)
        self.assertTrue(maps)
        self.assertEqual(len(maps.keys()), 23)
        self.assertEqual(
            maps["xyejrz01"], "What's your email address? (ID: xyejrz01)"
        )

    @patch.object(requests, "get")
    def test_can_build_csv(self, mockget):
        importer = ScreendoorImporter(api_key="KEY", base_url="https://fake.tld")
        csv = importer.build_csv_from_data(LIST_FORMS[0], LIST_RESPONSES)
        self.assertTrue(csv)
        parsed_csv = Dataset().load(csv)
        self.assertTrue(
            "What's your email address? (ID: xyejrz01)" in parsed_csv.headers
        )

    @patch.object(requests, "get")
    def test_can_build_csv_with_ids(self, mockget):
        importer = ScreendoorImporter(api_key="KEY", base_url="https://fake.tld")
        csv = importer.build_csv_from_data(LIST_FORMS[0], LIST_RESPONSES)
        self.assertTrue(csv)
        parsed_csv = Dataset().load(csv)
        self.assertTrue("id" in parsed_csv.headers)

    # @patch.object(requests, "get")
    # def test_can_use_buildin_id_during_import(self, mockget):
    #     mockresponse = Mock()
    #     mockget.return_value = mockresponse
    #     mockresponse.json.side_effect = [
    #         LIST_FORMS, LIST_RESPONSES
    #     ]
    #     importer = ScreendoorImporter(api_key="KEY", base_url="https://fake.tld")
    #     csv = importer.build_csv(6076)
    #     print("Screendoor CSV", csv)
    #     self.assertTrue(len(csv))
    #     self.assertTrue(False)
