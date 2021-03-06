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
  BoxesTool
"""
from zLOG import LOG, DEBUG, INFO

from Globals import InitializeClass, DTMLFile, MessageDialog, PersistentMapping
from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from Acquisition import aq_base, aq_parent, aq_inner

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName, _checkPermission

class BoxesTool(UniqueObject, PortalFolder):
    """
    Boxes Tool.
    """
    id = 'portal_boxes'
    meta_type = 'CPS Boxes Tool'
    security = ClassSecurityInfo()

    def __init__(self):
        pass

    manage_options = list(PortalFolder.manage_options)
    # Replace the pointless 'View' with 'Overview'
    manage_options[1] = {'label': "Overview", 'action': 'manage_overview',}


    #
    # ZMI
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('zmi/explainBoxesTool', globals())

    #
    # Public API
    #
    security.declarePublic('getBoxes')
    def getBoxes(self, context, slot=None, include_personal=1,
                 include_only_in_subfolder=0):
        """Return a sorted list of boxes
        box are loaded from root to current path
        and overriden by personal boxes folder
        return a list of dictionaries with keys:
            'url', 'display_url', 'settings', 'macro', 'box'
        """

        # Find bottom-most folder:
        obj = context
        bmf = None
        while 1:
            if obj.isPrincipiaFolderish:
                bmf = obj
                break
            parent = aq_parent(aq_inner(obj))
            if not obj or parent == obj:
                break
            obj = parent
        if not bmf:
            bmf = context

        # get boxes from root to current path
        # XXX This is badly reinventing traversal.
        # XXX Use aq_parent(aq_inner(ob)) the other way round instead.
        portal_url = getToolByName(self, 'portal_url')
        rpath = portal_url.getRelativeContentPath(bmf)
        obj = portal_url.getPortalObject()
        allboxes = []
        settings = {}
        home_boxes_loaded = 0
        home = getToolByName(self, 'portal_membership').getHomeFolder()
        for elem in ('',) + rpath:
            if elem:
                obj = getattr(obj, elem, None)
                if obj is None:
                    break
            if obj == home:
                home_boxes_loaded = 1
            f_boxes, f_settings = self._getFolderBoxesAndSettings(obj)
            allboxes.extend(f_boxes)
            self._updateSettings(settings, f_settings)

        if not home_boxes_loaded and include_personal and home:
            f_boxes, f_settings = self._getFolderBoxesAndSettings(home)
            # we don't to make users boxes global boxes
            # we just take care to override the settings
            self._updateSettings(settings, f_settings)

        boxes = []
        for box in allboxes:
            ## Skip it if there is no view permission
            ##if not _checkPermission('View', box):
            ##    continue
            # Do ACL or TAL expression allow this box here
            if box.getGuard() and not box.getGuard().check(getSecurityManager(), box, context):
                continue
            # Only add boxes if they are to be displayed
            # in the subfolders, or if
            # this is the last part of the path
            boxpath = portal_url.getRelativeContentPath(box)
            if len(boxpath) < 3:
                boxdisplayurl = ''
            else:
                boxdisplayurl = '/'.join(boxpath[:-2])
            rurl = '/'.join(rpath)


            if (not box.display_in_subfolder and
                not box.display_only_in_subfolder and
                rurl != boxdisplayurl):
                continue

            if (not include_only_in_subfolder and
                box.display_only_in_subfolder and rurl == boxdisplayurl):
                continue

            newbox = {'url': portal_url.getRelativeUrl(box),
                      'display_url': boxdisplayurl,
                      'settings': box.getSettings(),
                      'macro': box.getMacro(),
                      'box': box}

            # Override any box settings with the local settings
            # If the box isn't locked and there are overrides
            if not newbox['box'].locked and settings.get(newbox['url']):
                newbox['settings'].update(settings[newbox['url']])
                newbox['macro'] = newbox['box'].getMacro(
                    provider=newbox['settings']['provider'],
                    btype=newbox['settings']['btype'])

            boxes.append(newbox)

        # We now have a list of all boxes that can be displayed in this context.
        # We'll now filter to only get the open boxes in the asked for slot.
        # This can not be done previously, since 'slot' and 'closed' settings
        # can be overriden by local setting
        boxes = [x for x in boxes
                   if slot is None or x['settings']['slot'] == slot]

        # sorting
        def cmpbox(a, b):
            return a['settings']['order'] - b['settings']['order']
        boxes.sort(cmpbox)

        return boxes


    security.declarePublic('filterBoxes')
    def filterBoxes(self, boxes, slot='', closed_only=0, keep_closed=0):
        """Filter a list of boxes for required slot removing closed boxes
        or filter for all closed box
        or filter for required slot keeping closed box"""
        if closed_only:
            # don't take care of the slot criteria
            return [x for x in boxes if x['settings']['closed']]

        if keep_closed:
            return [x for x in boxes if (x['settings']['slot'] == slot)]

        return [x for x in boxes if (x['settings']['slot'] == slot and
                                     not x['settings']['closed'])]


    def setBoxOverride(self, boxurl, settings, context):
        """Allow overriding the box default settings

        boxurl is the relative url of the box (gotten from
        portal_url.getRelativeUrl(box) )

        settings is a dictionary of the settings and the values

        context is the object where defaults should be stored.
        """
        sm = getSecurityManager()
        if not sm.checkPermission('Manage Box Overrides', context):
            raise Unauthorized()

        if not hasattr(aq_base(context), '_box_overrides'):
            context._box_overrides = PersistentMapping()

        # TODO: check which settings you are allowed to change
        context._box_overrides[boxurl] = settings

    security.declarePublic('getBoxOverride')
    def getBoxOverride(self, boxurl, context):
        """Get the overridden settings for a box"""
        if not hasattr(aq_base(context), '_box_overrides'):
            return {}
        return context._box_overrides.get(boxurl, {})

    security.declarePublic('getAllBoxOverrides')
    def getAllBoxOverrides(self, context):
        """Get all the local overrides"""
        return getattr(aq_base(context), '_box_overrides', {})

    #
    # managing Personal overrides
    #
    security.declarePublic('updatePersonalBoxOverride')
    def updatePersonalBoxOverride(self, boxurl, new_settings):
        """Save personal override for a single box"""
        # find the personal boxes container pbc, create if empty
        home = getToolByName(self, 'portal_membership').getHomeFolder()
        if home is None:
            return
        idbc = self.getBoxContainerId(home)

        home.manage_addProduct['CPSBoxes'].addBoxContainer(quiet=1)
        pbc = getattr(home, idbc, None)

        # get current override and update
        settings = self.getBoxOverride(boxurl, pbc)
        settings.update(new_settings)

        for field in settings.keys():
            if field in ('minimized', 'order', 'closed'):
                settings[field] = int(settings[field])
            elif not settings[field]:
                del settings[field]

        self.setBoxOverride(boxurl, settings, pbc)
        LOG('portal_boxes', DEBUG,
            'updatePersonalBoxOverride', 'in %s setting: %s\n' % (
            pbc.absolute_url(), str(settings)))

    security.declarePublic('delPersonalBoxOverrides')
    def delPersonalBoxOverrides(self):
        """Delete all personal boxes overrides
        XXX TODO rename ? indead delete the personal boxcontainer"""
        # find the personal boxes container pbc
        home = getToolByName(self, 'portal_membership').getHomeFolder()
        if home is None:
            return
        idbc = self.getBoxContainerId(home)

        if hasattr(aq_base(home), idbc):
            home.manage_delObjects([idbc])
            LOG('portal_boxes', INFO, 'delPersonalBoxOverrides',
                'Delete all personal boxes settings: %s/%s\n' % (
                home.absolute_url(), idbc))

    #
    # misc
    #
    security.declarePublic('getBoxContainerId')
    def getBoxContainerId(self, folder):
        """Return the id of the box container for the folder
        because root folder should have a different id to pass
        _checkId for non manager"""
        portal_url = getToolByName(self, 'portal_url')
        url = portal_url.getRelativeUrl(folder)

        if url:
            return BoxContainer.id

        return BoxContainer.id_root


    #
    # Private
    #
    security.declarePrivate('_getFolderBoxesAndSettings')
    def _getFolderBoxesAndSettings(self, folder):
        """Load all boxes in a .cps_boxes folder
        load folder settings
        """
        idbc = self.getBoxContainerId(folder)
        boxes = []
        settings = {}
        folder_boxes = None
        if hasattr(aq_base(folder), idbc):
            folder_boxes = getattr(folder, idbc)
            for box in folder_boxes.objectValues():
                if not hasattr(aq_base(box), 'isPortalBox'):
                    continue
                boxes.append(box)

            settings = self.getAllBoxOverrides(folder_boxes)

        return boxes, settings


    security.declarePrivate('_updateSettings')
    def _updateSettings(self, set1, set2):
        """Update settings 1 with settings 2 """
        if not set2:
            return
        for k in set2.keys():
            if set1.get(k):
                set1[k].update(set2[k])
            else:
                set1[k] = set2[k]



InitializeClass(BoxesTool)

class BoxContainer(PortalFolder):
    id = '.cps_boxes'
    id_root = '.cps_boxes_root'    # different name to make _checkId
                                   # working for non manager
    meta_type = 'CPS Boxes Container'
    portal_type = 'CPS Boxes Container'
    security = ClassSecurityInfo()

    manage_options = (
        (PortalFolder.manage_options[0],
        {'label': "Overrides", 'action': 'manage_boxOverridesForm',},) +
        PortalFolder.manage_options[2:]
        )

    #
    # ZMI
    #
    security.declarePublic('objectIds')
    security.declarePublic('objectValues')
    security.declarePublic('objectItems')

    security.declareProtected('Manage Box Overrides', 'manage_boxOverridesForm')
    manage_boxOverridesForm = DTMLFile('zmi/manage_boxOverridesForm', globals())

    security.declareProtected('Manage Box Overrides', 'manage_boxOverrides')
    def manage_boxOverrides(self, submit, new_path, overrides=[], selected=[],
                            REQUEST=None):
        """Sets overrides."""
        LOG('Box Container', DEBUG, 'manage_boxOverrides',
            'submit: %s\nselected: %s\noverrides: %s\nnew_path: %s\n' % \
            (submit, selected, str(overrides), new_path))
        if not hasattr(aq_base(self), '_box_overrides'):
            self._box_overrides = PersistentMapping()

        if submit == " Delete ":
            for each in selected:
                del self._box_overrides[each]
            message = 'Override(s) deleted.'
        elif submit == " Add new override ":
            target = self.unrestrictedTraverse(new_path, None)
            if target is None:
                message = 'Entered box could not be found'
            else:
                portal_url = getToolByName(self, 'portal_url')
                boxpath = portal_url.getRelativeContentURL(target)
                self._box_overrides[boxpath] = {}
                message = 'Override added.'
        elif submit == " Save Changes ":
            # Kill the old settings
            self._box_overrides = PersistentMapping()
            for override in overrides:
                settings = {}
                # Filter out empty settings:
                box_path = None
                for key, item in override.items():
                    if item:
                        if key in ('order', 'minimized', 'closed'):
                            item = int(item)
                        if key == 'box_path':
                            box_path = item
                        else:
                            settings[key] = item
                LOG('Box Container', DEBUG, 'manage_boxOverrides',
                    str(settings) + '\n')
                self._box_overrides[box_path] = settings
            message = 'Settings changed.'
        else:
            message = 'Nothing to do.'
        if REQUEST is not None:
            return self.manage_boxOverridesForm(REQUEST,
                management_view='Overrides',
                manage_tabs_message=message)


    #
    # Management interface support functions
    #
    # These are mainly here to support the management GUI.
    # In typical usage the overrides would be set and retrieved through
    # the portal_boxes tool.
    security.declarePublic('getOverrides')
    def getOverrides(self):
        """Gets all the local overrides."""
        result = []
        overrides = getattr(aq_base(self), '_box_overrides', {})
        for key, item in overrides.items():
            override = {'box_path': key, 'slot': '', 'order': '', 'closed': '',
                        'minimized': '', 'provider': '', 'btype': '',
                        'box_skin': ''}
            override.update(item)
            result.append(override)
        #LOG('BoxContainer', DEBUG, 'getOverrides', str(result) + '\n' )
        return result


def addBoxContainer(self, id=None, REQUEST=None, quiet=0):
    """Add a Box Container."""
    self = self.this()
    btool = getToolByName(self, 'portal_boxes')
    id = btool.getBoxContainerId(self)

    if hasattr(aq_base(self), id):
        if quiet:
            return
        else:
            return MessageDialog(
                title='Item Exists',
                message='This object already contains an %s' % id,
                action='%s/manage_main' % REQUEST['URL1'])

    ob = BoxContainer(id)
    self._setObject(id, ob)

    LOG('addBoxContainer', DEBUG,
        'adding box container %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


InitializeClass(BoxContainer)
