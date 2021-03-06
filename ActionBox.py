# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""
  ActionBox
"""
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent
from BaseBox import BaseBox
from Products.CMFCore.utils import getToolByName

factory_type_information = (
    {'id': 'Action Box',
     'title': 'portal_type_ActionBox_title',
     'description': 'portal_type_ActionBox_description',
     'meta_type': 'Action Box',
     'icon': 'box.png',
     'product': 'CPSBoxes',
     'factory': 'addActionBox',
     'immediate_view': 'actionbox_edit_form',
     'filter_content_types': 0,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'basebox_view',
                  'permissions': (View,)},
                 {'id': 'edit',
                  'name': 'action_edit',
                  'action': 'actionbox_edit_form',
                  'permissions': (ModifyPortalContent,)},
                 ),
     # additionnal cps stuff
     'cps_is_portalbox': 1,
     },
    )


class ActionBox(BaseBox):
    """
    An Action Box simply returns an action.
    """
    meta_type = 'Action Box'
    portal_type = 'Action Box'

    security = ClassSecurityInfo()

    _properties = BaseBox._properties + (
        {'id': 'categories', 'type': 'lines', 'mode': 'w', 
            'label':'Categories of actions'},
    )

    def __init__(self, id, category='actionbox', categories=[], **kw):
        BaseBox.__init__(self, id, category=category, **kw)
        self.categories = categories

    security.declarePublic('getActions')
    def getActions(self, context, actions=None):
        """Return actions that belong to self.categories"""
        if not actions:
            atool = getToolByName(self, 'portal_actions')
            actions = atool.listFilteredActionsFor(context)

        categories = all_categories = actions.keys()
        if self.categories:
            categories = self.categories

        items = []
        for cat in categories:
            if cat in all_categories:
                if len(actions[cat]):
                    items.append(actions[cat])

        if len(items) == 1 and len(items[0]) == 1 \
           and items[0][0]['id'] == 'view':
            items = []

        return items


InitializeClass(ActionBox)


def addActionBox(dispatcher, id, REQUEST=None, **kw):
    """Add a Action Box."""
    ob = ActionBox(id, **kw)
    dispatcher._setObject(id, ob)
    ob = getattr(dispatcher, id)
    ob.manage_permission(View, ('Anonymous',), 1)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
