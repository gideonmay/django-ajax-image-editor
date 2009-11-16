'''
Created on 10.08.2009

@author: german
'''
from django.utils.translation import ugettext as _
from django.db import models

class FolderManager(models.Manager):
    def published(self, user=None):
        return self.get_query_set().filter(user=user, public=True).exclude(images=None)

    def default(self, user=None):
        r = self.get_query_set().filter(user=user, type=0)
        n = r.count()
        if n:
            result = r[0]
            if n > 1:
                r.exclude(pk=result.pk).delete()
        else:
            result = self.model(type=0, name=_('Default folder'), description=_('Default folder for images.'))
            result.user = user
            result.save()
        return result 

    def all_galleries(self, user=None):
        return self.get_query_set().filter(user=user)
    
    def all_photo_galleries(self, user=None):
        return self.get_query_set().filter(user=user, type=1)
    
    def all_article_galleries(self, user=None):
        return self.get_query_set().filter(user=user, type=2)
    
    def photo_galleries(self, user=None):
        return self.published().filter(user=user, type=1)
    
    def article_gallerries(self, user=None):
        return self.published().filter(user=user, type=2)