import os
import csv
import redis
import textwrap
from io import StringIO
import time
import subprocess
import signal

def main():
    cleaned = textwrap.dedent(RAW).strip()
    LOCAL_PORT = 63792
    HOSTNAME = "redis.d3llie.tech"
    LOCAL_HOST = "127.0.0.1"
    SERVICE_TOKEN_SECRET="4e0f730142c2a5a1e2889125de517265ab7430e42c00e39778908953a5f8ed5e"
    SERVICE_TOKEN_ID="5f5f6f7f70032ed235556225e80bb9b1.access"
    
    
    cloudflared_cmd = [
            "cloudflared", "access", "tcp",
            "--hostname", HOSTNAME,
            "--url", f"{LOCAL_HOST}:{LOCAL_PORT}",
            "--service-token-id", SERVICE_TOKEN_ID,
            "--service-token-secret", SERVICE_TOKEN_SECRET,
        ]

        # Output status information
    print(f"Starting Cloudflare proxy on {LOCAL_HOST}:{LOCAL_PORT} → redis.d3llie.tech ...")

    # Make the actual subprocess to handle our connection
    proc = subprocess.Popen(
        cloudflared_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # Wait briefly for the tunnel to come up
    time.sleep(0.5)

    if proc.poll() is not None:
        stderr = proc.stderr.read()
        raise RuntimeError(f"cloudflared exited early:\n{stderr}")

    # The main connection initialization block
    try:
        r = redis.Redis(
                host=f'{LOCAL_HOST}',
                port=LOCAL_PORT,
                username="default",
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True,
            )
        
    except Exception as e:
        print(
            f"Failed to establish SQL connection!\nFailed with exception: {e}")
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)  # Tell it to close
            try:
                # Give it the chance to exit gracefully
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()  # Kill it if it takes too long

    reader = csv.DictReader(StringIO(cleaned), delimiter="\t", skipinitialspace=True)

    pipe = r.pipeline()
    for raw_row in reader:
        fields = {k.strip(): v.strip() for k, v in raw_row.items() if k and v}
        if fields:
            pipe.xadd("sensor_stream", fields)
    pipe.execute()

    print("Data successfully pushed as Redis lists!")

if __name__ == "__main__":
    main()
