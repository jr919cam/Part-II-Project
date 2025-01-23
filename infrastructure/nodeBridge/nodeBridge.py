import asyncio
import json
from sanic import Sanic
from sanic import Websocket
import paho.mqtt.client as mqtt
from synopses import LectureBoundarySynopsis, PercentageConcentrationSynopsis, WholeRoomStabilitySynopsis

app = Sanic("nodeBridge")

node_published_data = []

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    client.subscribe("csn/cerberus-node-lt1")

def on_message(client, userdata, msg):
    node_published_data.append(str(msg.payload))
    
client = mqtt.Client()
client.username_pw_set("csn-node", "csn-node")

client.on_connect = on_connect
client.on_message = on_message

MQTT_BROKER_HOST = "tfc-app9.cl.cam.ac.uk"
MQTT_BROKER_PORT = 1883

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.loop_start() 

@app.websocket("/ws")
async def websocket_feed(request, ws: Websocket):
    wholeRoomStabilitySynopsis = WholeRoomStabilitySynopsis()
    percentageConcentrationSynopsis = PercentageConcentrationSynopsis(None)
    try:
        while True:
            if len(node_published_data) > 0:
                latestResponse = node_published_data.pop(0)[2:-1]
                latestResponseJSON = json.loads(latestResponse)
                acp_ts, acp_id, acp_type_id, payload_cooked = latestResponseJSON.values()
                bax, crowdcount, seats_occupied, occupancy_filled = payload_cooked.values()
                wholeRoomStabilitySynopsis.updateRoomStability(seats_occupied)

                if percentageConcentrationSynopsis.seat != None:
                    percentageConcentrationSynopsis.updateAverage(seats_occupied)

                enhancedReading = {
                    "acp_ts":acp_ts,
                    "acp_id":acp_id, 
                    "acp_type_id":acp_type_id, 
                    "payload_cooked": {
                        "bax": bax,
                        "crowdcount": crowdcount,
                        "seats_occupied": seats_occupied, 
                        "occupancy_filled": occupancy_filled,
                        "percent_concentration": percentageConcentrationSynopsis.avg, 
                        "seatsOccupiedDiffCountTotal":wholeRoomStabilitySynopsis.seatsOccupiedDiffCountTotal,
                        "seatsOccupiedDiffCount":wholeRoomStabilitySynopsis.seatsOccupiedDiffCount
                    },
                    "type":"reading", 
                    "readingType":"node"
                }
                await ws.send(json.dumps(enhancedReading))
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

if __name__ == "__main__":
    app.run(port=8001, auto_reload=True)