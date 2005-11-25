# -*- coding: iso-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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
# $Id:$
"""
  CPSBoxes installation
"""
from Products.CPSInstaller.CPSInstaller import CPSInstaller

# CPSBoxes permissions
ManageBoxes = 'Manage Boxes'
AddBoxContainer = 'Add Box Container'
ManageBoxOverrides = 'Manage Box Overrides'

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'

class CPSBoxesInstaller(CPSInstaller):

    def setupAccessControl(self):
        sections_perms = {
            AddBoxContainer: ['Manager', 'SectionManager'],
            ManageBoxOverrides: ['Manager','SectionManager'],
            ManageBoxes: ['Manager', 'SectionManager'],
            }
        self.setupPortalPermissions(sections_perms, self.portal[SECTIONS_ID])

        workspaces_perms = {
            AddBoxContainer: ['Manager', 'WorkspaceManager',
                                  'SectionManager'],
            ManageBoxOverrides: ['Manager','WorkspaceManager'],
            ManageBoxes: ['Manager', 'WorkspaceManager'],
            }
        self.setupPortalPermissions(workspaces_perms,
                                    self.portal[WORKSPACES_ID])

    def setupSkins(self):
        skins = {
            'cps_boxes'  : 'Products/CPSBoxes/skins/cps_boxes',
        }
        self.verifySkins(skins)

    def setupTypes(self):
        t = 'typeinfo_name'
        amt = 'add_meta_type'
        FTI = 'Factory-based Type Information'
        boxes_dict =  {
            'Base Box': {
                t: 'CPSBoxes: Base Box (Base Box)',
                amt: FTI,},
            'Text Box': {
               t: 'CPSBoxes: Text Box (Text Box)',
               amt: FTI,},
            'Tree Box': {
                t: 'CPSBoxes: Tree Box (Tree Box)',
                amt: FTI,},
            'Content Box': {
                t: 'CPSBoxes: Content Box (Content Box)',
                amt: FTI,},
            'Action Box': {
                t: 'CPSBoxes: Action Box (Action Box)',
                amt: FTI,},
            'Image Box': {
                t: 'CPSBoxes: Image Box (Image Box)',
                amt: FTI,},
            'Flash Box': {
                t: 'CPSBoxes: Flash Box (Flash Box)',
                amt: FTI,},
            'Event Calendar Box': {
                t: 'CPSBoxes: Event Calendar Box (Event Calendar Box)',
                amt: FTI,},
            'InternalLinks Box': {
                t: 'CPSBoxes: InternalLinks Box (InternalLinks Box)',
                amt: FTI,},
            'Doc Render Box':{
                t: 'CPSBoxes: Doc Render Box (Doc Render Box)',
                amt: FTI,},
        }

        self.verifyContentTypes(boxes_dict)

    def setupBoxes(self):
        self.verifyTool('portal_boxes', 'CPSBoxes', 'CPS Boxes Tool')
        self.log("Adding cps default boxes")
        boxes = {
            'action_header': {'type': 'Action Box',
                    'title': 'Header actions',
                    'btype': 'header',
                    'slot': 'top',
                    'categories': 'global_header',
                    'order': 5,
                    },
            'search': {'type': 'Base Box',
                    'title': 'Search form',
                    'btype': 'search',
                    'slot': 'top',
                    'order': 10,
                    },
            'logo': {'type': 'Base Box',
                    'title': 'Portal logo',
                    'btype': 'logo',
                    'slot': 'top',
                    'order': 20,
                    },
            'menu': {'type': 'Tree Box',
                    'title': 'Tab menu',
                    'btype': 'menu',
                    'slot': 'top',
                    'order': 30,
                    },
            'breadcrumbs': {'type': 'Base Box',
                            'title': 'Navigation path',
                            'btype': 'breadcrumbs',
                            'slot': 'top',
                            'order': 40,
                            },

            'contact': {'type': 'Text Box',
                       'title': 'Contact',
                       'btype': 'default',
                       'box_skin': 'here/box_lib/macros/wbox2',
                       'slot': 'bottom',
                       'order': 10,
                       'text': '<address class="contact">Nuxeo - 18-20, rue Soleillet, 75020 Paris France<br />Email : <a href="mailto:contact@nuxeo.com">contact@nuxeo.com</a> - Tel: +33 (0)1 40 33 79 87 - Fax: +33 (0)1 40 33 71 41</address>',
                    },

            'conformance_statement': {'type': 'Base Box',
                    'title': 'Conformance statements',
                    'btype': 'conformance_statement',
                    'slot': 'bottom',
                    'order': 20,
                    },

            'l10n_select': {'type': 'Base Box',
                            'title': 'Locale selector',
                            'btype': 'l10n_select',
                            'slot': 'left',
                            'order': 10,
                            },

            'action_user': {'type': 'Action Box',
                            'title': 'User actions',
                            'btype': 'user',
                            'slot': 'left',
                            'order': 20,
                            'categories': 'user',
                            'box_skin': 'here/box_lib/macros/sbox',
                            },
            'action_portal': {'type': 'Action Box',
                            'title': 'Portal actions',
                            'slot': 'left',
                            'order': 30,
                            'categories': 'global',
                            'box_skin': 'here/box_lib/macros/sbox',
                            },
            'navigation': {'type': 'Tree Box',
                        'title': 'Navigation tree menu',
                        'depth': 1,
                        'contextual': 1,
                        'slot': 'left',
                        'order': 40,
                        'box_skin': 'here/box_lib/macros/mmbox',
                        },

            'action_object': {'type': 'Action Box',
                            'title': 'Object actions',
                            'slot': 'right',
                            'order': 10,
                            'categories': ('object', 'workflow'),
                            'box_skin': 'here/box_lib/macros/sbox',
                            },

            'action_folder': {'type': 'Action Box',
                            'title': 'Folder actions',
                            'slot': 'right',
                            'order': 20,
                            'categories': 'folder',
                            },

            'welcome': {'type': 'Text Box',
                        'title': 'Portal welcome message',
                        'slot': 'center',
                        'order': 10,
                        'btype': 'default',
                         # No frame, no title box, no class="box" cf. box_lib.pt
                        'box_skin': 'here/box_lib/macros/wbox3',
                        'display_in_subfolder': 0,
                        'display_only_in_subfolder': 0,
                        'text': 'welcome_body',
                        'i18n': 1,
                        },

            'nav_header': {'type': 'Base Box',
                            'title': 'Folder header',
                            'slot': 'folder_view',
                            'order': 0,
                            'btype': 'folder_header',
                            },

            'nav_folder': {'type': 'Tree Box',
                            'title': 'Sub folders',
                            'slot': 'folder_view',
                            'order': 10,
                            'box_skin': 'here/box_lib/macros/wbox2',
                            'btype': 'center',
                            'contextual': 1,
                            'depth': 2,
                            'children_only': 1,
                            },

            'nav_content': {'type': 'Content Box',
                            'title': 'Contents',
                            'slot': 'folder_view',
                            'btype': 'default',
                            'box_skin': 'here/box_lib/macros/sbox2',
                            'order': 20,
                            },
        }
        self.verifyBoxes(boxes)
        self.verifyAction(
            tool='portal_actions',
            id='boxes',
            name='action_boxes_root',
            action='string:${portal_url}/box_manage_form',
            condition='python:folder is object',
            permission=(ManageBoxes,),
            category='global',
            visible=1)

def install(self):
    installer = CPSBoxesInstaller(self, 'CPSBoxes')
    installer.log("Starting CPSBoxes install")

    # skins
    installer.setupSkins()

    # types
    installer.setupTypes()

    # set up boxes
    installer.setupBoxes()

    # set up permissions on sections / workspaces
    # XXX we don't do it yet since 'setupPortalPermissions' overrides
    # existing permissions

    # installer.setupAccessControl()

    # Translations
    installer.setupTranslations()

    installer.finalize()
    installer.log("End of specific CPSBoxes install")
    return installer.logResult()

