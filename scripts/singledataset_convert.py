#!/bin/python3


# this is a script file that converted all the saves json to actual trainable annotation json files.
# modified to work with single dataset


import argparse
import json
import os
import sys
from PIL import Image
import sqlite3
import shutil

SQLITE_DB_LOCATION='/home/chadrick/github/test/mysite/db.sqlite3'
STATIC_PATH='/home/chadrick/github/test/mysite/homepage/static'
DS_IMG_PATH='/home/chadrick/github/test/mysite/homepage/static/datasets/imgs'

CURRENT_DIR=os.getcwd()

ds_finished_count=0
swap_count=0
below_zero_case=0
finished_count=0
no_label_count=0


def prepare_output_dir(dirpath):
    # remove the dir
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    os.makedirs(dirpath)

def convert_and_save(spjsondata,imgdir,dirfilelist,outputdir,dsid):
    global ds_finished_count, no_label_count
    ds_finished_count=0
    for i in range(0,len(spjsondata)):
        
        get_data_of_index = spjsondata[str(i)]

        # if there are no labeles, then skip
        if len(get_data_of_index)==0:
            no_label_count+=1
            continue
        
        dsidformat = format(dsid,'03')
        paddedindex = format(i,'03')
        # outputfilename = outputdir+'_'+paddedindex+'.json'
        basefilename = dsidformat+'_'+paddedindex+'.json'
        outputfilename = os.path.join(outputdir,basefilename)
        outfd = open(outputfilename,'w')
        

        createjson={}
        createjson['imgfile']=dirfilelist[i]
        imgpath = os.path.join(imgdir,dirfilelist[i])
        im=Image.open(imgpath)
        w,h=im.size
        createjson['w']=w
        createjson['h']=h
        arrlist=[]

        for item in get_data_of_index:
            startx=item['startX']
            starty=item['startY']
            widthx=item['widthX']
            widthy=item['widthY']

            x1=startx
            y1=starty
            x2=startx+widthx
            y2=starty+widthy

            # adjust x1,y1,x2,y2 larger values
            # x1<x2, y1<y2
            swap_occured_flag =False
            if x1>x2:
                temp=x1
                x1=x2
                x2=temp
                swap_occured_flag=True
            if y1>y2:
                temp=y1
                y1=y2
                y2=temp
                swap_occured_flag=True
            
            if swap_occured_flag:
                # print("swap occured!")
                global swap_count
                swap_count+=1
            
            if x1<0 or x2<0 or y1<0 or y2<0:
                # print("below zero case occured!!")
                global below_zero_case
                below_zero_case+=1



            
            objects_json={}
            objects_json['name']=item['label']
            rectjson={}
            rectjson['x1']=x1
            rectjson['y1']=y1
            rectjson['x2']=x2
            rectjson['y2']=y2
            objects_json['rect']=rectjson
            
            arrlist.append(objects_json)
        
        createjson['objects']=arrlist
        # outfd.write(str(createjson))
        # outfd.flush()

        ## the proper way to write json to file is using dump not str(jsonobject)
        ## the prior will save with double apostrophies, while the latter will save with single apostrophies. This does matter.
        json.dump(createjson,outfd)
        outfd.close()
        global finished_count
        finished_count+=1
        ds_finished_count+=1
    
parser = argparse.ArgumentParser(description="converting json to json that is compatible with training")
# parser.add_argument('--prepareonelot',action='store_const',const=True,default=False,help="use it when the user wants to save all the converted json and images in one dir")
# parser.add_argument('--zipprefix',nargs=1,type=str)
# parser.add_argument('--zipbasename',action='store', default="outputzip", help="zip file base name")
# parser.add_argument('--saveinonedir',action='store_const', const=True, default=False,help="save all video screenshots in one directory")
parser.add_argument('dsid',help="dsid to convert")


parseargs = parser.parse_args()

targetdsid = int(parseargs.dsid)






conn = sqlite3.connect(SQLITE_DB_LOCATION)
c = conn.cursor()


c.execute("SELECT * from homepage_save_progress where dsid=?",(targetdsid,))
results = c.fetchall()
results = sorted(results,key=lambda x: x[2])

print("result = {}".format(results))

if len(results) is not 1:
    print("query result size is not 1.")
    sys.exit(0)

result = results[0]


savedprogressjsonfile = os.path.join(STATIC_PATH,result[3])
dsid = result[2]
datasetimgdir=os.path.join(DS_IMG_PATH,str(dsid))


conv_output_dir = os.path.join(CURRENT_DIR,str(dsid))
prepare_output_dir(conv_output_dir)




fd = open(savedprogressjsonfile,'r')
rawline=fd.readline()
firstconv=json.loads(rawline)
spjson=json.loads(firstconv)
spjsondata = spjson['data']

dirfilelist = sorted(os.listdir(datasetimgdir))

# check length
if len(spjsondata) != len(dirfilelist):
    print("length do not match. abort")
    sys.exit(1)

# now convert and save in to conv_output_dir
convert_and_save(spjsondata,datasetimgdir,dirfilelist,conv_output_dir,dsid)

print("finished convert and saving for dsid={} -- finish count={}".format(dsid,ds_finished_count))
    

   

# find the saved progress table.
# find the file that matches the dsid and username

#print stat
print("finished count={}".format(finished_count))
print("swap_count={}".format(swap_count))
print("below_zero_count={}".format(below_zero_case))
print("no label count={}".format(no_label_count))

fd.close()
print("finish code")


