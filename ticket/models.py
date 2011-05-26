import datetime
import hashlib
import urllib

from nexathan.auth.models import User
from nexathan.auth.models import Group
from nexathan.project.models import Project
from nexathan.auth.signals import user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.manager import EmptyManager
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import constant_time_compare

# Create your models here.
class TicketCategory(models.Model):
    """ 
    the category of a ticket, which could be a bug report, a feature/improvement request, document request, 
    limitation complaint, a task, or a story. This is configurable from users, like add a new 
    ticket category
    """
    name = models.CharField(_('name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    # a category could be project-specific
    # we use foreign key, the default is 0, which means 
    project = models.IntegerField(_("project_id"), default=0, help_text=_("project-specific category, default: 0, i.e. for all projects"))
    #the default assignee for a specific category ticket if not provided
    assignee = models.IntegerField(_("default_assignee"), default=-1)
    
class TicketStatus(models.Model):
    """ 
    the status of a ticket, which could be New, In Progress, Locked, Resolved, Feedback, Closed, Rejected. This is configurable from users, like add a new 
    ticket status
    """
    name = models.CharField(_('name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    # a category could be project-specific
    # we use foreign key, the default is 0, which means 
    project = models.IntegerField(_("project_id"), default=0, help_text=_("project-specific category, default: 0, i.e. for all projects"))
    #the default assignee for a specific ticket status if not provided
    assignee = models.IntegerField(_("default_assignee"), default=-1)
    
class TicketPriority(models.Model):
    """ 
    the priority of a ticket, which could be Blocker, Critical, Major, Minor, Trivial. This is configurable from users, like add a new 
    ticket priority
    """
    name = models.CharField(_('name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    # a category could be project-specific
    # we use foreign key, the default is 0, which means 
    project = models.IntegerField(_("project_id"), default=0, help_text=_("project-specific category, default: 0, i.e. for all projects"))
    #the default assignee for a specific ticket priority if not provided
    assignee = models.IntegerField(_("default_assignee"), default=-1)
    
class Environment(models.Model):
    """
    A configuration environment for a project, ticket, or others. It includes information such as OS, compiler, architecture
    """
    name = models.CharField(_('name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    
    arch = models.CharField(_("arch"), max_length=30)
    os = models.CharField(_("os"), max_length=30)
    compiler = models.CharField(_("compiler"), max_length=30)
    description = models.TextField(_('description'),help_text=_("more description of the environment"))
    
class Ticket(models.Model):
    """
    A ticket, which could be a bug report, a feature/improvement request, document request, 
    limitation complaint, a task, or a story
    """

    reporter = models.ForeignKey(User, related_name='Ticket_reporter')
    project = models.ForeignKey(Project, related_name='Ticket_project')
    assignee = models.ForeignKey(User, related_name='Ticket_assignee')
    category = models.ForeignKey(TicketCategory, related_name='Ticket_category')
    status = models.ForeignKey(TicketStatus, related_name='Ticket_status')
    priority = models.ForeignKey(TicketPriority, related_name='Ticket_priority')
    due_date = models.DateTimeField(_('due date'), default=datetime.datetime.now, help_text=_("no text"))
    milestone = models.IntegerField(_('milestone'), default=-1)
    
    affected_versions = models.CommaSeparatedIntegerField(_('affected versions'), max_length=256)
    fixed_versions = models.CommaSeparatedIntegerField(_('fixed versions'), max_length=256)
    components = models.CommaSeparatedIntegerField(_('components'), max_length=256)
    # the tickets this one depends on
    dependents = models.CommaSeparatedIntegerField(_('dependents'), max_length=256)
    viewable = models.ForeignKey(Group, related_name='Ticket_viewable')
    watchers = models.CommaSeparatedIntegerField(_('watchers'), max_length=256)
    reproducable = models.BooleanField(_('reproducable'), default=True)
    reproduce_steps = models.TextField(_('reproduce steps'),help_text=_("Description of the reproduction"))
    
    #TODO: this means a database query, we need to optimize this
    environment = models.ForeignKey(Environment, related_name='Ticket_environment')
    
    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)
    
    subject = models.CharField(_('name'), max_length=255, unique=True, help_text=_("Required. 255 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    description = models.TextField(_('description'),help_text=_("Description of the ticket"))
    
   
class Comment(models.Model):
    """ 
    comments for a ticket, or others
    """
    container = models.IntegerField(_('container id'))
    # a container could be a ticket itself, a comment, or others
    container_type = models.SmallIntegerField(_('container_type'))
    commenter = models.ForeignKey(User, related_name='Attachment_commenter')
    created_on = models.DateTimeField(_('created on'), default=datetime.datetime.now)
    updated_on = models.DateTimeField(_('updated on'), default=datetime.datetime.now)
    comments = models.TextField(_('comments'))

class Attachment(models.Model):  
    """
    The attached file for anything
    """
    container = models.IntegerField(_('container id'))
    # a container could be a ticket itself, a comment, or others
    container_type = models.SmallIntegerField(_('container_type'))
    filename = models.CharField(_('filename'), max_length=255)
    filesize = models.IntegerField(_('filesize'))
    content_type = models.CharField(_('content type'), max_length=30)
    digest = models.CharField(_('digest'), max_length=40)
    downloads = models.IntegerField(_('downloads'))
    owner = models.ForeignKey(User, related_name='Attachment_owner')
    uploaded_on = models.DateTimeField(_('uploaded on'), default=datetime.datetime.now)
    description = models.CharField(_('short description'), max_length=255)
    
class Journal(models.Model):
    """
    A jounal is the log of all the activities of a project
    """
    container = models.IntegerField(_('container id'))
    # a container could be a ticket itself, a comment, or others
    container_type = models.SmallIntegerField(_('container_type'))
    user = models.ForeignKey(User, related_name='Journal_owner')
    created_on = models.DateTimeField(_('uploaded on'), default=datetime.datetime.now)
    notes = models.CharField(_('notes'), max_length=255)
    
class JournalDetail(models.Model):
    """
    Journal details records all the attribute chanages in each journal
    """
    journal=models.ForeignKey(Journal, related_name="JournalDetail_journal")
    #the type of changes, e.g. attribute change or others
    property = models.CharField(_('property'), max_length=30)
    prop_key = models.CharField(_('prop_key'), max_length=30)
    old_value = models.CharField(_('old_vale'), max_length=255)
    new_value = models.CharField(_('new_value'), max_length=255)
    
    