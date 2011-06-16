#!/usr/bin/env python
#    Copyright (C)  University of Southern Queensland
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from django.shortcuts import render_to_response
from triplink import TripLink, Triple
from urlparse import urlsplit, parse_qs

def ontologize(request):
    
    #url = request.URL
    url = request.build_absolute_uri()
    if request.META.has_key("HTTP_REFERER"):
        ref  =  request.META["HTTP_REFERER"]
    else:
        ref = "[unknown referring page]"
    
    tripll = TripLink()
    data =  tripll.process(url,referer=ref )
    if data:
        statement = data["statement"]
        rdfa = data["RDFaTemplate"]
        data['url'] = url
        
        
    
        
    
    
    
    return render_to_response('ont.html', data) 


#Legacy code from original ontologize me



rels = {
     	"http://purl.org/dc/terms/creator" : "has a Dublin Core creator",
	    "http://purl.org/dc/terms/dateCopyrighted" : "has a Dublin Core date copyrighted",
        "http://purl.org/dc/terms/description" : "has a Dublin Core description",
        "http://purl.org/dc/terms/hasFormat" : "has a Dublin Core formnat",

    }

def getRelName(rel):
	if rels.has_key(rel):
       		return rels[rel]
	else:
		return rel




def meta(request, template_name="meta.html"):
    """
    decode a metadata triple
    """
   
    r = ""
    if request.method == "GET":
        try:
    		r = request.GET["r"]
        except:
  		r= "none"
	r = getRelName(r)
        try:
        	o = request.GET["o"]
	except:
		o = "nothing"
        if request.META.has_key("HTTP_REFERER"):
       		s =  request.META["HTTP_REFERER"]
	else:
		s = "&lt;unknown referring page>"
    
    return render_to_response(template_name, {"r" : r, "s" : s, "o" : o,})
    	




#Hello ['COOKIES', 'FILES', 'GET', 'META', 'POST', 'REQUEST', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_cookies', '_encoding', '_get_cookies', '_get_encoding', '_get_files', '_get_get', '_get_post', '_get_raw_post_data', '_get_request', '_get_upload_handlers', '_initialize_handlers', '_load_post_and_files', '_post_parse_error', '_set_cookies', '_set_encoding', '_set_get', '_set_post', '_set_upload_handlers', '_upload_handlers', 'build_absolute_uri', 'encoding', 'environ', 'get_full_path', 'get_host', 'is_ajax', 'is_secure', 'method', 'parse_file_upload', 'path', 'path_info', 'raw_post_data', 'session', 'upload_handlers', 'user'] 
