"""
Media file serving views for production deployment.
"""
import os
import mimetypes
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.utils.http import http_date
from django.views.decorators.vary import vary_on_headers
import stat


@require_GET
@cache_control(max_age=86400)  # Cache for 1 day
@vary_on_headers('Accept-Encoding')
def serve_media(request, path):
    """
    Serve media files in production.
    This is a simple fallback when media files can't be served by the web server.
    """
    # Security check: ensure path doesn't contain dangerous characters
    if '..' in path or path.startswith('/') or '\\' in path:
        raise Http404("Invalid path")
    
    # Build the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Normalize the path to prevent path traversal attacks
    file_path = os.path.normpath(file_path)
    
    # Check if file exists and is within media root
    try:
        if not os.path.exists(file_path) or not os.path.commonpath([settings.MEDIA_ROOT, file_path]) == settings.MEDIA_ROOT:
            raise Http404("File not found")
    except ValueError:
        # os.path.commonpath raises ValueError if paths are on different drives
        raise Http404("File not found")
    
    # Check if it's actually a file (not a directory)
    if not os.path.isfile(file_path):
        raise Http404("File not found")
    
    # Get file stats for caching headers
    try:
        file_stat = os.stat(file_path)
    except OSError:
        raise Http404("File not found")
    
    # Get the MIME type
    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Handle conditional requests (ETags, Last-Modified)
    mtime = file_stat[stat.ST_MTIME]
    size = file_stat[stat.ST_SIZE]
    
    # Create ETag based on file path, size, and modification time
    etag = f'"{hash(f"{path}-{size}-{mtime}")}"'
    
    # Check if client has cached version
    if_modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
    if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
    
    if if_none_match == etag or (if_modified_since and 
                                http_date(mtime) == if_modified_since):
        return HttpResponseNotModified()
    
    # Read and serve the file
    try:
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Set caching headers
            response['Last-Modified'] = http_date(mtime)
            response['ETag'] = etag
            response['Content-Length'] = size
            
            if encoding:
                response['Content-Encoding'] = encoding
                
            return response
    except IOError:
        raise Http404("File not found")