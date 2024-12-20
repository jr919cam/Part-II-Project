import asyncio
import json
import random
from sanic import Sanic
from sanic import file
from sanic import text

app = Sanic("atntv")

@app.get("/")
async def root_response(request):
    return await file("infrastructure/atntv/index.html")

@app.get("/livenode")
async def livenode_response(request):
    return await file("infrastructure/atntv/livenode/index.html")


if __name__ == "__main__":
    app.run(port=8001, debug=True, auto_reload=True)