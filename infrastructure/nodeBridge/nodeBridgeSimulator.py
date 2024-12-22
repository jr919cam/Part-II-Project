import asyncio
from sanic import Sanic
from sanic import Websocket
import json

app = Sanic("nodeBridgeSimulator")

data = []

def getJSONDataList(day):
    with open(f'node_22-28Jan/cerberus-node-lt1_2024-01-{day}.txt', 'r') as file:
        JSONDataList = [json.loads(dataLine[:-1]) for dataLine in file]
    return JSONDataList[6200:]


@app.websocket("/ws")
async def websocket_feed(request, ws: Websocket):
    speed = float(request.args.get("speed"))
    day = request.args.get("day")
    JSONDataList = getJSONDataList(day)
    try:
        for i, reading in enumerate(JSONDataList):
            acp_ts, acp_id, crowdcount, seats_occupied = reading.values()
            formattedReading = {"acp_ts":acp_ts,"acp_id":acp_id, "payload_cooked":{"crowdcount": crowdcount, "seats_occupied": seats_occupied}}
            print(f'sending: {formattedReading}')
            await ws.send(json.dumps(formattedReading))
            if i == len(JSONDataList) - 1:
                break
            time_delta = float(JSONDataList[i+1]['acp_ts']) - float(formattedReading['acp_ts'])
            await asyncio.sleep(time_delta/speed)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

if __name__ == "__main__":
    app.run(port=8002, auto_reload=True)