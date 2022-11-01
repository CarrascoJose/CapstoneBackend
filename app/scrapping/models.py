from django.db import models
from django.conf import settings

class Basket(models.Model):
    """ Track a basket request and its results"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    basket = models.JSONField()
    ranking = models.JSONField(default = list,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=200, blank=True)
    

