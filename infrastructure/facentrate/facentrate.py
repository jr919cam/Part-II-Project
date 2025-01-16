import asyncio
import json
import random
from sanic import Sanic
from sanic import file
from sanic import text

app = Sanic("facentrate")

app.static("/infrastructure", "./infrastructure", name="infrastructure_static")
app.static("/node_modules", "./node_modules", name="node_modules_static")

@app.get("/")
async def root_response(request):
    return await file("infrastructure/facentrate/index.html")

@app.get("/livenode")
async def livenode_response(request):
    return await file("infrastructure/facentrate/livenode/index.html")

@app.get("/emulatednode")
async def emulatednode_response(request):
    return await file("infrastructure/facentrate/emulatednode/index.html")


if __name__ == "__main__":
    app.run(port=8000, debug=True, auto_reload=True)