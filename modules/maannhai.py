import time
from gpiozero import LED, Button, DigitalInputDevice
from utils.tts import speak, OPEN, CLOSE, OFF, ENA

# Note that the speech is disabled here, but can be uncommented to activate

# initialize a class for the control over the hardware
class MaanNhai:
    def __init__(self, init_status="close"):
        # Assign pins

        # LED
        self.red = LED(17)
        self.green = LED(27)
        self.blue = LED(22)

        # push button
        self.button1 = Button(24, pull_up=True)
        self.button2 = Button(23, pull_up=True)

        # limit switches
        self.lmPulley = DigitalInputDevice(12, pull_up=True, bounce_time = 0.1)
        self.lmMotor = DigitalInputDevice(6, pull_up=True, bounce_time = 0.1)

        # stepper motor driver
        self.pul = LED(16)
        self.dir = LED(20)
        self.ena = LED(21)

        # Setup motor parameters
        self.speed = 50
        self.rotate = 90
        self.status = init_status

    # Setup functions to control LED colors
    def led(self, rgb):
        r, g, b = [int(color) for color in rgb]
        self.red.value = r
        self.green.value = g
        self.blue.value = b

    def ledOff(self):
        self.led("000")

    def ledRed(self):
        self.led("100")

    def ledGreen(self):
        self.led("010")

    def ledBlue(self):
        self.led("001")

    def ledPurple(self):
        self.led("101")

    def ledCyan(self):
        self.led("011")

    def ledYellow(self):
        self.led("110")

    def ledWhite(self):
        self.led("111")

    # Motor control methods

    # move the clicker piece to the motor side
    def moveToMotor(self):
        self.dir.off()
        time.sleep(0.0001)
        for _ in range(self.rotate):
            self.pul.on()
            time.sleep(0.001 / self.speed)
            self.pul.off()
            time.sleep(0.001 / self.speed)

    # move the clicker piece to the pulley side
    def moveToPulley(self):
        self.dir.on()
        time.sleep(0.0001)
        for _ in range(self.rotate):
            self.pul.on()
            time.sleep(0.001 / self.speed)
            self.pul.off()
            time.sleep(0.001 / self.speed)

    # stop the motor and move the clicker away from the limit switch (motor side)
    def stopMotor(self):
        self.ledRed()
        time.sleep(0.01)
        self.moveToPulley()
        time.sleep(0.01)
        time.sleep(0.5)
        self.ledOff()

    # stop the motor and move the clicker away from the limit switch (pulley side)
    def stopPulley(self):
        self.ledRed()
        time.sleep(0.01)
        self.moveToMotor()
        time.sleep(0.01)
        time.sleep(0.5)
        self.ledOff()

    # Movement control methods

    # move the clicker until it hits the motor side limit switch
    # LED code is purple
    def moveUntilMotor(self):
        self.ledPurple()
        while self.lmMotor.is_active:
            self.moveToMotor()
        self.stopMotor()
        self.ledOff()

    # move the clicker until it hits the pulley side limit switch
    # LED code is blue
    def moveUntilPulley(self):
        self.ledBlue()
        while self.lmPulley.is_active:
            self.moveToPulley()
        self.stopPulley()
        self.ledOff()

    # move to predifined home position
    def moveHome(self):
        self.ledWhite()
        while self.lmPulley.is_active:
            self.moveToPulley()
        self.stopPulley()
        self.ledOff()

    # Main loop to run the curtain control system
    def run(self, action=None):
        """
        Runs the main control loop.
        If an action ("OPEN" or "CLOSE") is provided, it will execute that action.
        Otherwise, it will handle button presses.
        """
        if action == "OPEN":
            self.open_curtain()
        elif action == "CLOSE":
            self.close_curtain()
        else:
            self.handle_buttons()

    # open the curtain
    def open_curtain(self):
        if self.status == "close":
            print("[DEVICE] Openning")
            self.ledCyan()
            self.moveUntilMotor()
            self.status = "open"
            if ENA:
                speak("open")
            print("[DEVICE] Curtains are OPENED")
            self.ledGreen()

    # close the curtain
    def close_curtain(self):
        if self.status == "open":
            print("[DEVICE] Closing")
            self.ledYellow()
            self.moveUntilPulley()
            self.status = "close"
            if ENA:
                speak("close")
            print("[DEVICE] Curtains are CLOSED")
            self.ledGreen()


    # handle the push button operations
    def handle_buttons(self, queue):
        """
        Handles button presses to control the curtains.
        """

        # wait for signal
        while True:

            # default LED to green
            self.ledGreen()

            # if the pulley side limit switch is hit
            if not self.lmPulley.is_active:
                print("lmPulley active")
                self.stopPulley()
                self.status = "close"
                if ENA:
                    speak(CLOSE)

            # if the motor side limit switch is hit
            if not self.lmMotor.is_active:
                print("lmMotor active")
                self.stopMotor()
                self.status = "open"
                if ENA:
                    speak(OPEN)

            # if push button 1 is pressed
            if self.button1.is_pressed:
                print("Button1 pressed")
                # if closed, then move slightly to open, LED is cyan
                if self.status == "close":
                    self.ledCyan()
                    self.moveToMotor()
                    time.sleep(0.005)
                # if opend, then move slightly to close, LED is yellow
                else:
                    self.ledYellow()
                    self.moveToPulley()
                    time.sleep(0.005)

            # if push button 2 is pressed
            if self.button2.is_pressed:
                print("Button2 pressed")
                # if button 1 is also pressed, turns off the system
                if self.button1.is_pressed:
                    self.moveHome()
                    print("Curtain Turning off")
                    if ENA:
                        speak(OFF)
                    return
                # if closed, then move until open
                if self.status == "close":
                    self.moveUntilMotor()
                    time.sleep(0.01)
                    self.status = "open"
                    if ENA:
                        speak(OPEN)
                # if opened, then move until close
                else:
                    self.moveUntilPulley()
                    time.sleep(0.01)
                    self.status = "close"
                    if ENA:
                        speak(CLOSE)

            # sleep to better performance
            time.sleep(0.1)


if __name__ == '__main__':
    curtain_control = MaanNhai(init_status="close")
    curtain_control.run()
