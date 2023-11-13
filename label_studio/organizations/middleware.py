"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging

from django.conf import settings
from django.contrib import auth
from users.models import User
from users.functions import login
from organizations.models import Organization

logger = logging.getLogger(__name__)


class DummyGetSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org = Organization.objects.first()
        user = request.user
        # auto login in
        if user is None or user.is_authenticated==False:
            email = settings.DEFAULT_USER_NAME
            password = settings.DEFAULT_USER_PASSWORD
            # advanced way for user auth
            if email and password:
                user = settings.USER_AUTH(User, email, password)
                # regular access
                if user is None:
                    user = auth.authenticate(email=email, password=password)
                if user and user.is_authenticated:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        if user and user.is_authenticated and user.active_organization is None:
            user.active_organization = org
            user.save(update_fields=['active_organization'])
        if org is not None:
            request.session['organization_pk'] = org.id
        response = self.get_response(request)
        return response
