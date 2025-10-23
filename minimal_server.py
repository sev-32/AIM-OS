
import sys
import json

print("Minimal server starting...", file=sys.stderr)
while True:
    line = sys.stdin.readline()
    if not line:
        break
    try:
        request = json.loads(line.strip())
        response = {"echo": request, "status": "ok"}
        print(json.dumps(response), flush=True)
    except Exception as e:
        error = {"error": str(e)}
        print(json.dumps(error), flush=True)
