import sys
import subprocess
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

LANGUAGE_OPTIONS = {
    'python': {
        'ext': 'py',
        'bin': 'python3',
        'commands': ['python3 {0}']
    },
    'cpp': {
        'ext': 'cpp',
        'bin': 'g++',
        'commands': ['g++ -Wall {0} -o /tmp/cpp.out', './tmp/cpp.out']
    },
    'c': {
        'ext': 'c',
        'bin': 'gcc',
        'commands': ['gcc -Wall {0} -o /tmp/c.out', './tmp/c.out']
    },
    'js': {
        'ext': 'js',
        'bin': 'node',
        'commands': ['node {0}']
    },
}


def printe(*kwargs):
    print(*kwargs, file=sys.stderr)
    return


def get_arguments(req):
    """ Gets the arguments from the web UI and fetches the entries from the map """
    code = None
    language = 'python'
    request_json = req.get_json()
    if request_json:
        if 'language' in request_json:
            language = str(request_json['language']).lower()
        if 'code' in request_json:
            code = request_json["code"]
    if 'code' in req.form:
        code = req.form['code']
    if 'language' in req.form:
        language = req.form['language']
    return code, language


def format_commands(language):
    """ Formats the commands to be executed for the child process to execute """
    options = LANGUAGE_OPTIONS[language]
    bin_exec = "{0}".format(options['bin'])
    filename = "/tmp/tmp.{0}".format(options['ext'])
    commands = [c.format(filename) for c in options['commands']]
    return bin_exec, filename, commands


@app.route("/")
def advertise():
    return "Working!"


@app.route("/run", methods=["POST"])
def run_code():
    """
    Runs the code submitted from the front end,
    by using a fork-exec model.
    It also captures the STDOUT, STDERR and relays them back
    """
    # In seconds
    MAX_TIMEOUT = 5
    code, language = get_arguments(request)
    if code is None or language is None:
        return Response(status=404)
    bin_exec, filename, cmds = format_commands(language)
    # Write the code to be run to a temporary file
    with open(filename, 'w+') as file:
        file.write(code)
    str_stdout = ""
    str_stderr = ""
    for cmd in cmds:
        split_cmd = cmd.split(" ")
        try:
            # Run the code written in the temp file, and capture STDOUT, STDERR.
            # Also, we have a timeout to prevent long running code
            out = subprocess.run(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=MAX_TIMEOUT)
            printe("Command: {0}, Output: {1}".format(cmd, out))
            str_stdout += out.stdout.decode("UTF-8")
            str_stderr += out.stderr.decode("UTF-8")
            if out.returncode != 0:
                break
        except subprocess.TimeoutExpired as e:
            printe("Exception:", e)
            str_stderr += str(e)
            break
    response = {'stdout': str_stdout, 'stderr': str_stderr}
    return jsonify(response)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
