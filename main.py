import json
import uuid

import websocket
import rel
from datetime import datetime
from time import sleep
from collections import defaultdict

hamsats = {
        47311: "AO-109",
        22825: "AO-27",
        39444: "AO-73",
        7530: "AO-7",
        43017: "AO-91",
        43137: "AO-92",
        43770: "AO-95",
        41847: "CAS-2T",
        43441: "CAS-4A",
        42759: "CAS-4B",
        27844: "CUTE-1",
        40032: "EO-80",
        42017: "EO-88",
        24278: "FO-29",
        43937: "FO-99",
        30776: "FS-3",
        50466: "HO-113",
        36122: "HO-68",
        40931: "IO-86",
        25544: "ISS-FM",
        44419: "JAISAT-1",
        43803: "JO-97",
        40908: "LILACSAT-2",
        20442: "LO-19",
        41557: "LO-87",
        26931: "NO-44",
        43132: "PICSAT",
        43678: "PO-101",
        43700: "QO-100",
        44909: "RS-44",
        27607: "SO-50",
        # 50988: "TEVEL-3",
        44881: "TO-108",
        14781: "UO-11",
        47438: "UVSQ-SAT",
        27848: "XI-IV",
        40903: "XW-2A",
        40911: "XW-2B",
        40906: "XW-2C",
        40907: "XW-2D",
        40909: "XW-2E",
        40910: "XW-2F"}

observers = {}
prediction_requests = {}

class Observer:
    def __init__(self, latitude, longitude, name=None):
        self.uuid = str(uuid.uuid4())
        self.latitude = latitude
        self.longitude = longitude
        self.name = name



def on_message(ws, message):
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    #print("message: " + message)
    m_object = json.loads(message)
    #print(m_object['observer'])

    #print(m_object)

    if "event" in m_object:
        if m_object['event'] == "observer_registered":
            observers[m_object['observer']['uuid']] = m_object['observer']
            print(current_time + " OBSERVER REGISTERED | " + m_object['observer']['uuid'])

            sats_to_subscribe = []

            message = '{"event": "subscribe", "satellites": ['

            for k, v in hamsats.items():
                message += str(k) + ', '

            message = message[0:len(message) - 2]

            message += '], "observer_uuid": "' + m_object['observer']['uuid'] + '"}'
            ws.send(message)

        if m_object['event'] == "subscription_confirmed":
            print(current_time + " SUBSCRIPTION CONFIRMED | " + str(len(m_object['prediction_requests'])) + " PREDICTION REQUESTS")

            for prediction_request in m_object['prediction_requests']:
                prediction_requests[prediction_request['norad_cat_id']] = prediction_request

            message2 = '{"event": "unsubscribe", "prediction_request_uuids": ["' + prediction_requests['44881']['prediction_request_uuid'] + '"]}'

            ws.send(message2)

        if m_object['event'] == "unsubscribe_confirmed":
            line = current_time + " UNSUBSCRIBE CONFIRMED | "
            for prediction_request_uuid in m_object['prediction_request_uuids']:
                line += str(prediction_request_uuid) + ", "

            line = line[0:len(line)-2]

            print(line)

        if m_object['event'] == "system_status":
            print(current_time + " SYSTEM_STATUS | " + json.dumps(m_object))

    else:
        if "predictions" in m_object:
            for prediction in m_object['predictions']:
                if(prediction['norad_cat_id'] == 44881 or prediction['norad_cat_id'] == 7530):
                    print(current_time + " PREDICTION RECEIVED | " + prediction['name'] + " (" + str(prediction['norad_cat_id']) + ")  " + "Azimuth: " + str(prediction['azimuth']) + "  Elevation: " + str(prediction['elevation']) + "  Timestamp: " + str(prediction['timestamp']))

def on_error(ws, error):
    print("error: " + str(error))

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:8000",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    message = '{"event": "register_observer", "observer": {"name": "my_location", "latitude": -38, "longitude": -92}}'
    ws.send(message)
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()


