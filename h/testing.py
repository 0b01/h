# -*- coding: utf-8 -*-
import logging

from pyramid.view import view_config
from pyramid_layout.layout import layout_config
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.testing import DummyMailer

from h.layouts import BaseLayout

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@view_config(layout='pattern_library',
             renderer='h:templates/pattern_library.pt',
             route_name='pattern_library')
def page(context, request):
    return {}


@layout_config(name='pattern_library', template='h:templates/base.pt')
class PatternLibraryLayout(BaseLayout):
    requirements = (
        ('app', None),
        ('inject_css', None),
    )


class LoggingMailer(DummyMailer):
    def __init__(self):
        super(LoggingMailer, self).__init__()

    def send(self, message):
        if not message.sender:
            message.sender = 'fake@localhost'
        super(LoggingMailer, self).send(message)
        log.info('sent: %s', message.to_message().as_string())

    def send_immediately(self, message, fail_silently=False):
        if not message.sender:
            message.sender = 'fake@localhost'
        super(LoggingMailer, self).send_immediately(message, fail_silently)
        log.info('sent immediately: %s', message.to_message().as_string())

    def send_to_queue(self, message):
        if not message.sender:
            message.sender = 'fake@localhost'
        super(LoggingMailer, self).send_to_queue(message)
        log.info('queued: %s', message.to_message().as_string())


def includeme(config):
    config.include('pyramid_layout')

    config.add_route('pattern_library', '/dev/pattern-library')

    mailer = LoggingMailer()
    config.registry.registerUtility(mailer, IMailer)

    config.scan(__name__)
