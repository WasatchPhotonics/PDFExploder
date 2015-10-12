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


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'pdfexploder'}

class ThumbnailViews:
    """ Return png objects from disk where the serial number is found,
    otherwise return placeholder imagery.
    """
    def __init__(self, request):
        self.request = request
        self.sanitize_parameters()

    def sanitize_parameters(self):
        """ slugify the parameters to prevent relative path names in the
        system.
        """
        #log.info("Pre-sanitize: %s", self.request.matchdict["serial"])
        serial = self.request.matchdict["serial"]
        self.request.matchdict["serial"] = slugify(serial)
        #log.info("post-sanitize: %s", self.request.matchdict["serial"])

    @view_config(route_name="top_page_thumbnail")
    def top_page_thumbnail(self):

        file_name = "database/imagery/%s/top_page_thumbnail.png" \
                    % self.request.matchdict["serial"]
        location = "database/imagery/top_page_placeholder.png"

        if os.path.exists(file_name):
            location = file_name

        return FileResponse(location)

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_pdfexploder_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

