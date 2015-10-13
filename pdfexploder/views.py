import os
import shutil
import logging

from pyramid.response import Response, FileResponse
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from slugify import slugify

from wand.image import Image

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
        serial = "unspecified"
        try:
            serial = self.request.matchdict["serial"]
        except KeyError:
            log.warn("No serial key specified")

        self.request.matchdict["serial"] = slugify(serial)

    @view_config(route_name="add_pdf",
                 renderer="templates/add_pdf.pt")
    def add_pdf(self):
        """ Display the pdf addition form, accept an uploaded file and
        generation thumbnail representations.
        """
        if "form.submitted" in self.request.params:
            if "serial" not in self.request.params:
                log.critical("Must submit a serial")
                return HTTPNotFound()

            serial = self.request.POST["serial"] 
            if serial == "":
                log.critical("Must populate serial")
                return HTTPNotFound()

            file_content = self.request.POST["file_content"]
            filename = file_content.filename
            self.write_file(serial, "original.pdf", file_content.file)
            self.generate_pdf_thumbnail(serial)
            self.generate_mosaic_thumbnail(serial)
        
            return dict(serial=serial, filename=filename)
             
            
        return dict(serial="", filename="")

    def generate_mosaic_thumbnail(self, serial):
        """ Convert the uploaded pdf to a wide image of overlaid, titled
        pages for display as a sort of line of polaroids.
        """
        pdf_filename = "%s/%s/original.pdf" % (self.prefix, serial)
        tile_dir = "%s/%s/tiles/" % (self.prefix, serial)
        temp_file = "%s/%s/top_thumbnail.png" % (self.prefix, serial)

        # delete any previously generated tiles
        if os.path.exists(tile_dir):
            log.info("Deleting previous tile dir")
            shutil.rmtree(tile_dir)

        else:
            log.info("Make tile directory: %s", tile_dir)
            os.makedirs(tile_dir)
        

        # Convert pdf to pngs
        pagecount = 0
        with Image(filename=pdf_filename) as img:
            img.resize(306, 396)
            save_filename = "%s/wt_%s.png" % (tile_dir, pagecount)
            pagecount += 1

        
        #log.info("Combine into polaroid row")
        #cmd_options = ['montage', 'null:', 'wt_*.png', 'null:', '+polaroid',
        #              '-gravity', 'center', '-tile', '9x1',  '-geometry',
        #              '-50+2', '-resize', '30%', 'polaroid_overlap.jpg']
        
        

    def generate_pdf_thumbnail(self, serial):
        """  Convert the first page of the designated pdf to png format
        using imagemagick.
        """
        pdf_filename = "%s/%s/original.pdf[0]" % (self.prefix, serial)
        temp_file = "%s/%s/top_thumbnail.png" % (self.prefix, serial)

        with Image(filename=pdf_filename) as img:
            img.resize(306, 396)
            img.save(filename=temp_file)

        log.info("Saved top thumbnail")

    def write_file(self, serial, destination, upload_file):
        """ With file from the post request, write to a temporary file,
        then ultimately to the destination specified.
        """
        temp_file = "database/temp_file"
        upload_file.seek(0)
        with open(temp_file, "wb") as output_file:
            shutil.copyfileobj(upload_file, output_file)

        # Create the directory if it does not exist
        final_dir = "%s/%s" % (self.prefix, serial)
        if not os.path.exists(final_dir):
            log.info("Make directory: %s", final_dir)
            os.makedirs(final_dir)

        final_file = "%s/%s" % (final_dir, destination)

        os.rename(temp_file, final_file)
        log.info("Saved file: %s" % final_file)

    @view_config(route_name="top_thumbnail")
    def top_thumbnail(self):
        """ Display the top page thumbnail of the specified pdf if it
        exists.
        """
        file_name = "%s/%s/top_thumbnail.png" \
                    % (self.prefix, self.serial)
        location = "%s/top_placeholder.png" % self.prefix

        if os.path.exists(file_name):
            location = file_name

        return FileResponse(location)

    @view_config(route_name="mosaic_thumbnail")
    def mosaic_thumbnail(self):
        """ Display the mosaic multi page thumbnail of the pdf if it
        exists.
        """
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

