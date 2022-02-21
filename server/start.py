from subprocess import Popen, PIPE, CalledProcessError

cmd = 'concurrently "python3 /home/ubuntu/server/post.py" "cd /home/ubuntu/test/my-app && yarn start"'
with Popen(cmd, shell=True, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in iter(p.stdout.readline, ""):
        print(line)
        if "compiled successfully" in line:
            print("testing app running on: http://ec2-52-68-10-27.ap-northeast-1.compute.amazonaws.com:8080/")

if p.returncode != 0:
    raise CalledProcessError(p.returncode, p.args)