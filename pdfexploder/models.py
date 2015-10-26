""" datamodel objects used by the pdfexploder project.
"""
import colander
from deform import widget, FileData

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface
    This is from the deform2demo code: 
    https://github.com/Pylons/deformdemo/blob/master/deformdemo/\
        __init__.py
    If you attempt to make tmpstore a class of FileUploadTempStore as
    described in the stack overflow entry below, it complains about
    the missing implementation of preview_url.
    """
    def preview_url(self, uid):
        """ provide interface for schemanode
        """
        return None


class PDFUploadSchema(colander.Schema):
    """ use colander to define a data validation schema for linkage with
    a deform object.
    """
    csn = colander.SchemaNode

    serial = csn(colander.String(),
                 validator=colander.Length(3, 10))

    # Based on: # http://stackoverflow.com/questions/6563546/\
    # how-to-make-file-upload-facultative-with-deform-and-colander
    # Various demos delete this temporary file on succesful submission
    pdf_tmp_store = MemoryTmpStore()
    fuw = widget.FileUploadWidget(pdf_tmp_store)
    pdf_upload = csn(FileData(), widget=fuw)
