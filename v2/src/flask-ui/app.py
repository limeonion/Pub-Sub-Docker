import logging
import subprocess
from flask import Flask, render_template, Response

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO)


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
    return


@app.route("/", methods=["GET"])
def base():
    # for path in execute(["locate", "docker"]):
    #     logging.info(path)
    logs = {'topic_broker': "Shit's on fire,\n yo."}
    return Response(execute(["locate", "libcurl"]), mimetype="text/html")
    # return render_template("index.html", logs=logs)


if __name__ == "__main__":
    app.run()
