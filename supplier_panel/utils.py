from functools import wraps
from django.http import HttpResponseRedirect
from accounts.models import Profile
from django.shortcuts import render, redirect

from django.contrib import messages


def vendor_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated and request.user.is_anonymous:
            return redirect('accounts:login')

        profile = Profile.objects.get(user=request.user).status

        if profile == "vendor":

            return function(request, *args, **kwargs)
        else:

            return HttpResponseRedirect('/')

    return wrap
