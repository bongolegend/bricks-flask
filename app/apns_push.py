
import time
from apns import APNs, Frame, Payload

apns = APNs(use_sandbox=True, key_file='../apns_auth_key.p8')

# Send a notification
token_hex = '77290198dc2ebc3d62c39f0fe709f6ef0e458e6f594ba932e1ecde38d919c347'
payload = Payload(alert="Hello World!", sound="default", badge=1)
apns.gateway_server.send_notification(token_hex, payload)