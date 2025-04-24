import os
from pathlib import Path
from base64 import b64encode

from yaml import safe_load

print("Starting...")

key = os.urandom(32)

volumePath = None
composePath = Path.cwd() / "compose.yaml"
if composePath.exists():
    with open(composePath, "r") as f:
        compose = safe_load(f.read())
    for service in compose.get("services", {}).values():
        if "circuit-stash-backend" in service.get("image", ""):
            volumePath = service.get("volumes", [])
            if len(volumePath) > 0:
                volumePath = volumePath.pop().split(":")[0]

if volumePath:
    print("Volume path found")
    if volumePath.startswith("/"):
        print("Volume path is absolute")
        secretPath = Path(volumePath) / "secrets" / "jwt.txt"
    else:
        print("Volume path is relative")
        secretPath = Path.cwd() / volumePath / "secrets" / "jwt.txt"
else:
    print("Volume path not found")
    secretPath = Path.cwd() / "secrets" / "jwt.txt"

print(f"Saving secret to {secretPath}")
secretPath.parent.mkdir(parents=True, exist_ok=True)
with open(secretPath, "w") as f:
    f.write(b64encode(key).decode())

print("Done!")