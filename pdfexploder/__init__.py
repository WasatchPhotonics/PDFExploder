""" Defines application main, routes and configuration options for the
pyramid application.
"""
from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. Check the
    config/.ini files for more information.
    """
    config = Configurator(settings=settings)
    config.include("pyramid_chameleon")
    config.add_static_view("assets", "assets", cache_max_age=3600)
    config.add_route("generate_thumbnails", "/")
    config.add_route("top_thumbnail", "/top/{serial}")
    config.add_route("mosaic_thumbnail", "/mosaic/{serial}")
    config.scan()
    return config.make_wsgi_app()
