import os
import sys
import shutil
import logging

import colander

from pyramid.response import Response, FileResponse
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from deform import Form
from deform.exception import ValidationFailure

from slugify import slugify

from pdfexploder.models import PDFUploadSchema, EmptyThumbnails
from pdfexploder.thumbnailgenerator import ThumbnailGenerator

log = logging.getLogger(__name__)

class ThumbnailViews(object):
    """ Return png objects from disk where the serial number is found,
    otherwise return placeholder imagery.
    """
    def __init__(self, request):
        self.request = request

    @view_config(route_name="top_thumbnail")
    def top_thumbnail(self):
        """ Return the file on disk.
        """
        serial = slugify(self.request.matchdict["serial"])
        filename = "thumbnails/%s/top.png" % serial
        return FileResponse(filename)

    @view_config(route_name="mosaic_thumbnail")
    def mosaic_thumbnail(self):
        """ Return the file on disk.
        """
        serial = slugify(self.request.matchdict["serial"])
        filename = "thumbnails/%s/mosaic.png" % serial
        return FileResponse(filename)

    @view_config(route_name="generate_thumbnails",
                 renderer="templates/pdfexploder_form.pt")
    def generate_thumbnails(self):
        """ Display the form on get, on submission, save the uploaded
        pdf to the "serial" directory, and return the form populated 
        along with the generated thumbnails.
        """
        form = Form(PDFUploadSchema(), buttons=("submit",))
        data = EmptyThumbnails()

        if "submit" in self.request.POST:
            #log.info("submit: %s", self.request.POST)

            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
                rendered_form = form.render(appstruct)

                self.write_upload_files(appstruct)
                self.write_thumbnails(appstruct)

                return {"form":rendered_form, "appstruct":appstruct}

            except ValidationFailure as e: 
                log.info("Validation failure")
                return {'form':e.render()} 

        return {"form":form.render()}

    def write_thumbnails(self, appstruct):
        """ Create the output filenames and generate the top and mosaic
        thumbnails and write them to disk.
        """
        slugser = slugify(appstruct["serial"])
        pdf_filename = "thumbnails/%s/uploaded.pdf" % slugser
        top_file = "thumbnails/%s/top.png" % slugser
        mos_file = "thumbnails/%s/mosaic.png" % slugser
                        
        thumg = ThumbnailGenerator(pdf_filename)
        self.save_blob(thumg.top_thumbnail(), top_file)
        self.save_blob(thumg.mosaic_thumbnail(), mos_file)

    def save_blob(self, img_blob, filename):
        """ Expect a binary blob of image data from wand and a filename.
        Write the binary blob to the file.
        """
        out_file = open(filename, "wb")
        out_file.write(img_blob)
        out_file.close()

    def write_upload_files(self, appstruct):
        """ With parameters in the post request, create a destination
        directory then write the uploaded file to a hardcoded filename.
        """
 
        # Create the directory if it does not exist
        final_dir = "thumbnails/%s" % slugify(appstruct["serial"])
        if not os.path.exists(final_dir):
            log.info("Make directory: %s", final_dir)
            os.makedirs(final_dir)

        final_file = "%s/uploaded.pdf" % final_dir
        file_pointer = appstruct["pdf_upload"]["fp"]
        self.single_file_write(file_pointer, final_file)

    def single_file_write(self, file_pointer, filename):
        """ Read from the file pointer, write intermediate file, and
        then copy to final destination.
        """
        temp_file = "resources/temp_file"

        file_pointer.seek(0)
        with open(temp_file, "wb") as output_file:
            shutil.copyfileobj(file_pointer, output_file)

        os.rename(temp_file, filename)
        log.info("Saved file: %s", filename) 
