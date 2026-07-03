from telemetry.Xbee import Xbee
import threading

antenna = Xbee(port='/dev/ttyUSB0', baudrate=38400)
antenna.open(force_settings=True)

# start polling thread
def poll_thread():
    while True:
        dest, msg = antenna.poll_msg()
        print(f"Received from {dest}: {msg}")

polling = threading.Thread(target=poll_thread)
polling.start()

while True:
    msg = input("Enter message to send (or 'exit' to quit): ")
    if msg.lower() == 'exit':
        break
    antenna.send_msg_broadcast(msg)

polling.join(timeout=3)
antenna.close()