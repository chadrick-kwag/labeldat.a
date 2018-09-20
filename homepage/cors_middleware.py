import re

from django.utils.text import compress_string
from django.utils.cache import patch_vary_headers

from django import http

from django.utils.deprecation import MiddlewareMixin, RemovedInDjango21Warning

try:
    import settings 
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
except:
    XS_SHARING_ALLOWED_ORIGINS = 'http://localhost:8000'
    XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']


class XsSharingMiddleware(MiddlewareMixin):
    """
        This middleware allows cross-domain XHR using the html5 postMessage API.
         

        Access-Control-Allow-Origin: http://foo.example
        Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE


    """
    # def __init__(self,get_response):
    #     self.get_response = get_response

    # def __call__(self,request):
    #     response=self.get_response(request)

    #     return response



    def process_request(self, request):

        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS ) 
            response["Access-Control-Allow-Credentials"]="true"
            response["Access-Control-Allow-Headers"]="x-csrftoken"
            
            return response

        return None

    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
        response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
        response["Access-Control-Allow-Credentials"]="true"

        return response