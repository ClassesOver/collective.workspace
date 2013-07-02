from Products.CMFCore.utils import getToolByName
from collective.workspace.interfaces import IWorkspace
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import classProvides
from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def find_workspace(context):
    while hasattr(context, 'context'):
        context = context.context
    for context in reversed(context.aq_chain):
        workspace = IWorkspace(context, None)
        if workspace is not None:
            return workspace


def TeamGroupsVocabulary(context):
    workspace = find_workspace(context)
    # Membership in the Members group is implied by
    # inclusion in the roster, so we don't need to show
    # it as an explicit option.
    groups = set(workspace.available_groups.keys()) - set([u'Members'])
    return SimpleVocabulary.fromValues(sorted(groups))
directlyProvides(TeamGroupsVocabulary, IVocabularyFactory)


class UsersSource(object):
    """A source for looking up users.

    Unfortunately the one in plone.app.vocabularies is not
    quite workable with z3c.formwidget.query
    """
    implements(IQuerySource)
    classProvides(IContextSourceBinder)

    def __init__(self, context):
        self._context = context
        self._users = getToolByName(context, "acl_users")

    def __contains__(self, value):
        return self._users.getUserById(value, None) and True or False

    def search(self, query):
        for u in self._users.searchUsers(fullname=query):
            yield self.getTerm(u['userid'])

    def getTerm(self, userid):
        fullname = userid
        user = self._users.getUserById(userid, None)
        if user:
            fullname = user.getProperty('fullname', None) or userid
        return SimpleTerm(userid, userid, fullname)
    getTermByToken = getTerm

    def __iter__(self):
        for item in self._users.searchUsers():
            yield self.getTerm(item['userid'])

    def __len__(self):
        return len(self._users.searchUsers())