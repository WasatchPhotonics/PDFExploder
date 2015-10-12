import unittest
import transaction

from pyramid import testing

from .models import DBSession


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
        pass

    def tearDown(self):
        pass

    def test_unexisting_top_page_thumbnail(self):
        # Request the top of the pdf thumbnail, expect a placeholder png
        # if that device does not exist on disk
        from pdfexploder.views import ThumbnailViews

        request = testing.DummyRequest()
        request.matchdict["serial"] = "BADDevice123"
        inst = ThumbnailViews(request)
        view_back = inst.top_page_thumbnail()

        self.assertEqual(len(view_back.body), 1234)
        

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
