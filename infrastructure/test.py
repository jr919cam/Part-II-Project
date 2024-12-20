from sanic import Sanic
from sanic.response import text
from sanic.response import html

app = Sanic("TestApp")

@app.get("/")
async def test_response(request):
    return text("test successful")

@app.get("/hello_esha")
async def get_hello_esha(request):
    html_response = "<h1>Hello Esha!</h1><img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfWXfxjJVRBX8zqYXnocg1rL0NNSm7DCxvRg&s' />"
    return html(html_response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)