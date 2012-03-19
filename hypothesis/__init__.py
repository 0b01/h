#!/usr/bin/env python

routes = [
    ('home', '/')
]

def create_app(config):
    config.include('hypothesis.assets')
    config.include('hypothesis.models')
    config.include('hypothesis.views')

    for view, path in routes:
        config.add_route(view, path)

    return config.make_wsgi_app()
