from app import createApp
from waitress import serve
from os import environ


app = createApp()

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=int(environ.get("PORT", 8080)), debug=True)
    serve(app, host='0.0.0.0', port=int(environ.get("PORT")))
