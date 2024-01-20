from bson import json_util
import json

potential_date_fields = [
  'datetime',
  'lastUsed',
]

def parse_json(data):
  res = json.loads(json_util.dumps(data))
  res['_id'] = res['_id']['$oid']
  
  # Convert all potential date fields to string
  for field in potential_date_fields:
    if field in res:
      res[field] = res[field]['$date']

  return res
