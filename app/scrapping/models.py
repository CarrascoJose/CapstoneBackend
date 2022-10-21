from django.db import models


class Basket(models.Model):
    """ Track a basket request and its results"""
    basket = models.JSONField()
    ranking = models.JSONField(default = list,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=200, blank=True)
    

