from subprocess import Popen, PIPE, CalledProcessError

cmd = 'concurrently "node /home/ubuntu/webrtc/index.js" "sudo python3 /home/ubuntu/pm/src/app.py"'
with Popen(cmd, shell=True, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in iter(p.stdout.readline, ""):
        print(line)
        if "compiled successfully" in line:
            pass
