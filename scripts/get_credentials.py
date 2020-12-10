import base64
import sys

args = sys.argv

if len(args) < 2:
    print("You must provide the 'basicAuth' value from the QR code payload")
    exit(1)

user_pass = ""
try:
    user_pass = base64.b64decode(args[1]).decode().rstrip()
except Exception as e:
    print(f"Failed to decode base64 encoded user:pass - {e}")
    exit(1)

user_pass_split = user_pass.split(":")

if len(user_pass_split) != 2:
    print(f"Decoded data ({user_pass}) does not contain enough segments")
    exit(1)

username = user_pass_split[0]
password = user_pass_split[1]

print(f"HTTP_USERNAME={username}")
print(f"HTTP_PASSWORD={password}")
