#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import dataCore
import re
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

[wxID_FRAME1,wxID_FRAME1BITMAPBUTTON, wxID_FRAME1BUTTON, 
 wxID_FRAME1PANEL, wxID_FRAME1SCROLLEDWINDOW, wxID_FRAME1STATICTEXT, 
 wxID_FRAME1TEXTCTRL, wxID_FRAME1STATICBOX,wxID_FRAME1RADIOBOX,] = [wx.NewId() for _init_ctrls in range(9)]

class contacts(object):
    def __init__(self,parent,dbAction):
        self.parent = parent
        self.dbAction = dbAction
        self.itemKeys = ["firstName","middleName","lastName","tel","phone","email","group"] #"pingyin"
        
    def infoContact(self,event):
        wx.CallAfter(self.showContact )
        event.Skip()
        
    def editContact(self,event):
        wx.CallAfter(self.editContactPage )
        event.Skip()

    def deleteContact(self,event):
        wx.CallAfter(self.delContactPage )
        event.Skip()

    def saveContact(self,event):
        try:
            type(self.contactInfo)
        except:
            self.contactInfo={'id':''}

        itemKeys = self.itemKeys[::-1]
        for c in self.parent.GetChildren():
            if type(c) == wx._controls.TextCtrl :
                if c.Value is u'': temp = "Null"
                else:   temp = str( c.Value)
                self.contactInfo[itemKeys.pop() ] = temp
        if self.contactInfo['id'] != '':
            self.dbAction.modify(self.contactInfo)
        else:
            self.dbAction.add(self.contactInfo)
        wx.CallAfter( self.showContact )
        event.Skip()
        
    def addContacts(self,listid,contactInfo,addDistance): 
        self.contactInfo = contactInfo
        middleName = ( self.contactInfo['middleName'] == 'Null' ) and " " or  self.contactInfo['middleName']
        self.panel = wx.Panel(id=wxID_FRAME1PANEL, name=str('panel_%d' % listid),
                              parent=self.parent,style=wx.TAB_TRAVERSAL,
                              size=wx.Size(333, 40),pos=wx.Point(4, listid * 40 + addDistance + 20))
        self.bitmapButton = wx.BitmapButton(bitmap=wx.NullBitmap,
                                            id=wxID_FRAME1BITMAPBUTTON, name=str('avator_%d' % listid),
                                            parent=self.panel,style=wx.BU_AUTODRAW,
                                            size=wx.Size(32, 32),pos=wx.Point(20, 4))
        self.staticText = wx.StaticText(id=wxID_FRAME1STATICTEXT,
                                        label=str("%s %s %s" % ( contactInfo['firstName'],middleName,contactInfo['lastName']) ),
                                        name=str('contactName_%d' % listid),
                                        parent=self.panel,style=0,
                                        size=wx.Size(180,20),pos=wx.Point(68, 10))
        self.bitmapButton.Bind(wx.EVT_LEFT_DOWN,self.infoContact)
        self.staticText.Bind(wx.EVT_LEFT_DOWN,self.infoContact)
        
    def editContactPage(self):
        self.parent.DestroyChildren()
        self.newContact(self.contactInfo)
        return True
        
    def delContactPage(self):
        self.parent.DestroyChildren()
        if self.dbAction.delete(self.contactInfo['id']):
            self.staticText = wx.StaticText(id=wxID_FRAME1STATICTEXT,label="DeleteSuccess",name="deleteSuccess", 
                                            parent=self.parent,style=0,
                                            pos=wx.Point(150, 200),size=wx.Size(100,20))
        return True

    def newContact(self,contactData={}):
        if contactData == {}:
            contactData={ item:'' for item in self.itemKeys }
            contactData["id"]=''
        else:
            for key in contactData.keys():
                if contactData[key] == "None" : contactData[key] = ""
        self.staticText = {}
        itemNum=0
        for key in self.itemKeys:
            self.staticText[key] = [ wx.StaticText(id=wxID_FRAME1STATICTEXT,
                                         label=key.upper(), name=key, parent=self.parent,style=0,
                                         pos=wx.Point(20, itemNum * 25 + 30), size=wx.Size(120, 25)),
                                    wx.TextCtrl(id=wxID_FRAME1TEXTCTRL,
                                         value=contactData[key], name="Text" + contactData[key], parent=self.parent,style=0,
                                         pos=wx.Point(150, itemNum * 25 + 30), size=wx.Size(200, 25))]
            itemNum = itemNum + 1
        self.button_save = wx.Button(id=wxID_FRAME1BUTTON,
                                     label='Save', name='buttonSave',
                                     parent=self.parent,style=0,
                                     pos=wx.Point(20,itemNum * 25 + 50),size=wx.Size(80, 30))
        self.button_save.Bind(wx.EVT_LEFT_DOWN,self.saveContact)

    def showContact(self):
        if type(self.parent) is wx._windows.Panel:
            self.parent =  self.parent.Parent
        self.parent.DestroyChildren()
        self.parent.SetScrollbars(0,1,0,400)
        self.staticText = {}
        itemKeys = list( self.itemKeys )
        itemKeys.insert(0,"id")
        itemNum=0
        for key in itemKeys:
            self.staticText[key] = [wx.StaticText(id=wxID_FRAME1STATICTEXT,
                                         label=key.upper(), name=key, parent=self.parent,
                                         pos=wx.Point(20, itemNum * 20 + 30), size=wx.Size(120, 20), style=0),
                                    wx.StaticText(id=wxID_FRAME1STATICTEXT,
                                         label=self.contactInfo[key], name=self.contactInfo[key], parent=self.parent,
                                         pos=wx.Point(150, itemNum * 20 + 30), size=wx.Size(200, 20), style=0)]
            #self.staticText[key][0].Bind(wx.EVT_LEFT_DOWN,self.editContact)
            self.staticText[key][1].Bind(wx.EVT_LEFT_DOWN,self.editContact)
            itemNum = itemNum + 1
        self.button_edit = wx.Button(id=wxID_FRAME1BUTTON,
                                     label='Edit', name='buttonEdit',
                                     parent=self.parent, pos=wx.Point(20,260), size=wx.Size(100, 50),style=0)
        self.button_delete = wx.Button(id=wxID_FRAME1BUTTON,
                                     label='Delete', name='buttonDelete',
                                     parent=self.parent, pos=wx.Point(200,260), size=wx.Size(100, 50),style=0)
        self.button_edit.Bind(wx.EVT_LEFT_DOWN,self.editContact)
        self.button_delete.Bind(wx.EVT_LEFT_DOWN,self.deleteContact)
        return True
        
class Frame(wx.Frame):
    def __init__(self, parent):
        self.fileHandle = dataCore.xml_file(".db.xml")
        self.dbAction = dataCore.phone_DB(self.fileHandle)
        self._init_ctrls(parent)
        self.showBook()
        
    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER , title='Phone Book',
                          pos=wx.Point(611, 217), size=wx.Size(404, 620))
        self.SetClientSize(wx.Size(386, 568))
        icoFile = "pb.ico"
        if os.path.isfile(icoFile) == True: self.SetIcon(wx.Icon(icoFile, wx.BITMAP_TYPE_ICO))  
        """ End: Basic Layout"""
        self.panel1 = wx.Panel(id=wxID_FRAME1PANEL, name='panel1', parent=self,style=wx.TAB_TRAVERSAL,
                               pos=wx.Point(0, 0), size=wx.Size(392, 104))
        self.scrolledWindow = wx.ScrolledWindow(id=wxID_FRAME1SCROLLEDWINDOW,
              name='scrolledWindow', parent=self, style=wx.HSCROLL | wx.VSCROLL,
              pos=wx.Point(0, 106),size=wx.Size(392, 420))
        self.scrolledWindow.SetMinSize(wx.Size(-1, 408))
        self.scrolledWindow.SetFocus()
        self.panel2 = wx.Panel(id=wxID_FRAME1PANEL, name='panel2', parent=self,style=wx.TAB_TRAVERSAL,
                               pos=wx.Point(0, 528), size=wx.Size(392, 40))

        self.button_Book = wx.Button(id=wxID_FRAME1BUTTON,
                                     label='My Contacts', name='buttonBook',
                                     parent=self.panel1,style=0,
                                     pos=wx.Point(0, 0), size=wx.Size(192, 48))
        self.button_Book.SetToolTipString('Show Contacts')
        self.button_Book.SetHelpText('')
        self.button_Book.SetThemeEnabled(False)
        self.button_Book.Bind(wx.EVT_BUTTON, self.showBookButton)
        self.button_Group = wx.Button(id=wxID_FRAME1BUTTON,
                                      label='My Group', name='buttonGroup',
                                      parent=self.panel1, style=0,
                                      pos=wx.Point(192, 0), size=wx.Size(192, 48))
        self.button_Group.SetToolTipString('Show Groups')
        self.button_Group.Bind (wx.EVT_LEFT_UP, self.showGroupButton)
        
        self.text_Search = wx.TextCtrl(id=wxID_FRAME1TEXTCTRL, name='textSearch',
                                       value='search contact',
                                       parent=self.panel1, style=0,
                                       pos=wx.Point(16, 64), size=wx.Size(288, 32))
        self.text_Search.Bind(wx.EVT_LEFT_DOWN, self.OnTextSearchLeftDown)
        self.text_Search.Bind(wx.EVT_CHAR_HOOK, self.searchEnter)
        self.button_Search = wx.Button(id=wxID_FRAME1BUTTON,
                                       label='search', name='buttonSearch',
                                       parent=self.panel1,style=0,
                                       pos=wx.Point(320, 64), size=wx.Size(56, 32))
        self.button_Search.Bind(wx.EVT_LEFT_UP, self.searchButton)
        self.button_addContact = wx.Button(id=wxID_FRAME1BUTTON,
                                           label='+ New Contact', name='buttonAddContact',
                                           parent=self.panel2,style=0,
                                           pos=wx.Point(120, 0), size=wx.Size(150, 40))
        self.button_addContact.Bind(wx.EVT_BUTTON, self.addContactButton)
        """ Event """
    def showBookButton(self,event):
        self.clearMain()
        self.showBook()
        event.Skip()
    
    def showGroupButton(self,event):
        self.showGroup()
        event.Skip()
    
    def searchButton(self, event):
        self.clearMain()
        keyword = self.text_Search.Value
        if keyword != '': 
            self.clearMain()
            self.dbAction.refresh()
            contactData = self.dbAction.sort(self.itemKeys[0])
            result=[]
            for contact in contactData:
                for value in contact.values():
                    searchBool = re.search(r'' + keyword, value )
                    if searchBool != None: break
                if searchBool != None: result.append(contact)
            self.initContacter(self.scrolledWindow,result,0)
        event.Skip()
    
    def searchEnter(self,event):
        code = event.GetKeyCode()
        if code == wx.WXK_RETURN: self.searchButton(event)
        event.Skip()
        
    def OnTextSearchLeftDown(self,event):
        self.text_Search.Value=''
        event.Skip()
    
    def addContactButton(self, event):
        self.clearMain()
        self.scrolledWindow.SetScrollbars(0,0,0,0)
        contacter = contacts(self.scrolledWindow,self.dbAction)
        contacter.newContact()
        event.Skip()
    
    def sortHandle(self,event):
        for c in self.bookPanel.GetChildren():
            if type(c) == wx._windows.Panel: c.Destroy()
        keyword = self.itemKeys[ event.Selection ]
        self.loadContact(keyword)
        event.Skip()

    def initContacter(self,parent,contacterData,contDistance=0):
        contacter = []
        contactNum = 0
        for res in contacterData:
            contacter= contacts(parent,self.dbAction)
            contacter.addContacts(contactNum,res,contDistance)
            contactNum = contactNum + 1
        return True
    
    def showBook(self):
        self.itemKeys = ["firstName","lastName","phone"]
        sortlength = 10000000
        self.bookPanel = wx.Panel(id=wxID_FRAME1PANEL, name='Bookpanel', parent=self.scrolledWindow,style=wx.TAB_TRAVERSAL,
                pos=wx.Point(0, 0) ,size=wx.Size(360, sortlength * 40 )) 
        self.radioBox = wx.RadioBox(choices=[ s.title() for s in self.itemKeys ], id=wxID_FRAME1RADIOBOX,label='Fast Sort', majorDimension=3, name='radioBox',
            parent=self.bookPanel, size=wx.Size(340,70),pos=wx.Point(20, 0), style=wx.RA_SPECIFY_COLS)
        self.radioBox.Bind(wx.EVT_RADIOBOX, self.sortHandle)
        sortlength = self.loadContact(self.itemKeys[0])
    
    def loadContact(self,sortWord):
        self.dbAction.refresh()
        sortData = self.dbAction.sort(sortWord)
        sortlength = len(sortData)
        self.scrolledWindow.SetScrollbars(0, 1, 0, (sortlength + 2  ) * 40 )
        self.scrolledWindow.SetScrollRate(-1,20)
        self.initContacter(self.bookPanel,sortData,55)
        return sortlength

    def showGroup(self):
        self.clearMain()
        self.dbAction.refresh()
        groupData = self.dbAction.group()
        contactBox = 0
        groupBox = 0
        for groupName in groupData.keys():
            contactlength = len(groupData[groupName])
            self.groupBox = wx.Panel(id=wxID_FRAME1PANEL, name='panel-' + groupName, parent=self.scrolledWindow,style=wx.TAB_TRAVERSAL,
                pos=wx.Point(6, contactBox * 40 + groupBox * 30 + 5),
                size=wx.Size(360, (contactlength  + 1) * 40 + 30) )
            self.groupText = wx.StaticText(id=wxID_FRAME1STATICTEXT,label=str("Group: %s" % ( groupName) ),
                name=str('groupName_%s' % groupName),
                parent=self.groupBox,style=0,
                size=wx.Size(100,20),pos=wx.Point(0, 10) )
            groupBox = groupBox + 1
            contactBox = contactBox + contactlength
            self.initContacter(self.groupBox,groupData[groupName],12)
        if contactBox * 40 + groupBox * 30  > 410:
            self.scrolledWindow.SetScrollbars(0, 1, 0, contactBox * 40 + groupBox * 30 + 10 )
            self.scrolledWindow.SetScrollRate(-1,20)
        return True
            
    def clearMain(self):
        self.scrolledWindow.DestroyChildren()
        self.scrolledWindow.SetFocus()
        return True

class BoaApp(wx.App):
    def OnInit(self):
        self.main = Frame(None)
        self.main.Center()
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
