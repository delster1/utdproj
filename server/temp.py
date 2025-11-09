import os
import csv
import redis
import textwrap
from io import StringIO
import time
import subprocess
import signal

def main():
    RAW = """
    HeartRate	Temp	AccelX	AccelY	AccelZ
    78.54465638	27.07738655	0.038251037	0.059707538	89.96364385
    81.44963232	22.85595408	-0.006827296	-0.026332237	89.83924387
    74.23690019	20.99582355	0.120598706	0.004258071	89.99139438
    74.78047988	28.34333584	-0.117656461	0.073962978	90.02344499
    77.7353512	24.41270403	0.032144392	-0.059442033	90.13221796
    76.78233758	27.41371176	0.020124313	0.136161692	89.95207999
    66.17205077	27.61376375	-0.00725032	0.078416779	90.17590692
    72.80490073	27.4778902	-0.121878249	0.032225723	89.91511934
    72.75326831	24.75019741	0.127862159	0.109149327	90.12854296
    69.14236125	21.6384452	-0.032702344	0.074097066	89.91414339
    82.88322765	21.47959326	-0.074646924	0.034919451	90.06641241
    72.91733075	26.97921181	0.023980906	-0.294457771	89.96595432
    74.10657269	28.45550419	-0.155421131	0.173737057	90.01282738
    74.73429575	29.15996603	-0.040068059	0.023166421	90.00657141
    75.51478856	27.69851477	0.21041361	0.056772834	89.93146111
    79.07222032	27.29219012	-0.031081165	0.06193692	90.13052847
    76.33450435	24.67628869	0.233631816	-0.146268276	90.05036798
    82.32520634	27.51172964	0.049216539	-0.002913824	89.8474606
    74.51538624	25.00192709	-0.048007897	0.034117334	89.88603
    68.85309155	26.17258417	0.105693467	-0.299918912	89.82741959
    65.95544995	21.70574159	-0.098966964	-0.061367262	89.96944246
    69.7060298	28.38827472	-0.02251305	0.123847554	90.03126943
    82.97265044	23.67659912	-0.062233422	0.059881754	90.13756438
    75.95307307	29.59988258	-0.066654365	0.046473209	89.99018433
    75.12833798	31.40181788	0.075746228	0.002363026	89.98555805
    66.35755935	23.16283373	-0.011622551	-0.061558802	90.17416592
    """

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
