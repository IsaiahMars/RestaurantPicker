from app import createApp

app = createApp()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


# This is the file used to run our website. In visual studio code,
# click the sideways triangle in the top right corner of your screen,
# wait a few seconds, and ctrl + click on the link provided. This is a
# locally hosted webpage.
