import datetime
import hashlib
import urllib

from nexathan import auth
from nexathan.auth.signals import user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.manager import EmptyManager
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import constant_time_compare

# Create your models here.

class SourceRCS(models.Model):
    """
    revision control system for source code, e.g. git, svn, cvs, etc
    """
    name = models.CharField(_('name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    description = models.CharField(_('description'), max_length=255, unique=False, help_text=_("Required. 255 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    

class Project(models.Model):
    """
    For a project, nexathan includes several project management components for users, like ticket system, wiki, etc
    
    A project may include one or multiple components, it may have multiple versions. we use this table to store a regular project, 
    the components of a projects and versions of a project
    """
    name = models.CharField(_('name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    description = models.TextField(_('description'),help_text=_("project description"))
    
    # if this is a project version, it is the project id, otherwise (general project or component), this is -1
    project = models.IntegerField('project', db_index=True, default=-1);
    is_released = models.BooleanField(_('isReleased'), default=False, help_text=_("Designates whether this version is released or not"))
    # if this is a released version, the last_update time is the release time
    
    # if this is a project component, it is the project id, otherwise (general project or version), this is -1
    parent = models.IntegerField('project', db_index=True, default=-1);
    
    is_public = models.BooleanField(_('staff status'), default=False, help_text=_("Designates whether the it is public available or not."))
    is_active = models.BooleanField(_('active'), default=True, help_text=_("Designates whether this is ongoing or finished"))
    last_update = models.DateTimeField(_('last update'), default=datetime.datetime.now)
    date_created = models.DateTimeField(_('date created'), default=datetime.datetime.now)
    
    repository = models.ForeignKey(SourceRCS)
    repository_url = models.URLField(_('repo URL'), verify_exists=False, max_length=255, help_text=_("Optional SOURCE Repository URL"))
    
    """
    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __unicode__(self):
        return self.name
    
    def is_project(self):
        return self.project == -1 and self.parent == -1
    
    def is_version(self):
        return self.project != -1
    
    def is_component(self):
        return self.parent != -1
        """


class ProjectDependency(models.Model):
    """
    For the project/component dependency graph
    """
    parent = models.ForeignKey(Project, related_name='ProjectDepencency_parent')
    child = models.ForeignKey(Project, related_name='ProjectDepencency_child')
    
