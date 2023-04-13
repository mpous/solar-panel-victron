import json
import os
import paho.mqtt.client as mqtt
from lib.protocol import *
from lib.helper import get_product_name, get_operation_state_message, get_off_reason_message


device_id = os.environ.get('BALENA_DEVICE_UUID', default="default")

serial_port = os.getenv("SERIAL_PORT", default="/dev/ttyUSB0")
mqtt_broker = os.getenv("MQTT_BROKER", default="localhost") 
mqtt_port = os.getenv("MQTT_PORT", default="1883")
mqtt_topic = os.getenv("MQTT_TOPIC", default=f"{device_id}/tronmon/uplink")

if __name__ == '__main__':

    ve = Vedirect(serial_port, 30)
    
    client = mqtt.Client()

    # TODO: Add try catch for MQTT connection
    client.connect(mqtt_broker, int(mqtt_port), 60)
    client.loop_start()

    def mqtt_send_callback(packet):

        payload = {
                'victron': {
                        'system': {
                                'serial': packet['SER#'],
                                'product_id': packet['PID'],
                                'product_name': get_product_name(packet['PID'])
                        },
                        'panel': {
                                'voltage': int(packet['VPV']) * .001,
                                'current': round(int(packet['PPV']) / int(packet['VPV']) * 1000, 2),
                                'power': int(packet['PPV'])
                        },
                        'battery': {
                                'voltage': int(packet['V']) * .001, 
                                'current': int(packet['I']) * .001,
                                'power': int(packet['VPV']) / 1000 * int(packet['I']) / 1000, 
                                'state': packet['CS'],
                                'state_message': get_operation_state_message(packet['CS'])
                                #'off_reason': packet['OR'],
                                #'off_reason_message': get_off_reason_message(packet['OR']),
                        }
                }
        }

        client.publish(mqtt_topic, json.dumps(payload))

    ve.read_data_callback(mqtt_send_callback)