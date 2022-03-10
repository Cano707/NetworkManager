from os import path
import json
import app.models

db_base=dict()
for device_type in app.models.device_vendor_mapping.keys():
    db_base[device_type]=dict()


with open(path.join(".", "app", "database.json"), "w") as db_handler:
    json.dump(db_base, db_handler, indent=4)