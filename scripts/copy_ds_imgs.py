import os,sys, shutil, subprocess, shlex

# a simple script to copy the imgs of a dataset to here
# this script is used separately.


DS_IMG_PATH='/home/chadrick/github/test/mysite/homepage/static/datasets/imgs'
CURRENT_DIR = os.getcwd()
COPY_DESTINATION_PATH= os.path.join(CURRENT_DIR,'imgs')

# prepare copy destination
if os.path.exists(COPY_DESTINATION_PATH):
    shutil.rmtree(COPY_DESTINATION_PATH)
os.makedirs(COPY_DESTINATION_PATH)

for i in range(0,12):
    index= str(i)
    target_dir = os.path.join(DS_IMG_PATH,index)
    cmd="cp -r {} {}".format(target_dir+"/.",COPY_DESTINATION_PATH)
    p=subprocess.Popen(shlex.split(cmd))
    p.wait()
    print("copy of {} finished".format(index))

print("finish code")

