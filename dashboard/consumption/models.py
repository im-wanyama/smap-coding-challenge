# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone


class User_data(models.Model):

    id = models.IntegerField(primary_key=True)
    area = models.CharField(max_length=50)
    tariff = models.CharField(max_length=50)

    class Meta:
        db_table = "user_data"


class Consumption(models.Model):

    user_data = models.ForeignKey(User_data, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now)
    consumption = models.FloatField()

    class Meta:
        db_table = "consumption"
