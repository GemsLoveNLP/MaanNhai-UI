import threading
import queue
from modules.maannhai import MaanNhai
from modules.subscriber import Subscriber
import time

class DeviceController:
    # initialize
    def __init__(self):
        # hardware control
        self.maannhai = MaanNhai(init_status="close")
        # request queue
        self.request_queue = queue.Queue()
        # remote control subscriber
        self.mqtt_subscriber = Subscriber(topic="maannhai-mqtt", callback=self.handle_mqtt_message)

    def handle_mqtt_message(self, message):
        """
        Callback function to handle MQTT messages.
        """
        self.request_queue.put(message)

    def device_loop(self):
        # handle MQTT
        while True:
            # when requested
            if not self.request_queue.empty():
                action = self.request_queue.get()
                # open the curtain
                if action == "OPEN":
                    self.maannhai.open_curtain()
                # close the curtain
                elif action == "CLOSE":
                    self.maannhai.close_curtain()
            # sleep to help with performance
            else:
                time.sleep(0.1)
            

    def start(self):
        # Start button thread
        button_thread = threading.Thread(target=self.maannhai.handle_buttons, kwargs={"queue": self.request_queue})
        button_thread.daemon = True
        button_thread.start()

        # Start the device loop thread
        device_thread = threading.Thread(target=self.device_loop)
        device_thread.daemon = True
        device_thread.start()

        # Start the MQTT subscriber in the main thread
        self.mqtt_subscriber.run()


if __name__ == "__main__":
    device = DeviceController()
    device.start()
