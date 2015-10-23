""" unit and functional tests for the pdfexploder application
"""
import os
import sys
import shutil
import logging
import unittest
import transaction

from pyramid import testing

from webtest import TestApp, Upload

from slugify import slugify

from coverageutils import file_range, size_range
from pdfexploder.thumbnailgenerator import ThumbnailGenerator


# Specify stdout as the logging output stream to reduce verbosity in the
# nosetest output. This will let you still see all of logging when
# running with python -u -m unittest, yet swallow it all in nosetest.
log = logging.getLogger()
log.setLevel(logging.INFO)
strm = logging.StreamHandler(sys.stdout)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)

class DeformMockFieldStorage(object):
    """ Create a storage object that references a file for use in
    view unittests. Deform/colander requires a dictionary to address the
    multiple upload fields. This is not required for 'plain' html file
    uploads.
    """
    def __init__(self, source_file_name):
        self.filename = source_file_name
        self.file = file(self.filename)
        self.type = "file"
        self.length = os.path.getsize(self.filename)


class TestCoverageUtils(unittest.TestCase):
    def test_file_does_not_exist(self):
        filename = "known_unknown_file"
        self.assertFalse(file_range(filename, 10000))

    def test_file_sizes_out_of_range(self):
        filename = "resources/known_unittest.pdf"
        self.assertFalse(file_range(filename, 1250000)) #small
        self.assertFalse(file_range(filename, 1190000)) #large

class TestThumbnailGenerator(unittest.TestCase):
    def test_invalid_pdf_throws_exception(self):
        filename = "knowndoesnotexist"
        self.assertRaises(IOError, ThumbnailGenerator, filename)

    def test_valid_pdf_does_not_throw_exception(self):
        filename = "resources/known_unittest.pdf"
        thumg = ThumbnailGenerator(filename)
        self.assertEqual(filename, thumg.filename)

    def test_top_page_thumbnail_from_pdf(self):
        filename = "resources/known_unittest.pdf"
        thumg = ThumbnailGenerator(filename)
        png_img = thumg.top_thumbnail()
        img_size = len(png_img)
        self.assertTrue(size_range(img_size, 105238, ok_range=5000))

    def test_mosaic_thumbnail_from_pdf(self):
        filename = "resources/known_unittest.pdf"
        thumg = ThumbnailGenerator(filename)
        png_img = thumg.mosaic_thumbnail()
        # Image has randomized components
        self.assertTrue(size_range(len(png_img), 21000, ok_range=2000))

class TestThumbnailViews(unittest.TestCase):
    def setUp(self):
        # Clean any existing test files
        self.clean_test_files()
        self.config = testing.setUp()

    def tearDown(self):
        # Comment out this line for easier post-test state inspections
        #self.clean_test_files()
        testing.tearDown()

    def clean_test_files(self):
        # Remove the directory if it exists
        test_serials = ["ut1234"]

        for item in test_serials:
            dir_out = "thumbnails/%s" % slugify(item)
            if os.path.exists(dir_out):
                shutil.rmtree(dir_out)
        
    def test_get_returns_default_form(self):
        from pdfexploder.views import ThumbnailViews
        request = testing.DummyRequest()
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
        self.assertIsNone(result.get("appstruct"))

    def test_serial_missing_or_empty_is_failure(self):
        from pdfexploder.views import ThumbnailViews

        post_dict = {"submit":"submit"}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
        self.assertIsNone(result.get("appstruct"))

        post_dict = {"submit":"submit", "serial":""}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
        self.assertIsNone(result.get("appstruct"))

    def test_file_missing_or_empty_is_failure(self):
        from pdfexploder.views import ThumbnailViews

        post_dict = {"submit":"submit", "serial":"UT1234"}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
        self.assertIsNone(result.get("appstruct"))

        pdf_upload_dict = {"upload":""}
        post_dict = {"submit":"submit", "serial":"UT1234",
                     "pdf_upload":pdf_upload_dict}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
        self.assertIsNone(result.get("appstruct"))

    def test_serial_and_file_is_passing(self):
        from pdfexploder.views import ThumbnailViews

        pdf_name = "resources/known_unittest.pdf"
        pdf_file = DeformMockFieldStorage(pdf_name)
        pdf_upload_dict = {"upload":pdf_file}
 
        post_dict = {"submit":"submit", "serial":"UT1234",
                     "pdf_upload":pdf_upload_dict}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
        self.assertIsNotNone(result.get("appstruct"))
       
        appstruct = result.get("appstruct") 
        self.assertEqual(appstruct["serial"], post_dict["serial"])

        up_name = appstruct["pdf_upload"]["fp"].name
        mock_name = pdf_file.filename

        self.assertEqual(up_name, mock_name)

    def test_post_serial_and_pdf_uploads_file_to_hardcoded_name(self):
        from pdfexploder.views import ThumbnailViews

        pdf_name = "resources/known_unittest.pdf"
        pdf_file = DeformMockFieldStorage(pdf_name)
        pdf_upload_dict = {"upload":pdf_file}
 
        post_dict = {"submit":"submit", "serial":"UT1234",
                     "pdf_upload":pdf_upload_dict}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
       
        dest_top = "thumbnails/ut1234/uploaded.pdf"
        self.assertTrue(file_range(dest_top, 1210163))

    def test_correct_post_generates_thumbnails_on_disk(self):
        from pdfexploder.views import ThumbnailViews

        pdf_name = "resources/known_unittest.pdf"
        pdf_file = DeformMockFieldStorage(pdf_name)
        pdf_upload_dict = {"upload":pdf_file}
 
        post_dict = {"submit":"submit", "serial":"UT1234",
                     "pdf_upload":pdf_upload_dict}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()
       
        dest_top = "thumbnails/ut1234/top.png"
        self.assertTrue(file_range(dest_top, 105238, ok_range=5000))
       
        dest_top = "thumbnails/ut1234/mosaic.png"
        self.assertTrue(file_range(dest_top, 21000, ok_range=2000))

    def test_post_view_of_thumbnails_files_accessible(self):
        from pdfexploder.views import ThumbnailViews

        pdf_name = "resources/known_unittest.pdf"
        pdf_file = DeformMockFieldStorage(pdf_name)
        pdf_upload_dict = {"upload":pdf_file}
 
        post_dict = {"submit":"submit", "serial":"UT1234",
                     "pdf_upload":pdf_upload_dict}
        request = testing.DummyRequest(post_dict)
        inst = ThumbnailViews(request)
        result = inst.generate_thumbnails()

        request = testing.DummyRequest()
        request.matchdict["serial"] = "UT1234"
        inst = ThumbnailViews(request)

        result = inst.top_thumbnail()
        img_size = result.content_length
        self.assertTrue(size_range(img_size, 105238, ok_range=5000))

        # Mosaic has randomization
        result = inst.mosaic_thumbnail()
        img_size = result.content_length
        self.assertTrue(size_range(img_size, 21000, ok_range=2000))
        

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.clean_test_files()
        from pdfexploder import main
        settings = {}
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp

    def clean_test_files(self):
        # Remove the directory if it exists
        test_serials = ["ft789"]

        for item in test_serials:
            dir_out = "thumbnails/%s" % slugify(item)
            if os.path.exists(dir_out):
                shutil.rmtree(dir_out)

    def test_home_form_starts_empty_placeholders_visible(self):
        res = self.testapp.get("/")
        self.assertEqual(res.status_code, 200)

        form = res.forms["deform"]
        self.assertEqual(form["serial"].value, "")

        indexed_form_name = form.get("upload", 0).name
        self.assertEqual(indexed_form_name, "upload")

        match_mosaic = "assets/img/known_mosaic_image.png"
        self.assertTrue(match_mosaic in res.body)

        match_top = "assets/img/known_top_image.png"
        self.assertTrue(match_top in res.body)

    def test_imagery_placeholders_are_accessible(self):
        res = self.testapp.get("/assets/img/known_top_image.png")
        self.assertEqual(res.status_code, 200)

        res = self.testapp.get("/assets/img/known_mosaic_image.png")
        self.assertEqual(res.status_code, 200)

    def test_submit_with_no_values_has_error_messages(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with your" in submit_res.body) 

    def test_submit_with_serial_but_no_pdf_has_error_message(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form["serial"] = "okserial"
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with your" in submit_res.body) 

    def test_submit_with_pdf_but_no_serial_has_error_message(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form.set("upload", Upload("resources/known_unittest.pdf"), 0)
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with your" in submit_res.body)

    def test_submit_with_all_values_has_no_error_messages(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form["serial"] = "ft789"
        form.set("upload", Upload("resources/known_unittest.pdf"), 0)
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with" not in submit_res.body)

    def test_submit_with_all_values_image_links_available(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form["serial"] = "ft789"
        form.set("upload", Upload("resources/known_unittest.pdf"), 0)
        submit_res = form.submit("submit")

        top_link = "src=\"/top/ft789"
        self.assertTrue(top_link in submit_res.body)
 
        res = self.testapp.get("/top/ft789")
        img_size = res.content_length
        self.assertTrue(size_range(img_size, 105238, ok_range=5000))
        
        mosaic_link = "src=\"/mosaic/ft789"
        self.assertTrue(mosaic_link in submit_res.body)

        res = self.testapp.get("/mosaic/ft789")
        img_size = res.content_length
        self.assertTrue(size_range(img_size, 21000, ok_range=2000))
