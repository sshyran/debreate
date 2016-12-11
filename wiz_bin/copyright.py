# -*- coding: utf-8 -*-

## \package wiz_bin.copyright

# MIT licensing
# See: docs/LICENSE.txt


import os, wx

from dbr.dialogs            import ConfirmationDialog
from dbr.functions          import GetSystemLicensesList
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from dbr.templates          import GetLicenseTemplatesList
from dbr.templates          import application_licenses_path
from dbr.templates          import local_licenses_path
from dbr.textinput          import MonospaceTextCtrl
from globals                import ident
from globals.constants      import system_licenses_path
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import GetTopWindow


# Globals
copyright_header = GT(u'Copyright © {} <copyright holder(s)> [<email>]\n\n')


## Copyright page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ident.COPYRIGHT, name=GT(u'Copyright'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        # FIXME: Ignore symbolic links
        opts_licenses = GetSystemLicensesList()
        
        # FIXME: Change variable name to 'self.builtin_licenses
        self.opts_local_licenses = GetLicenseTemplatesList()
        
        # Do not use local licenses if already located on system
        for lic in opts_licenses:
            if lic in self.opts_local_licenses:
                self.opts_local_licenses.remove(lic)
        
        # Add the remaining licenses to the selection list
        for lic in self.opts_local_licenses:
            opts_licenses.append(lic)
        
        opts_licenses.sort(key=unicode.lower)
        
        ## A list of available license templates
        self.sel_templates = wx.Choice(self, choices=opts_licenses, name=u'list»')
        self.sel_templates.default = 0
        self.sel_templates.SetSelection(self.sel_templates.default)
        
        btn_template = wx.Button(self, label=GT(u'Generate Template'), name=u'full»')
        self.btn_template_simple = wx.Button(self, label=GT(u'Generate Linked Template'), name=u'link»')
        
        if not self.sel_templates.GetCount():
            self.sel_templates.Enable(False)
            btn_template.Enable(False)
            self.btn_template_simple.Enable(False)
        
        ## Area where license text is displayed
        self.dsp_copyright = MonospaceTextCtrl(self, name=u'license')
        
        SetPageToolTips(self)
        
        if self.sel_templates.IsEnabled():
            self.OnSelectTemplate(self.sel_templates)
        
        # *** Layout *** #
        
        lyt_buttons = wx.BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_template, 1)
        lyt_buttons.Add(self.btn_template_simple, 1)
        
        lyt_label = wx.BoxSizer(wx.HORIZONTAL)
        lyt_label.Add(
            wx.StaticText(self, label=GT(u'Available Templates')),
            0,
            wx.TOP|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,
            5
        )
        lyt_label.Add(self.sel_templates, 0, wx.TOP, 5)
        lyt_label.Add(lyt_buttons, 1, wx.LEFT, 150)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_label, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        lyt_main.Add(self.dsp_copyright, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        self.sel_templates.Bind(wx.EVT_CHOICE, self.OnSelectTemplate)
        
        btn_template.Bind(wx.EVT_BUTTON, self.GenerateTemplate)
        self.btn_template_simple.Bind(wx.EVT_BUTTON, self.GenerateTemplate)
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        if not TextIsEmpty(self.dsp_copyright.GetValue()):
            warn_msg = GT(u'This will destroy all license text. Do you want to continue?')
            warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))
            
            if ConfirmationDialog(GetTopWindow(), text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
                return False
        
        return True
    
    
    ## TODO: Doxygen
    def ExportPage(self):
        return self.GetCopyright()
    
    
    ## TODO: Doxygen
    def GatherData(self):
        data = self.GetCopyright()
        return u'<<COPYRIGHT>>\n{}\n<</COPYRIGHT>>'.format(data)
    
    
    ## TODO: Doxygen
    def GenerateTemplate(self, event=None):
        if not self.DestroyLicenseText():
            return
        
        self.dsp_copyright.Clear()
        
        lic_path = u'/usr/share/common-licenses/{}'.format(self.sel_templates.GetStringSelection())
        cpright = u'Copyright: <year> <copyright holder> <email>'
        
        self.dsp_copyright.SetValue(u'{}\n\n{}'.format(cpright, lic_path))
    
    
    ## TODO: Doxygen
    def GetCopyright(self):
        return self.dsp_copyright.GetValue()
    
    
    ## TODO: Doxygen
    def GetLicensePath(self, template_name):
        # User templates have priority
        license_path = u'{}/{}'.format(local_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        license_path = u'{}/{}'.format(system_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        license_path = u'{}/{}'.format(application_licenses_path, template_name)
        if os.path.isfile(license_path):
            return license_path
        
        return None
    
    
    ## TODO: Doxygen
    def IsBuildExportable(self):
        return not TextIsEmpty(self.dsp_copyright.GetValue())
    
    
    ## TODO: Doxygen
    def OnSelectTemplate(self, event=None):
        if isinstance(event, wx.Choice):
            choice = event
        
        else:
            choice = event.GetEventObject()
        
        template = choice.GetString(choice.GetSelection())
        
        if template in self.opts_local_licenses:
            self.btn_template_simple.Disable()
        
        else:
            self.btn_template_simple.Enable()
        
        self.SetTemplateToolTip()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.dsp_copyright.Clear()
    
    
    ## TODO: Doxygen
    def SetCopyright(self, data):
        self.dsp_copyright.SetValue(data)
    
    
    ## TODO: Doxygen
    def SetTemplateToolTip(self):
        license_name = self.sel_templates.GetString(self.sel_templates.GetSelection())
        license_path = self.GetLicensePath(license_name)
        
        if license_path:
            self.sel_templates.SetToolTip(wx.ToolTip(license_path))
            return
        
        self.sel_templates.SetToolTip(None)
