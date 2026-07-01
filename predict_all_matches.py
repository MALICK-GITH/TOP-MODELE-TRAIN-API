"""
Générer des prédictions pour tous les matchs du JSON de données de marché
"""

import requests
import json

API_URL = "http://localhost:8001"

# Données de marché complètes (extraites du JSON)
market_data_json = {
  "Id": 0,
  "Success": True,
  "Error": "",
  "ErrorCode": 0,
  "Guid": "",
  "Value": [
    {
      "R": 50,
      "SC": {"FS": {"S1": 4, "S2": 3}, "PS": [], "CPS": "", "TS": 382, "I": "", "SLS": "6 minutes"},
      "VI": "xgame7_53282720",
      "VA": 1,
      "HMH": 1,
      "ICY": True,
      "U": 1782878965,
      "I": 733136194,
      "N": 183049,
      "T": 50,
      "CO": 17,
      "E": [
        {"T": 4, "C": 1.001, "CV": "1.001", "B": True, "G": 8},
        {"T": 5, "C": 1.12, "CV": "1.12", "G": 8},
        {"T": 1, "C": 1.168, "CV": "1.168", "G": 1},
        {"T": 12, "P": 4.5, "C": 1.256, "CV": "1.256", "G": 15},
        {"T": 14, "P": 3.5, "C": 1.31, "CV": "1.31", "G": 62},
        {"T": 8, "P": 1.0, "C": 1.775, "CV": "1.775", "G": 2},
        {"T": 10, "P": 7.5, "C": 1.785, "CV": "1.785", "G": 17},
        {"T": 9, "P": 7.5, "C": 2.025, "CV": "2.025", "G": 17},
        {"T": 7, "P": -1.0, "C": 2.048, "CV": "2.048", "G": 2},
        {"T": 13, "P": 3.5, "C": 3.34, "CV": "3.34", "G": 62},
        {"T": 11, "P": 4.5, "C": 3.72, "CV": "3.72", "G": 15},
        {"T": 6, "C": 4.04, "CV": "4.04", "G": 8},
        {"T": 2, "C": 4.71, "CV": "4.71", "G": 1},
        {"T": 3, "C": 28, "CV": "28", "G": 1}
      ],
      "AE": [
        {"G": 2, "ME": [
          {"T": 7, "P": -1.0, "C": 2.048, "CV": "2.048", "G": 2, "CE": 1},
          {"T": 8, "P": 1.0, "C": 1.775, "CV": "1.775", "G": 2, "CE": 1},
          {"T": 7, "P": -1.5, "C": 4.77, "CV": "4.77", "G": 2},
          {"T": 8, "P": 1.5, "C": 1.145, "CV": "1.145", "G": 2}
        ]},
        {"G": 17, "ME": [
          {"T": 9, "P": 7.5, "C": 2.025, "CV": "2.025", "G": 17, "CE": 1},
          {"T": 10, "P": 7.5, "C": 1.785, "CV": "1.785", "G": 17, "CE": 1}
        ]}
      ],
      "EC": 33,
      "TG": "",
      "V": "",
      "VE": "",
      "PN": "",
      "TN": "Mi-temps",
      "DI": "",
      "S": 1782878400,
      "HS": 1,
      "SGC": 1,
      "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
      "O1": "Barcelone",
      "O2": "Liverpool",
      "O1I": 180071,
      "O2I": 180449,
      "O1IS": [180071],
      "O2IS": [180449],
      "O1C": 78,
      "O1CT": "Barcelona",
      "O2C": 231,
      "O1IMG": ["180071.png"],
      "O2IMG": ["180449.png"],
      "O1R": "Барселона",
      "O2R": "Ливерпуль",
      "O1E": "Barcelona",
      "O2E": "Liverpool",
      "SI": 85,
      "SN": "FIFA",
      "SR": "FIFA",
      "SE": "FIFA",
      "L": "FC 26. 5x5 Rush. Superligue",
      "LR": "FC 26. 5x5 Rush. Суперлига",
      "LE": "FC 26. 5x5 Rush. Superleague",
      "LI": 2986291,
      "CN": "Monde",
      "CE": "World",
      "COI": 225,
      "MS": [0],
      "KI": 1,
      "CID": 2,
      "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
      "TNS": "Mi-temps"
    },
    {
      "R": 50,
      "SC": {"FS": {}, "PS": [], "CPS": "", "GS": 128, "TS": 35, "TD": -1, "I": "Paris avant le début du jeu", "SLS": "Début dans 1 minutes"},
      "HMH": 1,
      "GNS": True,
      "ICY": True,
      "U": 1782878965,
      "I": 733137546,
      "N": 192489,
      "T": 50,
      "CO": 17,
      "E": [
        {"T": 5, "C": 1.06, "CV": "1.06", "G": 8},
        {"T": 6, "C": 1.42, "CV": "1.42", "G": 8},
        {"T": 7, "P": 1.0, "C": 1.62, "CV": "1.62", "G": 2},
        {"T": 12, "P": 3.5, "C": 1.7, "CV": "1.7", "G": 15},
        {"T": 10, "P": 7.5, "C": 1.72, "CV": "1.72", "G": 17},
        {"T": 13, "P": 3.5, "C": 1.725, "CV": "1.725", "G": 62},
        {"T": 3, "C": 1.88, "CV": "1.88", "G": 1},
        {"T": 4, "C": 1.88, "CV": "1.88", "G": 8},
        {"T": 14, "P": 3.5, "C": 2.112, "CV": "2.112", "G": 62},
        {"T": 9, "P": 7.5, "C": 2.12, "CV": "2.12", "G": 17},
        {"T": 11, "P": 3.5, "C": 2.15, "CV": "2.15", "G": 15},
        {"T": 8, "P": -1.0, "C": 2.296, "CV": "2.296", "G": 2},
        {"T": 1, "C": 2.615, "CV": "2.615", "G": 1},
        {"T": 2, "C": 6.13, "CV": "6.13", "G": 1}
      ],
      "AE": [
        {"G": 2, "ME": [
          {"T": 7, "C": 2.3, "CV": "2.3", "G": 2},
          {"T": 8, "C": 1.62, "CV": "1.62", "G": 2},
          {"T": 7, "P": -1.0, "C": 3.65, "CV": "3.65", "G": 2},
          {"T": 8, "P": -1.0, "C": 2.296, "CV": "2.296", "G": 2, "CE": 1},
          {"T": 7, "P": 1.0, "C": 1.62, "CV": "1.62", "G": 2, "CE": 1},
          {"T": 8, "P": 1.0, "C": 1.264, "CV": "1.264", "G": 2},
          {"T": 8, "P": -1.5, "C": 2.664, "CV": "2.664", "G": 2},
          {"T": 7, "P": 1.5, "C": 1.455, "CV": "1.455", "G": 2},
          {"T": 8, "P": -2.0, "C": 3.63, "CV": "3.63", "G": 2},
          {"T": 7, "P": 2.0, "C": 1.27, "CV": "1.27", "G": 2}
        ]},
        {"G": 17, "ME": [
          {"T": 9, "P": 5.5, "C": 1.27, "CV": "1.27", "G": 17},
          {"T": 10, "P": 5.5, "C": 3.61, "CV": "3.61", "G": 17},
          {"T": 9, "P": 6.5, "C": 1.59, "CV": "1.59", "G": 17},
          {"T": 10, "P": 6.5, "C": 2.36, "CV": "2.36", "G": 17},
          {"T": 9, "P": 7.5, "C": 2.12, "CV": "2.12", "G": 17, "CE": 1},
          {"T": 10, "P": 7.5, "C": 1.72, "CV": "1.72", "G": 17, "CE": 1},
          {"T": 9, "P": 8.5, "C": 3.01, "CV": "3.01", "G": 17},
          {"T": 10, "P": 8.5, "C": 1.368, "CV": "1.368", "G": 17},
          {"T": 9, "P": 9.5, "C": 4.59, "CV": "4.59", "G": 17},
          {"T": 10, "P": 9.5, "C": 1.16, "CV": "1.16", "G": 17}
        ]}
      ],
      "EC": 103,
      "TG": "",
      "V": "",
      "VE": "",
      "PN": "",
      "TN": "Mi-temps",
      "DI": "",
      "S": 1782879000,
      "HS": 1,
      "SGC": 1,
      "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
      "O1": "Borussia Dortmund",
      "O2": "Lombardia",
      "O1I": 180429,
      "O2I": 9466583,
      "O1IS": [180429],
      "O2IS": [9466583],
      "O1C": 53,
      "O1CT": "Dortmund",
      "O2C": 225,
      "O1IMG": ["16e1f8a81f1c0bc02147460446de1333.png"],
      "O2IMG": ["6ff16309322bc0a6db4c42caf4a9eb49.png"],
      "O1R": "Боруссия",
      "O2R": "Ломбардия",
      "O1E": "Borussia",
      "O2E": "Lombardia",
      "SI": 85,
      "SN": "FIFA",
      "SR": "FIFA",
      "SE": "FIFA",
      "L": "FC 26. 5x5 Rush. Superligue",
      "LR": "FC 26. 5x5 Rush. Суперлига",
      "LE": "FC 26. 5x5 Rush. Superleague",
      "LI": 2986291,
      "CN": "Monde",
      "CE": "World",
      "COI": 225,
      "MS": [0],
      "KI": 1,
      "CID": 2,
      "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
      "TNS": "Mi-temps"
    },
    {
      "R": 50,
      "SC": {"FS": {}, "PS": [], "CPS": "", "GS": 128, "TS": 635, "TD": -1, "I": "Paris avant le début du jeu", "SLS": "Début dans 11 minutes"},
      "HMH": 1,
      "GNS": True,
      "ICY": True,
      "U": 1782878965,
      "I": 733138788,
      "N": 199338,
      "T": 50,
      "CO": 17,
      "E": [
        {"T": 5, "C": 1.064, "CV": "1.064", "G": 8},
        {"T": 4, "C": 1.488, "CV": "1.488", "G": 8},
        {"T": 10, "P": 7.5, "C": 1.675, "CV": "1.675", "G": 17},
        {"T": 7, "C": 1.72, "CV": "1.72", "G": 2},
        {"T": 14, "P": 3.5, "C": 1.74, "CV": "1.74", "G": 62},
        {"T": 6, "C": 1.77, "CV": "1.77", "G": 8},
        {"T": 11, "P": 3.5, "C": 1.83, "CV": "1.83", "G": 15},
        {"T": 12, "P": 3.5, "C": 1.975, "CV": "1.975", "G": 15},
        {"T": 1, "C": 2.005, "CV": "2.005", "G": 1},
        {"T": 13, "P": 3.5, "C": 2.09, "CV": "2.09", "G": 62},
        {"T": 8, "C": 2.12, "CV": "2.12", "G": 2},
        {"T": 9, "P": 7.5, "C": 2.19, "CV": "2.19", "G": 17},
        {"T": 3, "C": 2.416, "CV": "2.416", "G": 1},
        {"T": 2, "C": 6.02, "CV": "6.02", "G": 1}
      ],
      "AE": [
        {"G": 2, "ME": [
          {"T": 7, "C": 1.72, "CV": "1.72", "G": 2, "CE": 1},
          {"T": 8, "C": 2.12, "CV": "2.12", "G": 2, "CE": 1},
          {"T": 7, "P": -1.0, "C": 2.485, "CV": "2.485", "G": 2},
          {"T": 8, "P": -1.0, "C": 3.296, "CV": "3.296", "G": 2},
          {"T": 7, "P": 1.0, "C": 1.315, "CV": "1.315", "G": 2},
          {"T": 8, "P": 1.0, "C": 1.51, "CV": "1.51", "G": 2},
          {"T": 7, "P": -1.5, "C": 2.91, "CV": "2.91", "G": 2},
          {"T": 8, "P": -1.5, "C": 3.74, "CV": "3.74", "G": 2},
          {"T": 7, "P": 1.5, "C": 1.23, "CV": "1.23", "G": 2},
          {"T": 8, "P": 1.5, "C": 1.39, "CV": "1.39", "G": 2}
        ]},
        {"G": 17, "ME": [
          {"T": 9, "P": 5.5, "C": 1.29, "CV": "1.29", "G": 17},
          {"T": 10, "P": 5.5, "C": 3.45, "CV": "3.45", "G": 17},
          {"T": 9, "P": 6.5, "C": 1.63, "CV": "1.63", "G": 17},
          {"T": 10, "P": 6.5, "C": 2.28, "CV": "2.28", "G": 17},
          {"T": 9, "P": 7.5, "C": 2.19, "CV": "2.19", "G": 17, "CE": 1},
          {"T": 10, "P": 7.5, "C": 1.675, "CV": "1.675", "G": 17, "CE": 1},
          {"T": 9, "P": 8.5, "C": 3.15, "CV": "3.15", "G": 17},
          {"T": 10, "P": 8.5, "C": 1.34, "CV": "1.34", "G": 17},
          {"T": 9, "P": 9.5, "C": 4.85, "CV": "4.85", "G": 17},
          {"T": 10, "P": 9.5, "C": 1.144, "CV": "1.144", "G": 17}
        ]}
      ],
      "EC": 100,
      "TG": "",
      "V": "",
      "VE": "",
      "PN": "",
      "TN": "Mi-temps",
      "DI": "",
      "S": 1782879600,
      "HS": 1,
      "SGC": 1,
      "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
      "O1": "Juventus",
      "O2": "Fenerbahçe",
      "O1I": 180451,
      "O2I": 202111,
      "O1IS": [180451],
      "O2IS": [202111],
      "O1C": 79,
      "O2C": 190,
      "O2CT": "Istanbul",
      "O1IMG": ["180451.png"],
      "O2IMG": ["202111.png"],
      "O1R": "Ювентус",
      "O2R": "Фенербахче",
      "O1E": "Juventus",
      "O2E": "Fenerbahce",
      "SI": 85,
      "SN": "FIFA",
      "SR": "FIFA",
      "SE": "FIFA",
      "L": "FC 26. 5x5 Rush. Superligue",
      "LR": "FC 26. 5x5 Rush. Суперлига",
      "LE": "FC 26. 5x5 Rush. Superleague",
      "LI": 2986291,
      "CN": "Monde",
      "CE": "World",
      "COI": 225,
      "MS": [0],
      "KI": 1,
      "CID": 2,
      "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
      "TNS": "Mi-temps"
    },
    {
      "R": 50,
      "SC": {"FS": {}, "PS": [], "CPS": "", "GS": 128, "TS": 1235, "TD": -1, "I": "Paris avant le début du jeu", "SLS": "Début dans 21 minutes"},
      "HMH": 1,
      "GNS": True,
      "ICY": True,
      "U": 1782878965,
      "I": 733140246,
      "N": 207283,
      "T": 50,
      "CO": 17,
      "E": [
        {"T": 5, "C": 1.02, "CV": "1.02", "G": 8},
        {"T": 6, "C": 1.088, "CV": "1.088", "G": 8},
        {"T": 3, "C": 1.275, "CV": "1.275", "G": 1},
        {"T": 13, "P": 4.5, "C": 1.81, "CV": "1.81", "G": 62},
        {"T": 10, "P": 7.5, "C": 1.816, "CV": "1.816", "G": 17},
        {"T": 8, "P": -2.0, "C": 1.864, "CV": "1.864", "G": 2},
        {"T": 11, "P": 2.5, "C": 1.87, "CV": "1.87", "G": 15},
        {"T": 12, "P": 2.5, "C": 1.93, "CV": "1.93", "G": 15},
        {"T": 7, "P": 2.0, "C": 1.936, "CV": "1.936", "G": 2},
        {"T": 9, "P": 7.5, "C": 1.992, "CV": "1.992", "G": 17},
        {"T": 14, "P": 4.5, "C": 2, "CV": "2", "G": 62},
        {"T": 4, "C": 3.29, "CV": "3.29", "G": 8},
        {"T": 1, "C": 5.41, "CV": "5.41", "G": 1},
        {"T": 2, "C": 8.07, "CV": "8.07", "G": 1}
      ],
      "AE": [
        {"G": 2, "ME": [
          {"T": 8, "P": -1.0, "C": 1.39, "CV": "1.39", "G": 2},
          {"T": 7, "P": 1.0, "C": 2.896, "CV": "2.896", "G": 2},
          {"T": 8, "P": -1.5, "C": 1.632, "CV": "1.632", "G": 2},
          {"T": 7, "P": 1.5, "C": 2.27, "CV": "2.27", "G": 2},
          {"T": 8, "P": -2.0, "C": 1.864, "CV": "1.864", "G": 2, "CE": 1},
          {"T": 7, "P": 2.0, "C": 1.936, "CV": "1.936", "G": 2, "CE": 1},
          {"T": 8, "P": -2.5, "C": 2.19, "CV": "2.19", "G": 2},
          {"T": 7, "P": 2.5, "C": 1.675, "CV": "1.675", "G": 2},
          {"T": 8, "P": -3.0, "C": 2.74, "CV": "2.74", "G": 2},
          {"T": 7, "P": 3.0, "C": 1.43, "CV": "1.43", "G": 2}
        ]},
        {"G": 17, "ME": [
          {"T": 9, "P": 5.5, "C": 1.216, "CV": "1.216", "G": 17},
          {"T": 10, "P": 5.5, "C": 3.88, "CV": "3.88", "G": 17},
          {"T": 9, "P": 6.5, "C": 1.504, "CV": "1.504", "G": 17},
          {"T": 10, "P": 6.5, "C": 2.5, "CV": "2.5", "G": 17},
          {"T": 9, "P": 7.5, "C": 1.992, "CV": "1.992", "G": 17, "CE": 1},
          {"T": 10, "P": 7.5, "C": 1.816, "CV": "1.816", "G": 17, "CE": 1},
          {"T": 9, "P": 8.5, "C": 2.775, "CV": "2.775", "G": 17},
          {"T": 10, "P": 8.5, "C": 1.42, "CV": "1.42", "G": 17},
          {"T": 9, "P": 9.5, "C": 4.14, "CV": "4.14", "G": 17},
          {"T": 10, "P": 9.5, "C": 1.19, "CV": "1.19", "G": 17}
        ]}
      ],
      "EC": 106,
      "TG": "",
      "V": "",
      "VE": "",
      "PN": "",
      "TN": "Mi-temps",
      "DI": "",
      "S": 1782880200,
      "HS": 1,
      "SGC": 1,
      "CHIMG": "ca664fc41fa19d9ebf563216785a5485.png",
      "O1": "Olympique Lyonnais",
      "O2": "Real Madrid",
      "O1I": 2349351,
      "O2I": 180075,
      "O1IS": [2349351],
      "O2IS": [180075],
      "O1C": 225,
      "O2C": 78,
      "O2CT": "Madrid",
      "O1IMG": ["2349351.png"],
      "O2IMG": ["180075.png"],
      "O1R": "Лион",
      "O2R": "Реал",
      "O1E": "Olympique Lyonnais",
      "O2E": "Real Madrid",
      "SI": 85,
      "SN": "FIFA",
      "SR": "FIFA",
      "SE": "FIFA",
      "L": "FC 26. 5x5 Rush. Superligue",
      "LR": "FC 26. 5x5 Rush. Суперлига",
      "LE": "FC 26. 5x5 Rush. Superleague",
      "LI": 2986291,
      "CN": "Monde",
      "CE": "World",
      "COI": 225,
      "MS": [0],
      "KI": 1,
      "CID": 2,
      "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
      "TNS": "Mi-temps"
    },
    {
      "R": 50,
      "SC": {"FS": {"S1": 6, "S2": 5}, "PS": [{"Key": 1, "Value": {"S1": 4, "NF": "1ère mi-temps"}}, {"Key": 2, "Value": {"S1": 2, "S2": 5, "NF": "2ème mi-temps"}}], "CP": 2, "CPS": "2ème mi-temps", "TS": 360, "TR": -1, "I": "", "SLS": "6 minutes"},
      "VI": "xgame7_53282738",
      "VA": 1,
      "HMH": 1,
      "ICY": True,
      "U": 1782878963,
      "I": 733134662,
      "N": 176096,
      "T": 50,
      "CO": 17,
      "E": [],
      "AE": [],
      "EC": 33,
      "TG": "",
      "V": "",
      "VE": "",
      "PN": "",
      "TN": "Mi-temps",
      "DI": "",
      "S": 1782878400,
      "HS": 1,
      "SGC": 1,
      "O1": "Bournemouth",
      "O2": "Tottenham Hotspur",
      "O1I": 3274437,
      "O2I": 251217,
      "O1IS": [3274437],
      "O2IS": [251217],
      "O1C": 39,
      "O2C": 39,
      "O1IMG": ["be91ed99349a92447d2ceb9bb6e513cd.png"],
      "O2IMG": ["251217.png"],
      "O1R": "Борнмут",
      "O2R": "Тоттенхэм Хотспур",
      "O1E": "Bournemouth",
      "O2E": "Tottenham Hotspur",
      "SI": 85,
      "SN": "FIFA",
      "SR": "FIFA",
      "SE": "FIFA",
      "L": "FC 24. 4x4. Championnat d'Angleterre",
      "LR": "FC 24. 4x4. Чемпионат Англии",
      "LE": "FC 24. 4x4. England Championship",
      "LI": 2648573,
      "CN": "Angleterre",
      "CE": "England",
      "COI": 231,
      "MS": [0],
      "KI": 1,
      "CID": 2,
      "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
      "TNS": "Mi-temps"
    },
    {
      "R": 50,
      "SC": {"FS": {}, "PS": [], "CPS": "", "GS": 128, "TS": 637, "TD": -1, "TR": -1, "I": "Paris avant le début du jeu", "SLS": "Début dans 11 minutes"},
      "HMH": 1,
      "GNS": True,
      "ICY": True,
      "U": 1782878963,
      "I": 733137456,
      "N": 191777,
      "T": 50,
      "CO": 17,
      "E": [
        {"T": 5, "C": 1.001, "CV": "1.001", "B": True, "G": 8},
        {"T": 4, "C": 1.35, "CV": "1.35", "G": 8},
        {"T": 1, "C": 1.6, "CV": "1.6", "G": 1},
        {"T": 10, "P": 14.5, "C": 1.74, "CV": "1.74", "G": 17},
        {"T": 14, "P": 6.5, "C": 1.795, "CV": "1.795", "G": 62},
        {"T": 8, "P": 1.5, "C": 1.81, "CV": "1.81", "G": 2},
        {"T": 11, "P": 7.5, "C": 1.84, "CV": "1.84", "G": 15},
        {"T": 12, "P": 7.5, "C": 1.965, "CV": "1.965", "G": 15},
        {"T": 7, "P": -1.5, "C": 2, "CV": "2", "G": 2},
        {"T": 13, "P": 6.5, "C": 2.016, "CV": "2.016", "G": 62},
        {"T": 9, "P": 14.5, "C": 2.096, "CV": "2.096", "G": 17},
        {"T": 6, "C": 2.22, "CV": "2.22", "G": 8},
        {"T": 3, "C": 2.885, "CV": "2.885", "G": 1},
        {"T": 2, "C": 9.04, "CV": "9.04", "G": 1}
      ],
      "AE": [
        {"G": 2, "ME": [
          {"T": 7, "P": -1.5, "C": 2, "CV": "2", "G": 2, "CE": 1},
          {"T": 8, "P": -1.5, "C": 4.01, "CV": "4.01", "G": 2},
          {"T": 7, "P": 1.5, "C": 1.2, "CV": "1.2", "G": 2},
          {"T": 8, "P": 1.5, "C": 1.81, "CV": "1.81", "G": 2, "CE": 1},
          {"T": 7, "P": -2.5, "C": 2.53, "CV": "2.53", "G": 2},
          {"T": 8, "P": 2.5, "C": 1.496, "CV": "1.496", "G": 2},
          {"T": 7, "P": -3.5, "C": 3.395, "CV": "3.395", "G": 2},
          {"T": 8, "P": 3.5, "C": 1.3, "CV": "1.3", "G": 2},
          {"T": 8, "P": 4.5, "C": 1.15, "CV": "1.15", "G": 2}
        ]},
        {"G": 17, "ME": [
          {"T": 9, "P": 12.5, "C": 1.344, "CV": "1.344", "G": 17},
          {"T": 10, "P": 12.5, "C": 3.115, "CV": "3.115", "G": 17},
          {"T": 9, "P": 13.5, "C": 1.64, "CV": "1.64", "G": 17},
          {"T": 10, "P": 13.5, "C": 2.256, "CV": "2.256", "G": 17},
          {"T": 9, "P": 14.5, "C": 2.096, "CV": "2.096", "G": 17, "CE": 1},
          {"T": 10, "P": 14.5, "C": 1.74, "CV": "1.74", "G": 17, "CE": 1},
          {"T": 9, "P": 15.5, "C": 2.815, "CV": "2.815", "G": 17},
          {"T": 10, "P": 15.5, "C": 1.41, "CV": "1.41", "G": 17},
          {"T": 9, "P": 16.5, "C": 4.01, "CV": "4.01", "G": 17},
          {"T": 10, "P": 16.5, "C": 1.2, "CV": "1.2", "G": 17}
        ]}
      ],
      "EC": 131,
      "TG": "",
      "V": "",
      "VE": "",
      "PN": "",
      "TN": "Mi-temps",
      "DI": "",
      "S": 1782879600,
      "HS": 1,
      "SGC": 2,
      "O1": "Brentford",
      "O2": "Crystal Palace",
      "O1I": 3635533,
      "O2I": 3274445,
      "O1IS": [3635533],
      "O2IS": [3274445],
      "O1C": 231,
      "O2C": 39,
      "O1IMG": ["01e0e43c33f11cb287ec7f8af47de030.png"],
      "O2IMG": ["0c5ac8809833a5ec65bd2ec4c1f046d6.png"],
      "O1R": "Брентфорд",
      "O2R": "Кристал Пэлэс",
      "O1E": "Brentford",
      "O2E": "Crystal Palace",
      "SI": 85,
      "SN": "FIFA",
      "SR": "FIFA",
      "SE": "FIFA",
      "L": "FC 24. 4x4. Championnat d'Angleterre",
      "LR": "FC 24. 4x4. Чемпионат Англии",
      "LE": "FC 24. 4x4. England Championship",
      "LI": 2648573,
      "CN": "Angleterre",
      "CE": "England",
      "COI": 231,
      "MS": [0],
      "KI": 1,
      "CID": 2,
      "SIMG": "/genfiles/cms/sport_preview_5a598a83300665a1d4192948ea1362e5.png",
      "TNS": "Mi-temps"
    }
  ]
}

def predict_all_matches():
    """Génère des prédictions pour tous les matchs"""
    
    print("🧪 Génération de prédictions pour tous les matchs")
    print("=" * 80)
    
    matches = market_data_json["Value"]
    total_matches = len(matches)
    
    print(f"\n📊 Nombre total de matchs: {total_matches}")
    print("=" * 80)
    
    predictions = []
    
    for i, match in enumerate(matches, 1):
        team_home = match["O1E"]
        team_away = match["O2E"]
        league = match["L"]
        
        # Construire market_data si disponible
        market_data = None
        if match.get("E") and match.get("AE"):
            market_data = {
                "O1": match["O1"],
                "O2": match["O2"],
                "L": match["L"],
                "E": match["E"],
                "AE": match["AE"]
            }
        
        request = {
            "team_home": team_home,
            "team_away": team_away,
            "league": league
        }
        
        if market_data:
            request["market_data"] = market_data
        
        print(f"\n📋 Match {i}/{total_matches}: {team_home} vs {team_away}")
        print(f"   Ligue: {league}")
        print(f"   Market data: {'Oui' if market_data else 'Non'}")
        
        try:
            response = requests.post(f"{API_URL}/predict", json=request)
            if response.status_code == 200:
                data = response.json()
                predictions.append({
                    "match": f"{team_home} vs {team_away}",
                    "league": league,
                    "family": data["family"],
                    "predictions": data["predictions"]
                })
                print(f"   ✅ Prédiction générée - Famille: {data['family']}")
                
                # Afficher score_range
                score_range = data["predictions"]["score_range"]
                range_keys = list(score_range.keys())[:-1]
                print(f"   📊 Score Range: {range_keys}")
                
            else:
                print(f"   ❌ Erreur API: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ COMPLET DES PRÉDICTIONS")
    print("=" * 80)
    
    for pred in predictions:
        print(f"\n🏆 {pred['match']}")
        print(f"   Ligue: {pred['league']}")
        print(f"   Famille: {pred['family']}")
        print(f"\n   📈 1X2:")
        print(f"      Home: {pred['predictions']['1x2']['home']:.3f} (conf: {pred['predictions']['1x2']['confidence']:.3f})")
        print(f"      Draw: {pred['predictions']['1x2']['draw']:.3f}")
        print(f"      Away: {pred['predictions']['1x2']['away']:.3f}")
        print(f"\n   🎯 Total Goals:")
        print(f"      Prédit: {pred['predictions']['total_goals']['predicted']}")
        print(f"      Platform: {pred['predictions']['total_goals']['platform_value']}")
        print(f"\n   📊 BTTS:")
        print(f"      No: {pred['predictions']['btts']['no']:.3f} (conf: {pred['predictions']['btts']['confidence']:.3f})")
        print(f"      Yes: {pred['predictions']['btts']['yes']:.3f}")
        print(f"\n   🎲 Score Range:")
        for key, value in pred['predictions']['score_range'].items():
            if key != 'confidence':
                print(f"      {key}: {value:.3f}")
        print(f"      Confidence: {pred['predictions']['score_range']['confidence']:.3f}")
        print(f"\n   ⚖️ Over/Under:")
        print(f"      Under: {pred['predictions']['over_under']['under']:.3f}")
        print(f"      Over: {pred['predictions']['over_under']['over']:.3f} (conf: {pred['predictions']['over_under']['confidence']:.3f})")
        print(f"\n   🏃 Handicap:")
        print(f"      Prédit: {pred['predictions']['handicap']['predicted']}")
        print(f"      Platform: {pred['predictions']['handicap']['platform_value']}")
        print(f"\n   🔄 Double Chance:")
        print(f"      1X: {pred['predictions']['double_chance']['1x']:.3f}")
        print(f"      X2: {pred['predictions']['double_chance']['x2']:.3f}")
        print(f"      12: {pred['predictions']['double_chance']['12']:.3f}")
        print(f"\n   🧹 Clean Sheet:")
        print(f"      Home No: {pred['predictions']['clean_sheet']['home_no']:.3f}")
        print(f"      Home Yes: {pred['predictions']['clean_sheet']['home_yes']:.3f}")
        print(f"      Away No: {pred['predictions']['clean_sheet']['away_no']:.3f}")
        print(f"      Away Yes: {pred['predictions']['clean_sheet']['away_yes']:.3f}")
        print(f"\n   🎯 Draw No Bet:")
        print(f"      Home: {pred['predictions']['draw_no_bet']['home']:.3f}")
        print(f"      Away: {pred['predictions']['draw_no_bet']['away']:.3f}")
        print(f"      Draw: {pred['predictions']['draw_no_bet']['draw']:.3f}")
        print(f"\n   ⚡ Win Both Halves:")
        print(f"      No: {pred['predictions']['win_both_halves']['no']:.3f}")
        print(f"      Yes: {pred['predictions']['win_both_halves']['yes']:.3f}")
        print(f"\n   🎲 Parité:")
        print(f"      Pair: {pred['predictions']['parity']['pair']:.3f}")
        print(f"      Impair: {pred['predictions']['parity']['impair']:.3f}")
        print("\n" + "-" * 80)
    
    print(f"\n✅ Total des prédictions générées: {len(predictions)}/{total_matches}")
    
    return predictions

if __name__ == "__main__":
    predict_all_matches()
