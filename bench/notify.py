import os
import urllib.request

topic = os.environ.get("NTFY_TOPIC", "")
msg = (f"✅ Vision benchmark run {os.environ['RUN_ID']} finished\n"
       f"Report: {os.environ.get('PAGES_URL', '?')}\n"
       f"Dashboard: {os.environ.get('SPACE_URL', '?')}")
if topic:
    urllib.request.urlopen(f"https://ntfy.sh/{topic}", data=msg.encode())
print("notified" if topic else "no topic set")
