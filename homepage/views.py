from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
import os,sys
from django.http import HttpResponse
import json
from django.views.decorators.csrf import requires_csrf_token, ensure_csrf_cookie
from django.core.files.base import ContentFile

import uuid
import operator
from functools import reduce

# Create your views here.
@ensure_csrf_cookie
def homepage(request):
	# return render(request,'home.html',None)
	return render(request,'index.html',None)

@ensure_csrf_cookie
@login_required
def workportal(request):

	datasets = Dataset.objects.all()

	return render(request,'workportal2.html',context={'datasets':datasets})

@login_required
def dataset_summary(request,dsid):

	fetched_ds = Dataset.objects.all().filter(dsid=dsid)
	if len(fetched_ds) is not 1:
		raise ValueError
	
	single_ds = fetched_ds[0]

	ds_title = single_ds.title
	ds_desc = single_ds.description


	return render(request,'dataset_entry.html',context={'ds_id':dsid,'ds_title':ds_title,'ds_desc':ds_desc})

@ensure_csrf_cookie
@login_required
def workbench(request,dsid):
	print("workbench with dsid={}".format(dsid),file=sys.stderr)
	query = Dataset.objects.all().filter(dsid=dsid)
	
	if len( query)==0:
		print("ds query failed")
	
	ds = query[0]
	
	splitted=[]
	try:
		contents = ds.label_jsonfile.read()
		print("filename={}".format(ds.label_jsonfile.name))
		convv = contents.decode()
		print("convv  = {}".format(convv))

		splitted = convv.split('\n')

	except ValueError:
		splitted = ['car']

	
	print("splitted={}".format(splitted))


	# print("label json contents = {}".format(contents))
	return render(request,'app/workbench.html',context={'ds_id':dsid,'labellist':splitted})

@ensure_csrf_cookie
@login_required
def fetchimage(request,dsid,imgno):
	if request.method == "POST":
		return HttpResponse("")

	currentdir=os.getcwd()
	remainder = "homepage/static/datasets/imgs/"+str(dsid)
	selected_imgdir = os.path.join(currentdir,remainder)

	# check if exist
	print("selected_imgdir={}".format(selected_imgdir), file=sys.stderr)

	if os.path.isdir(selected_imgdir) and os.path.exists(selected_imgdir):
		allfiles=os.listdir(selected_imgdir)
		# print(allfiles,file=sys.stderr)
		allfiles = sorted(allfiles)

		# check if imgno is valid
		if imgno >= len(allfiles) or imgno<0:
			return HttpResponse(status=255)


		picked_file=allfiles[imgno]
		picked_file_fullpath = os.path.join(selected_imgdir,picked_file)
		# check if the image file is jpg or png
		ext = os.path.splitext(picked_file)[1]
		content_type=""
		if ext in [".jpg", ".jpeg"]:
			content_type = "image/jpeg"
		elif ext in [".png"]:
			content_type = "image/png"
		else:
			# weird extension
			print("found extension={}. strange value".format(ext),file=sys.stderr)
			return HttpResponse("image extension weird")



		with open(picked_file_fullpath,"rb") as f:
			print("sending img={}".format(picked_file_fullpath), file=sys.stderr)
			return HttpResponse(f.read(),content_type="image/jpeg")
	else:
		print("img dir doesn't exist", file=sys.stderr)
		return HttpResponse("no image file")

@ensure_csrf_cookie
@login_required
def fetch_image_numbers(request,dsid):
	currentdir=os.getcwd()
	remainder = "homepage/static/datasets/imgs/"+str(dsid)
	selected_imgdir = os.path.join(currentdir,remainder)

	# check if exist
	# print("selected_imgdir={}".format(selected_imgdir), file=sys.stderr)
	
	if os.path.isdir(selected_imgdir) and os.path.exists(selected_imgdir):
		allfiles=os.listdir(selected_imgdir)

		total_number = len(allfiles)
		returnjson={}
		returnjson["number_of_images"] = total_number

		print("sending proper data", file=sys.stderr)
		response= HttpResponse(json.dumps(returnjson),content_type="application/json")
		# response["Access-Control-Allow-Origin"]="http://localhost:8000"
		# response["Access-Control-Allow-Credentials"]="true"

		return response
	else:
		print("returning nothing due to dir not exist", file=sys.stderr)
		return HttpResponse("nothing")



# @requires_csrf_token
@ensure_csrf_cookie
@login_required
def saveprogress(request):

	# next_page = request.GET['next']
	# print("next_page = {}".format(next_page),file=sys.stderr)

	# if request.user.is_authenticated():
	# 	return HttpResponseRedirect(next_page)
	
	# get user, dsid, save data
	# with user, dsid create/locate json dump file. and register this in sql
	# the model that contains this info is 'save_progress'

	# print("body={}".format(request.body),file=sys.stderr)

	if request.body is None:
		response = HttpResponse("no body")
		# response["Access-Control-Allow-Origin"]="http://localhost:8000"
		# response["Access-Control-Allow-Credentials"]="true"

		return response

	if len(request.body) == 0:
		response = HttpResponse("body length is zero")
		# response["Access-Control-Allow-Origin"]="http://localhost:8000"
		# response["Access-Control-Allow-Credentials"]="true"
		return response



	# the request.body is a byte string. the json.loads requires unicode.


	request_jsondata = json.loads(request.body.decode('utf-8'))
	try:
		request_dsid = request_jsondata['dataset_id']
	except KeyError:
		response = HttpResponse("no dsid found in request")
		# response["Access-Control-Allow-Origin"]="http://localhost:8000"
		# response["Access-Control-Allow-Credentials"]="true"
		return response
		


	print("username={},dsid={}".format(request.user.username,request_dsid), file=sys.stderr)

	query = save_progress.objects.all().filter(username=request.user.username,dsid=request_dsid)
	print("query done",file=sys.stderr)
	print("query={}".format(query),file=sys.stderr)

	
	if len(query)==0:
		# create a new entry
		print("save progress file not exist. creating new one.",file=sys.stderr)
		newfilename = create_new_filename()
		new_progress = save_progress.objects.create(username=request.user.username, dsid=request_dsid)
		# new_progress.username = request.user.username
		# new_progress.dsid = request_dsid
		# # create new filename
		# new_progress.filename = "testfilename"

		# new_progress.savefile(newfilename,ContentFile(json.dumps(request.body.decode('utf-8'))))
		new_progress.savefile.save(newfilename,ContentFile(json.dumps(request.body.decode('utf-8'))))
	else:
		print("save progress file exists.overwriting it.",file=sys.stderr)
		queryobj = query[0]
		savefile = queryobj.savefile

		tempsavename = os.path.basename(savefile.name)
		print("tempsavename={}".format(tempsavename),file=sys.stderr)
		savefile.delete()

		savefile.save(tempsavename,ContentFile(json.dumps(request.body.decode('utf-8'))))

	

	response = HttpResponse("test response")
	# response["Access-Control-Allow-Origin"]="http://localhost:8000"
	# response["Access-Control-Allow-Credentials"]="true"

	return response


@ensure_csrf_cookie
@login_required
def getprogress(request):

	if request.method=="POST":
		if request.body is None:
			response = HttpResponse("no body")
			# response["Access-Control-Allow-Origin"]="http://localhost:8000"
			# response["Access-Control-Allow-Credentials"]="true"

			return response

		if len(request.body) == 0:
			response = HttpResponse("body length is zero")
			# response["Access-Control-Allow-Origin"]="http://localhost:8000"
			# response["Access-Control-Allow-Credentials"]="true"
			return response

		request_jsondata = json.loads(request.body.decode('utf-8'))
		#the username is inside the request. we just need to extract the dsid
		try:
			request_dsid = request_jsondata['dataset_id']
		except KeyError:
			response = HttpResponse("no dsid found in request")
			# response["Access-Control-Allow-Origin"]="http://localhost:8000"
			# response["Access-Control-Allow-Credentials"]="true"
			return response


		# update recent activity timestamp
		update_recent_activity(request.user.id, request_dsid)

		print("username={},dsid={}".format(request.user.username,request_dsid), file=sys.stderr)

		query = save_progress.objects.all().filter(username=request.user.username,dsid=request_dsid)
		print("query={}".format(query),file=sys.stderr)

		if len(query)==0:
			return HttpResponse("no query found")

		jsonfile = query[0].savefile
		readcontents = jsonfile.readlines()
		## all the json data should be contained in the first line
		firstline = readcontents[0]


		# print("readcontents={}".format(readcontents),file=sys.stderr)


		## also update recent_activity in this function as well. 
		print("user id={}".format(request.user.id),file=sys.stderr)

		

		


		
		# query = recent_activity.objects.all().filter(userid=request.user.id,dataset=fetched_ds)


		# if len(query)==0:
		# 	# first access to this ds for this user.
		# 	recent_activity.objects.create(userid=request.user.id,dataset=fetched_ds)
		# 	print("recent activity newly created",file=sys.stderr)
		# else:
		# 	# it exists
		# 	fetched_ra = query[0]
		# 	fetched_ra.save()
		# 	print("recent activity existing timestamp={}".format(fetched_ra.access_datetime),file=sys.stderr)



		print("recent activity updated",file=sys.stderr)

		
		return HttpResponse(firstline)






def create_new_filename():
	# generate random filename.
	random_filename = str(uuid.uuid4())+".json"
	if save_json_filename_exists(random_filename):
		return create_new_filename()
	else:
		return random_filename



def save_json_filename_exists(random_filename):
	# check if this exists in dir
	saveprogress_dir = os.getcwd() + "/homepage/static/saves"

	if os.path.isdir(saveprogress_dir) and os.path.exists(saveprogress_dir):
		getallfiles = os.listdir(saveprogress_dir)
		if random_filename in getallfiles:
			return True

	return False


@ensure_csrf_cookie
@login_required
def myworks(request):
	print("inside myworks")
	# query recent activity for current user
	queryset = recent_activity.objects.filter(userid=request.user.id).order_by('-access_datetime')
	# print queryset
	print("myorks queryset={}".format(queryset),file=sys.stderr)

	# fetch the savedprogress with userid, dsid
	# and then calculate the progress by extracting the finished number in savedprogress json
	# and the actual number of files in the ds img directory

	## fetch savedprogress
	print("calculating progress...")
	ra_progress_dict={}
	for RA in queryset:
		fetched_savedprogress = save_progress.objects.filter(username =request.user.username , dsid=RA.dataset.dsid)
		if len(fetched_savedprogress)==0:
			ra_progress_dict[RA]=0
			continue
		
		feched_savedprogress = fetched_savedprogress[0]

		# calculate the number of fetched_savedprogress

		jsonfile = feched_savedprogress.savefile
		readcontents = jsonfile.readlines()
		## all the json data should be contained in the first line
		firstline = readcontents[0]

		#convert this string to json
		spjson = json.loads(firstline.decode("utf-8"))
		spjson = json.loads(spjson)

		len_of_sp = len(spjson['data'])

		print("lenofsp={}".format(len_of_sp),file=sys.stderr)


		# get the length of imgs in the dataset dir

		len_of_dir=get_number_of_images(RA.dataset.dsid)

		if len_of_dir==-1:
			print("len of dir ==-1. setting percentage to 0",file=sys.stderr)
			ra_progress_dict[RA]=0
			
		else:
			# calculate percentage
			percentage = int(len_of_sp*100/len_of_dir)
			print("percnetage={}".format(percentage),file=sys.stderr)
			ra_progress_dict[RA]=percentage


	print("result of calculation={}".format(ra_progress_dict),file=sys.stderr)


	# render the RA items in html
	# return render(request,'app/myworks.html',context={'queryset':queryset})
	return render(request,'app/myworks.html',context={'queryset':ra_progress_dict})


@ensure_csrf_cookie
@login_required
def dsinfopage(request,dsid):
	# fetch data from model
	fetched_obj = Dataset.objects.all().filter(dsid=dsid)
	if len(fetched_obj) ==0 :
		return HttpResponse("no ds with that dsid found")

	fetched_ds = fetched_obj[0]
	print("fetched_ds thumbnail={}".format(fetched_ds.thumbnail_filename),file=sys.stderr)


	return render(request,'app/dataset_profile.html',context={'fetched_ds':fetched_ds}) 


@ensure_csrf_cookie
@login_required
def searchpage(request):

	if request.method == "GET":
		searchinput = request.GET.get('searchinput','')
		print("searchinput {}".format(searchinput))
		if searchinput == '':

			show_ds_set = Dataset.objects.order_by('dsid')[:20]
			print("fetched show_ds_set={}".format(show_ds_set),file=sys.stderr)
			return render(request,'app/searchpage.html',context={'show_ds_set':show_ds_set})
			# return render(request,'app/searchpage.html')
		else:
			# search ds with the keywords in it

			# split the search input
			splitted_keywords = searchinput.split(' ')

			# remove duplicate values in splitted_keywords
			splitted_keywords = set(splitted_keywords)

			print("splitted keywords ={}".format(splitted_keywords))



			# dsresult = (Dataset.objects.filter(title__icontains=q) for q in splitted_keywords)
			# dsresult = list(dsresult)[0]

			dsresult=None
			tempresult_combine=[]
			for keyword in splitted_keywords:
				# searching keyword in title
				tempresult = Dataset.objects.filter(title__icontains=keyword)
				print("tempresult for keyworkd {} = {}".format(keyword,tempresult))

				# search keyword in description
				tempresult2 = Dataset.objects.filter(description__icontains=keyword)
				tempresult_combine.extend(tempresult)
				tempresult_combine.extend(tempresult2)


				
			print("tempresult_combined={}".format(tempresult_combine))

			# deal with duplicate search results
			dsresult = set(tempresult_combine)


	


			# dsresult = Dataset.objects.filter(reduce(operator.and_, (Dataset.objects.filter(title__icontains=q) for q in splitted_keywords)) |
			# reduce(operator.and_,(Dataset.objects.filter(description__icontains=q) for q in splitted_keywords)))

			# firstwordonly = splitted_keywords[0]
			# dsresult = Dataset.objects.filter(title__icontains=firstwordonly)

			print("searched results = {}".format(dsresult))
			

			

			return render(request,'app/searchpage.html',context={'show_ds_set':dsresult})
			



	


def update_recent_activity(param_userid,param_dsid):

	print("updaing recent activity for ")

	fetch_ds_set = Dataset.objects.filter(dsid=param_dsid)

	if len(fetch_ds_set)==0:
		return None

	param_ds = fetch_ds_set[0]


	query = recent_activity.objects.all().filter(userid=param_userid,dataset=param_ds)


	if len(query)==0:
		# first access to this ds for this user.
		recent_activity.objects.create(userid=param_userid,dataset=param_ds)
		print("recent activity newly created",file=sys.stderr)
	else:
		# it exists
		fetched_ra = query[0]
		fetched_ra.save()
		print("recent activity existing timestamp={}".format(fetched_ra.access_datetime),file=sys.stderr)


def get_number_of_images(dsid):
	currentdir=os.getcwd()
	remainder = "homepage/static/datasets/imgs/"+str(dsid)
	selected_imgdir = os.path.join(currentdir,remainder)

	# check if exist
	# print("selected_imgdir={}".format(selected_imgdir), file=sys.stderr)
	
	if os.path.isdir(selected_imgdir) and os.path.exists(selected_imgdir):
		allfiles=os.listdir(selected_imgdir)

		total_number = len(allfiles)
		return total_number
	else:
		return -1