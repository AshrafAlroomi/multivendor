import datetime

from django.db import models
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ArchiveModel(models.Model):
    class Meta:
        abstract = True

    archived = models.BooleanField(default=False)
    archived_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='archive_user', blank=True, null=True)
    archived_date = models.DateTimeField(null=True, blank=True)


class ArchiveDeleter:
    def delete(self, *args, **kwargs):
        if "user" in kwargs:
            self.archived_date = datetime.datetime.now()
            self.archived = True
            self.archived_by = kwargs["user"]
            self.save()
        else:
            raise Exception("user not provided")


class BasicArchiveView(APIView):
    model = None

    def delete(self, request, pk, format=None):
        if self.model != None:
            instance = self.model.objects.get(pk=pk)
            instance.delete(user=request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Model not implemented")
