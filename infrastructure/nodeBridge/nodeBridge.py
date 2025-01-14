import asyncio
from sanic import Sanic
from sanic import Websocket
import paho.mqtt.client as mqtt

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
    try:
        while True:
            if len(node_published_data) > 0:
                latest_response = node_published_data.pop(0)[2:-1]
                print(f"sending {latest_response}")
                await ws.send(latest_response)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

if __name__ == "__main__":
    app.run(port=8001, auto_reload=True)