from django.conf.urls import url
from django.urls import path,include

from . import views


urlpatterns = [
	path('',views.homepage,name='home'),
	# path('workportal',views.workportal,name='workportal'),
	path('workportal',views.myworks,name='workportal'),
	# url(r'ds_summary/<int:dsid>/',views.dataset_summary,name='dssummary'),
	path('ds_summary/<int:dsid>',views.dataset_summary,name='dssummary'),
	path('workbench/<int:dsid>',views.workbench,name='workbench'),
	path('web/<int:dsid>/img/<int:imgno>',views.fetchimage,name='fetch-image'),
	path('web/<int:dsid>/info',views.fetch_image_numbers,name='fetch-image-total-number'),
	path('web/save',views.saveprogress,name='save_progress'),
	path('progress',views.getprogress,name='get_progress'),
	path('myworks',views.myworks,name='myworks'),
	path('dataset/info/<int:dsid>',views.dsinfopage,name='dsinfopage'),
	path('search',views.searchpage,name='searchpage'),
]