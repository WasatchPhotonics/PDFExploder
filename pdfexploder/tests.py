import os
import sys
import shutil
import logging
import unittest
import transaction

from pyramid import testing

from .models import DBSession

log = logging.getLogger()                                                             
log.setLevel(logging.DEBUG)                                                           
                                                                                      
strm = logging.StreamHandler(sys.stderr)                                              
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")                      
strm.setFormatter(frmt)                                                               
log.addHandler(strm)    

class TestMyViewSuccessCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_passing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'pdfexploder')

class TestThumbnailView(unittest.TestCase):
    def setUp(self):
        # Clean any existing test files
        self.clean_test_files()

    def tearDown(self):
        self.clean_test_files()

    def clean_test_files(self):
        # Remove the directory if it exists
        dir_out = "database/imagery/test0123"
        if os.path.exists(dir_out):
            result = shutil.rmtree(dir_out)
            self.assertIsNone(result)

    def test_unexisting_top_page_thumbnail(self):
        from pdfexploder.views import ThumbnailViews
        # Request the top of the pdf thumbnail, expect a placeholder png
        # if that device does not exist on disk

        # Get size of actual file on disk, compare
        file_name = "database/imagery/top_page_placeholder.png"
        actual_size = os.path.getsize(file_name)

        request = testing.DummyRequest()
        request.matchdict["serial"] = "BADDevice123"
        inst = ThumbnailViews(request)
        view_back = inst.top_page_thumbnail()

        self.assertEqual(view_back.content_length, actual_size)
        self.assertEqual(view_back.content_type, "image/png")
        
        # Specify a known existing file with a relative pathname, verify
        # it is unavailable by expecting the file size of the
        # placeholder image
        file_name = "database/imagery/../_empty_directory_required_"
        request.matchdict["serial"] = file_name 
        inst = ThumbnailViews(request)
        view_back = inst.top_page_thumbnail()
        
        self.assertEqual(view_back.content_length, actual_size)
        self.assertEqual(view_back.content_type, "image/png")

    def test_existing_top_page_thumbnail(self):
        from pdfexploder.views import ThumbnailViews
        # Add a known file into the imagery folder
        serial = "test0123" # slug-friendly serial
        dir_name = "database/imagery/%s" % serial
        dest_file = "%s/top_page_thumbnail.png" % dir_name
        src_file = "database/imagery/known_top_image.png"

        result = os.makedirs(dir_name)
        result = shutil.copy(src_file, dest_file) 

        # Verify that it can be viewed
        request = testing.DummyRequest()
        request.matchdict["serial"] = serial
        inst = ThumbnailViews(request)
        view_back = inst.top_page_thumbnail()

        actual_size = os.path.getsize(src_file)
        self.assertEqual(view_back.content_length, actual_size)
        self.assertEqual(view_back.content_type, "image/png")


class TestMyViewFailureCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_failing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info.status_int, 500)
