from django.db import models

class Basket(models.Model):
    """ Track a basket request and its results"""
    basket = models.JSONField()
    first_market = models.CharField(max_length=20,default="Pending...")
    second_market = models.CharField(max_length=20,default="Pending...")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


