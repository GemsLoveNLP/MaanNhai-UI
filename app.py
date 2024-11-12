from flask import Flask, render_template, jsonify
from modules.publisher import Publisher

# create a Flask application
app = Flask(__name__)

# connect the MQTT publisher
mqtt_publisher = Publisher()
mqtt_publisher.connect()

# render the UI in index.html
@app.route('/')
def index():
    return render_template('index.html')

# publish the OPEN command to the subscriber
@app.route('/open')
def open_button():
    mqtt_publisher.publish("OPEN")
    return jsonify(status="success")

# publish the CLOSE command to the subscriber
@app.route('/close')
def close_button():
    mqtt_publisher.publish("CLOSE")
    return jsonify(status="success")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
