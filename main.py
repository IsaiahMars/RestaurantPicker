from app import createApp
from waitress import serve
from os import environ
import os
import dotenv

project_folder = os.path.expanduser('~/RestaurantPicker')  # adjust as appropriate
dotenv.load_dotenv(os.path.join(project_folder, '.env'))


app = createApp()

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=int(environ.get("PORT", 8080)), debug=True)
    serve(app, port=int(environ.get("PORT")))
