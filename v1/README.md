# Version 1
## Overview
Version 1 consists of a webservice that runs inside a docker container, that executes arbitrary code passed to it
by the user, via a front end. It follows the fork-exec model of code execution by creating a child process,
that runs the arbitrary code. The child process has a time limit as well, to prevent it from running too 
long. 

The fork-exec model is followed to protect the parent process from crashing from any faults, or vulnerabilities the
arbitrary code might exhibit.

## Setup
1. Run the bash script `src/docker_build_run.sh`. This brings up a docker container that is accessible at 
`localhost:4000`.
2. Open the file `ui/index.html` in a normal web browser (Note, you do NOT need a webserver). 
3. Ensure that the docker container is up and running, and then you can enter any code in any of the given languages to see the output
