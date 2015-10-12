import os
import logging

from pyramid.response import Response, FileResponse
from pyramid.view import view_config

from slugify import slugify


from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )

log = logging.getLogger(__name__)


@view_config(route_name="home", renderer="templates/mytemplate.pt")
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == "one").first()
    except DBAPIError:
        return Response(conn_err_msg, content_type="text/plain", status_int=500)
    return {"one": one, "project": "pdfexploder"}

class ThumbnailViews:
    """ Return png objects from disk where the serial number is found,
    otherwise return placeholder imagery.
    """
    def __init__(self, request):
        print "init request: %r" % request
        self.request = request

        self.sanitize_parameters()
        #log.info("About to try serial assignment")
        self.serial = self.request.matchdict["serial"]
        self.prefix = "database/imagery"
        #log.info("Setup with serial %s", self.serial)

    def sanitize_parameters(self):
        """ slugify the parameters to prevent relative path names in the
        system.
        """
        #log.info("Sanitize parameters")
        serial = self.request.matchdict["serial"]
        self.request.matchdict["serial"] = slugify(serial)

    @view_config(route_name="top_thumbnail")
    def top_thumbnail(self):
        file_name = "%s/%s/top_thumbnail.png" \
                    % (self.prefix, self.serial)
        location = "%s/top_placeholder.png" % self.prefix

        if os.path.exists(file_name):
            location = file_name

        return FileResponse(location)

    @view_config(route_name="mosaic_thumbnail")
    def mosaic_thumbnail(self):

        file_name = "%s/%s/mosaic_thumbnail.png" \
                    % (self.prefix, self.serial)
        location = "%s/mosaic_placeholder.png" % self.prefix

        if os.path.exists(file_name):
            location = file_name

        return FileResponse(location)
                       

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_pdfexploder_db" script
    to initialize your database tables.  Check your virtual
    environment"s "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

