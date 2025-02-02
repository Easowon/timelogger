# Copyright (c) 2024 Eason Chen. Licensed under the MIT Licence.

import wx
import wx.xrc
import wx.adv
import os
import sqlite3
import time
import webbrowser
from functools import partial
from timelogger_model import *

'''
todo:
better name
'''


import gettext
_ = gettext.gettext

class StartupScreen():
    def __init__(self, parent):
        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName(_("Time Logger"))
        aboutInfo.SetVersion(_("1.0.0"))
        aboutInfo.SetDescription(_("Manages and logs time spent"))
        aboutInfo.AddDeveloper(_("Eason Chen"))
        aboutInfo.SetWebSite("https://github.com/Easowon/timelogger")
        wx.adv.AboutBox(aboutInfo, parent)

class TimeLogger ( wx.Frame ):

    def __init__( self, parent ):
        self.parent  = parent
        try:
            db_file = open("db_directory.txt", "x")
            db_file = open("db_directory.txt", "w")
            db_file.write("TimeLogger.db")
        except:
            pass
        finally:
            db_file = open("db_directory.txt")
        
        db_directory = db_file.readline().strip()
        self.logs = LogBook(db_directory)
        #self.logs.purge_db()
        
        self.m_menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        newItem = wx.MenuItem(fileMenu,wx.ID_NEW, text = "&New",kind = wx.ITEM_NORMAL)
        fileMenu.Append(newItem)
        openItem = wx.MenuItem(fileMenu,wx.ID_OPEN, text = "&Open",kind = wx.ITEM_NORMAL)
        fileMenu.Append(openItem)
        exportItem = wx.MenuItem(fileMenu,wx.ID_SAVEAS, text = "E&xport Full",kind = wx.ITEM_NORMAL)
        fileMenu.Append(exportItem)
        quitItem = wx.MenuItem(fileMenu,wx.ID_EXIT, text = "&Quit",kind = wx.ITEM_NORMAL)
        fileMenu.Append(quitItem)
        helpMenu = wx.Menu()
        aboutMenu = wx.Menu()
        StartupPageItem = wx.MenuItem(aboutMenu, wx.ID_ABOUT, text = "&Startup Page", kind = wx.ITEM_NORMAL)
        LinkedInItem = wx.MenuItem(aboutMenu, wx.ID_INFO, text = "&LinkedIn", kind = wx.ITEM_NORMAL)
        aboutMenu.Append(StartupPageItem)
        aboutMenu.Append(LinkedInItem)
        linkedInItem = wx.MenuItem(aboutMenu, wx.ID_ABOUT, text = "&LinkedIn", kind = wx.ITEM_NORMAL)
        aboutMenu.Append(linkedInItem)
        helpMenu.AppendSubMenu(aboutMenu, "&About")
        
        self.m_menuBar.Append(fileMenu, "&File")
        self.m_menuBar.Append(helpMenu, "&Help")
    
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Time Logger"), pos = wx.DefaultPosition, size = wx.Size( 700,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
            
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        OuterSizer = wx.BoxSizer( wx.VERTICAL )

        # -- CATEGORY SIZER
        
        CategorySizer = wx.BoxSizer( wx.VERTICAL )
        
        # ---- COMBOBOX SIZER
        
        ComboboxSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.m_comboCategoryChoices = self.logs.get_cat_names()
        self.m_comboCategory = wx.ComboBox( self, wx.ID_ANY, _(u""), wx.DefaultPosition, wx.Size(200, 30), self.m_comboCategoryChoices, 0)
        self.m_comboCategory.Bind(wx.EVT_COMBOBOX, self.on_combobox_select)
        
        ComboboxSizer.Add( self.m_comboCategory, 0, wx.ALL, 5 )

        self.m_buttonEditCategory = wx.Button( self, wx.ID_ANY, _(u"Edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        ComboboxSizer.Add( self.m_buttonEditCategory, 0, wx.ALL, 5 )
        self.m_buttonEditCategory.Bind(wx.EVT_BUTTON, self.on_category_edit)

        self.m_buttonDelCategory = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
        ComboboxSizer.Add( self.m_buttonDelCategory, 0, wx.ALL, 5 )
        self.m_buttonDelCategory.Bind(wx.EVT_BUTTON, self.on_category_del)

        CategorySizer.Add( ComboboxSizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        # ----

        # ---- CATEGORY CONTROLS SIZER
        
        CategoryControlsSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_textCategory = wx.TextCtrl(self, wx.ID_ANY, _(u""), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCategory.SetHint("Category Name...")
        CategoryControlsSizer.Add( self.m_textCategory, 0, wx.ALL, 5 )

        self.m_buttonCreateCategory = wx.Button( self, wx.ID_ANY, _(u"Create"), wx.DefaultPosition, wx.DefaultSize, 0 )
        CategoryControlsSizer.Add( self.m_buttonCreateCategory, 0, wx.ALL, 5 )
        self.m_buttonCreateCategory.Bind(wx.EVT_BUTTON, self.on_category_create)
        
        self.m_buttonUpdateCategory = wx.Button( self, wx.ID_ANY, _(u"Update"), wx.DefaultPosition, wx.DefaultSize, 0 )
        CategoryControlsSizer.Add( self.m_buttonUpdateCategory, 0, wx.ALL, 5 )
        self.m_buttonUpdateCategory.Bind(wx.EVT_BUTTON, self.on_category_update)
        self.m_buttonUpdateCategory.Disable()
        
        self.m_buttonCancelCategory = wx.Button( self, wx.ID_ANY, _(u"Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
        CategoryControlsSizer.Add( self.m_buttonCancelCategory, 0, wx.ALL, 5 )
        self.m_buttonCancelCategory.Bind(wx.EVT_BUTTON, self.on_category_cancel)
        self.m_buttonCancelCategory.Disable()
        
        # ----
        
        CategorySizer.Add( CategoryControlsSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        CategorySizer.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
        
        # --

        OuterSizer.Add( CategorySizer, 0, wx.EXPAND, 5 )
        
        # -- LOG SIZER 
        
        LogsSizer = wx.BoxSizer( wx.VERTICAL )
        
        self.m_listCtrl = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, 160), style=wx.LC_REPORT )
        LogsSizer.Add( self.m_listCtrl, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_listctrl_select)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_listctrl_deselect)
        
        self.m_listCtrl.AppendColumn("Description", width=250)
        self.m_listCtrl.AppendColumn("Start", width=150)
        self.m_listCtrl.AppendColumn("End", width=150)
        self.m_listCtrl.AppendColumn("Spent", width=50)
        self.m_listCtrl.AppendColumn("Billed", width=50)
        
        
        LogsButtonSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_buttonStartLog = wx.Button( self, wx.ID_ANY, _(u"Start"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonStartLog.Bind(wx.EVT_BUTTON, self.on_listctrl_start)
        LogsButtonSizer.Add( self.m_buttonStartLog, 0, wx.ALL, 5 )
        self.m_buttonStartLog.Disable()
        
        self.m_buttonStopLog = wx.Button( self, wx.ID_ANY, _(u"Stop"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonStopLog.Bind(wx.EVT_BUTTON, self.on_listctrl_stop)
        LogsButtonSizer.Add( self.m_buttonStopLog, 0, wx.ALL, 5 )
        
        self.m_buttonEditLog = wx.Button( self, wx.ID_ANY, _(u"Edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonEditLog.Bind(wx.EVT_BUTTON, self.on_listctrl_edit)
        LogsButtonSizer.Add( self.m_buttonEditLog, 0, wx.ALL, 5 )
        
        self.m_buttonDelLog = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonDelLog.Bind(wx.EVT_BUTTON, self.on_listctrl_del)
        LogsButtonSizer.Add( self.m_buttonDelLog, 0, wx.ALL, 5 )
        
        self.m_buttonExportLog = wx.Button( self, wx.ID_ANY, _(u"Export"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonExportLog.Bind(wx.EVT_BUTTON, self.on_export)
        LogsButtonSizer.Add( self.m_buttonExportLog, 0, wx.ALL, 5 )
                
        LogsSizer.Add(LogsButtonSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        # ---- TIME SIZER

        TimeSizer = wx.BoxSizer( wx.VERTICAL )

        self.m_labelTimeSpent = wx.StaticText( self, wx.ID_ANY, _(u"Total time spent for current category:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_labelTimeSpent.Wrap( -1 )

        TimeSizer.Add( self.m_labelTimeSpent, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.m_valueTimeSpent = wx.StaticText( self, wx.ID_ANY, _(u"00:00:00"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_valueTimeSpent.Wrap( -1 )
        
        self.m_valueTimeSpent.SetFont( wx.Font( 20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

        self.m_valueCurrentTimeSpent = wx.StaticText( self, wx.ID_ANY, _(u"(+00:00:00)"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_valueCurrentTimeSpent.Wrap( -1 )

        self.m_valueCurrentTimeSpent.SetFont( wx.Font( 10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

        TimeSizer.Add( self.m_valueTimeSpent, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        TimeSizer.Add( self.m_valueCurrentTimeSpent, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        # ----
        
        LogsSizer.Add( TimeSizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        LogsSizer.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
        
        # --

        OuterSizer.Add( LogsSizer, 1, wx.EXPAND, 5 )

        # -- LOG CREATOR
        
        LogCreatorSizer = wx.BoxSizer( wx.VERTICAL )

        LogCreatorControlSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.m_newDescription = wx.TextCtrl( self, wx.ID_ANY, _(u""), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_newDescription.SetHint("New Description...")
        self.m_newDescription.SetMinSize( wx.Size( 400,-1 ) )

        LogCreatorControlSizer.Add( self.m_newDescription, 0, wx.ALL, 5 )

        self.m_newCreate = wx.Button( self, wx.ID_ANY, _(u"Start"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_newCreate.Bind(wx.EVT_BUTTON, self.on_log_create)
        LogCreatorControlSizer.Add( self.m_newCreate, 0, wx.ALL, 5 )

        LogCreatorSizer.Add( LogCreatorControlSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        # --

        OuterSizer.Add( LogCreatorSizer, 0, wx.EXPAND, 5 )

        self.SetSizer( OuterSizer )
        self.Layout()

        self.Centre( wx.BOTH )
        
        self.SetMenuBar(self.m_menuBar)
        self.Bind(wx.EVT_MENU, self.menu_handler)

        self.billed_colour = wx.Colour(250, 218, 221)
            
        self.m_Timer = wx.Timer()
        self.m_Stopwatch = wx.StopWatch()
        self.m_TimeInterval = 1000 # 1 second
        self.m_Timer.Bind(wx.EVT_TIMER, self.on_timer)
        self.m_ongoingTime = 0
    
        last_log = self.logs.get_log_by_id(self.logs.AppState.get_last_entry_id())
        if last_log is None:
            self.m_comboCategory.SetSelection(0)
            self.task_ongoing = False
        else:
            last_cat = self.logs.get_cat_name_by_id(last_log.cat_id)
            self.task_ongoing = last_log.time_end == ""
            self.m_comboCategory.SetSelection(self.m_comboCategoryChoices.index(last_cat))
            
            if self.task_ongoing:
                self.m_ongoingTime = int(time.time()) - time.mktime(time.strptime(last_log.time_start))
                self.m_Timer.Start(self.m_TimeInterval)
        
        self.current_category = self.m_comboCategory.GetSelection()
        self.total_time_spent = 0
        
        self.m_listCtrl.DeleteAllItems()
        self.refresh_combobox_choices()
        if len(self.m_comboCategoryChoices) > 0:
            self.get_category_logs(self.m_comboCategory.GetValue())
        
    def __del__( self ):
        pass
    
    def reset(self):
        try:
            db_file = open("db_directory.txt", "x")
            db_file = open("db_directory.txt", "w")
            db_file.write("TimeLogger.db")
        except:
            pass
        finally:
            db_file = open("db_directory.txt")
        
        db_directory = db_file.readline().strip()
        self.logs = LogBook(db_directory)
        self.m_comboCategoryChoices = self.logs.get_cat_names()

        self.m_ongoingTime = 0
        
        last_log = self.logs.get_log_by_id(self.logs.AppState.get_last_entry_id())
        if last_log is None:
            self.m_comboCategory.SetSelection(0)
            self.task_ongoing = False
        else:
            last_cat = self.logs.get_cat_name_by_id(last_log.cat_id)
            self.task_ongoing = last_log.time_end == ""
            self.m_comboCategory.SetSelection(self.m_comboCategoryChoices.index(last_cat))
            
            if self.task_ongoing:
                self.m_ongoingTime = int(time.time()) - time.mktime(time.strptime(last_log.time_start))
                self.m_Timer.Start(self.m_TimeInterval)
        
        self.current_category = self.m_comboCategory.GetSelection()
        self.total_time_spent = 0
        
        self.m_listCtrl.DeleteAllItems()
        self.refresh_combobox_choices()
        if len(self.m_comboCategoryChoices) > 0:
            self.get_category_logs(self.m_comboCategory.GetValue())
    
    def menu_handler(self, event):
        event_id = event.GetId()
        if event_id == wx.ID_NEW:
            self.new_db(0)
        if event_id == wx.ID_OPEN:
            self.open_db(0)
        if event_id == wx.ID_SAVEAS:
            self.on_full_export(0)
        if event_id == wx.ID_EXIT:
            self.on_window_close(0)
        if event_id == wx.ID_ABOUT:
            self.about_app()
        if event_id == wx.ID_INFO:
            webbrowser.open('https://www.linkedin.com/in/eason-c/')
            
    def new_db(self, event):
        with wx.FileDialog(self, "Open db file", wildcard="db files (*.db)|*.db",
                           style=wx.FD_OPEN) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
            try:
                with open("db_directory.txt", "w") as file:
                    new_path = fileDialog.GetPath()
                    file.write(new_path)
            except Exception as e:
                wx.MessageDialog(self, f"Error Occured: {e}", "Open", wx.ICON_ERROR).ShowModal()
                return
        self.reset()
        
    def open_db(self, event):
        with wx.FileDialog(self, "Open db file", wildcard="db files (*.db)|*.db",
                           style=wx.FD_OPEN) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
            try:
                with open("db_directory.txt", "w") as file:
                    new_path = fileDialog.GetPath()
                    file.write(new_path)
            except Exception as e:
                wx.MessageDialog(self, f"Error Occured: {e}", "Open", wx.ICON_ERROR).ShowModal()
                return
        self.reset()
                
    def about_app(self):
        s = StartupScreen(self)

    def on_timer(self, event):
        self.m_ongoingTime += 1
        
        self.update_current_time(self.m_ongoingTime)
    
    def get_category_logs(self, cat):
        self.m_listCtrl.DeleteAllItems()
        cat_id = self.logs.get_cat_id_by_name(cat)
        cat_logs = self.logs.get_logs(cat_id)
        self.total_time_spent = 0
        for i, entry in enumerate(cat_logs):
            if entry.time_end != "":
                h,m,s = self.format_time(self.str_time_to_epoch(entry.time_end) - self.str_time_to_epoch(entry.time_start))
                self.m_listCtrl.Append([entry.details, entry.time_start, entry.time_end, '{:d}:{:02d}:{:02d}'.format(h, m, s), entry.billed])            
                self.total_time_spent += self.get_time_spent(i)
            else:
                self.m_listCtrl.Append([entry.details, entry.time_start, entry.time_end, "??:??:??", entry.billed])
            if entry.billed:
                self.m_listCtrl.SetItemBackgroundColour(self.m_listCtrl.GetItemCount()-1, self.billed_colour)
            
        self.update_total_time()
    
    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s
    
    def str_time_to_epoch(self, time_s):
        struct_time = time.strptime(time_s)
        
        return int(time.mktime(struct_time))
        
    def update_total_time(self, add_time=0):
        h,m,s = self.format_time(int(self.total_time_spent + add_time))
        self.total_time_spent += add_time
        #print(h, m, s)
        self.m_valueTimeSpent.SetLabel('{:d}:{:02d}:{:02d}'.format(h, m, s))
    
    def update_current_time(self, time):
        h,m,s = self.format_time(int(time))
        self.m_valueCurrentTimeSpent.SetLabel('(+{:02d}:{:02d}:{:02d})'.format(h, m, s))
    
    def get_time_spent(self, row_idx):
        row_time_start = self.m_listCtrl.GetItem(row_idx, 1).GetText()
        row_time_end = self.m_listCtrl.GetItem(row_idx, 2).GetText()

        return self.str_time_to_epoch(row_time_end) - self.str_time_to_epoch(row_time_start) 
    
    def on_combobox_select(self, event):
        if self.task_ongoing:
            self.m_comboCategory.SetSelection(self.current_category)
            wx.MessageDialog(self, f"There is a task still running.", "Warning", wx.OK|wx.CENTRE|wx.ICON_WARNING).ShowModal()
            return
    
        combobox_value = self.m_comboCategory.GetValue()
        self.m_buttonStartLog.Disable()
        
        self.get_category_logs(combobox_value)
        self.current_category = self.m_comboCategory.GetSelection()
    
    def refresh_combobox_choices(self):
        self.m_comboCategory.Clear()
        self.m_comboCategory.AppendItems(self.m_comboCategoryChoices)
        self.m_comboCategory.SetSelection(0)
        
    def on_category_create(self, event):
        category = self.m_textCategory.GetLineText(0)
        if len(category.strip()) <= 0:
            warning_msg = wx.MessageDialog(self, "Category name blank.", "Warning", wx.OK|wx.CENTRE|wx.ICON_ERROR)
            warning_msg.ShowModal()
            return
        #print("test", category)
        
        cat_count = len(self.m_comboCategoryChoices)
        self.logs.add_cat(Category(cat_count, name=category))
        self.m_comboCategoryChoices.append(category)
        self.m_comboCategory.Append(category)
        
        self.m_comboCategory.SetSelection(self.m_comboCategory.GetCount()-1)
        
        self.get_category_logs(category)
        self.m_textCategory.SetValue("")
            
    def on_category_edit(self, event):
        if len(self.m_comboCategoryChoices) == 0:
            return
        combobox_value = self.m_comboCategory.GetValue()
        combobox_value_index = self.m_comboCategory.GetSelection()
        
        self.m_textCategory.SetValue(combobox_value)
        
        self.m_buttonUpdateCategory.Enable()
        self.m_buttonCancelCategory.Enable()
        self.m_buttonCreateCategory.Disable()
    
    def on_category_update(self, event):
        updated_category = self.m_textCategory.GetLineText(0)
        category = self.m_comboCategory.GetValue()
        category_index = self.m_comboCategory.GetSelection()
        
        #print(category_index, category, "->", updated_category)
        
        self.m_comboCategoryChoices[category_index] = updated_category
        self.logs.update_cat_name_by_name(category, updated_category)
        
        self.refresh_combobox_choices()
        self.m_comboCategory.SetSelection(category_index)
        self.m_textCategory.SetValue("")
        
        self.m_buttonUpdateCategory.Disable()
        self.m_buttonCancelCategory.Disable()
        self.m_buttonCreateCategory.Enable()
    
    def on_category_cancel(self, event):
        self.m_textCategory.SetValue("")
        
        self.m_buttonUpdateCategory.Disable()
        self.m_buttonCancelCategory.Disable()
        self.m_buttonCreateCategory.Enable()
        
    def on_category_del(self, event):
        """Deletes category & records"""
        if len(self.m_comboCategoryChoices) == 0:
            return
        category = self.m_comboCategory.GetValue()
        
        warning_msg = wx.MessageDialog(self, f"Delete category '{category}'?", "Warning", wx.OK|wx.CANCEL|wx.CENTRE|wx.ICON_WARNING)
        
        if warning_msg.ShowModal() == wx.ID_OK:
            try:
                self.logs.del_cat_by_name(category)
                self.m_comboCategoryChoices.remove(category)
            
                self.refresh_combobox_choices()
                self.m_listCtrl.DeleteAllItems()
                
                #self.get_category_logs(self.m_comboCategory.GetValue())
            except sqlite3.IntegrityError:
                wx.MessageDialog(self, f"Cannot delete category '{category}' with logs.", \
                                 "Error", wx.OK|wx.CENTRE|wx.ICON_ERROR).ShowModal()
        if len(self.m_comboCategoryChoices) > 0:
            self.get_category_logs(category)
            self.current_category = self.m_comboCategory.GetSelection()
                
    def create_log(self, details):
        if self.task_ongoing:
            wx.MessageDialog(self, f"There is a task still running.", "Warning", wx.OK|wx.CENTRE|wx.ICON_WARNING).ShowModal()
            return
        if len(self.m_comboCategoryChoices) < 1:
            wx.MessageDialog(self, f"Not a valid category", "Warning", wx.OK|wx.CENTRE|wx.ICON_WARNING).ShowModal()
            return
        start_time = time.asctime(time.localtime())
        self.m_listCtrl.Append([details, start_time, "", "??:??:??", "0"])

        last_entry_id = self.logs.add_log(LogEntry(cat_id=self.logs.get_cat_id_by_name(self.m_comboCategory.GetValue()), \
                                   time_start=start_time, details=details))

        last_row_idx = self.m_listCtrl.GetItemCount() - 1
        self.m_listCtrl.EnsureVisible(last_row_idx)
        self.task_ongoing = True
        self.logs.update_last_entry(last_entry_id)
        self.m_Timer.Start(self.m_TimeInterval)
    
    def on_listctrl_select(self, event):
        """Runs when a row is pressed"""
        self.m_buttonStartLog.Enable() 
    
    def on_listctrl_deselect(self, event):
        self.m_buttonStartLog.Disable()
        
    def on_listctrl_start(self, event):
        row_idx = self.m_listCtrl.GetFocusedItem()
        if row_idx == -1 or row_idx >= self.m_listCtrl.GetItemCount():
            row_idx = self.m_listCtrl.GetItemCount()-1
        row_desc = self.m_listCtrl.GetItem(row_idx, 0).GetText()
        self.create_log(row_desc)
        
    def on_detail_update(self, row_idx, event):
        """Updates row description"""
        new_desc = self.m_newDescription.GetLineText(0)
        self.m_listCtrl.SetItem(row_idx, 0, new_desc)
        self.m_newDescription.SetValue("")
        
        row_time_start = self.m_listCtrl.GetItem(row_idx, 1).GetText()
        self.logs.update_log_details_by_start(row_time_start, new_desc)
        
        self.m_newCreate.SetLabel("Create")
        self.m_newCreate.Bind(wx.EVT_BUTTON, self.on_log_create)
    
    def on_listctrl_edit(self, event):
        """Enables row description editing"""
        if self.m_listCtrl.GetItemCount() == 0:
            return
        row_idx = self.m_listCtrl.GetFocusedItem()
        current_desc = self.m_listCtrl.GetItem(row_idx, 0)
        self.m_newDescription.SetValue(current_desc.GetText())
        #print(current_desc.GetText())
        
        self.m_newCreate.SetLabel("Update")
        self.m_newCreate.Bind(wx.EVT_BUTTON, partial(self.on_detail_update, row_idx))
    
    def on_listctrl_del(self, event):
        """Deletes selected row"""
        if self.m_listCtrl.GetItemCount() == 0:
            return
        row_idx = self.m_listCtrl.GetFocusedItem()
        if row_idx == -1 or row_idx >= self.m_listCtrl.GetItemCount():
            row_idx = self.m_listCtrl.GetItemCount()-1
        row_time_start = self.m_listCtrl.GetItem(row_idx, 1).GetText()
        row_time_end = self.m_listCtrl.GetItem(row_idx, 2).GetText()
        if row_time_end != "":
            time_spent = self.get_time_spent(row_idx)
            print(time_spent)
            self.update_total_time(-time_spent)
        
        self.task_ongoing = False
        self.m_ongoingTime = 0
        self.m_Timer.Stop()
        self.m_valueCurrentTimeSpent.SetLabel("(+00:00:00)")
        row_time_start = self.m_listCtrl.GetItem(row_idx, 1).GetText()
        time_spent = self.get_time_spent(row_idx)
        print(time_spent)
        self.update_total_time(-time_spent)
        self.m_listCtrl.DeleteItem(row_idx)
        self.logs.del_log_by_time(row_time_start)

        
    def on_listctrl_stop(self, event):
        """Stops the current task"""
        if self.m_listCtrl.GetItemCount() == 0:
            return
        last_row_idx = self.m_listCtrl.GetItemCount() - 1
        if self.m_listCtrl.GetItemText(last_row_idx, 2) != "":
            wx.MessageDialog(self, f"No task currently running.", "Warning", wx.OK|wx.CENTRE|wx.ICON_WARNING).ShowModal()
            return
        
        end_time = time.asctime(time.localtime())
        self.m_listCtrl.SetItem(last_row_idx, 2, end_time)
        
        h,m,s = self.format_time(self.str_time_to_epoch(end_time) - 
                                 self.str_time_to_epoch(self.m_listCtrl.GetItemText(last_row_idx, 1)))
        self.m_listCtrl.SetItem(last_row_idx, 3, '{:d}:{:02d}:{:02d}'.format(h, m, s))        
        
        #print(self.get_time_spent(last_row_idx))

        row_time_start = self.m_listCtrl.GetItem(last_row_idx, 1).GetText()
        self.logs.update_log_end_by_start(row_time_start, end_time)
        self.update_total_time(self.get_time_spent(last_row_idx))
        
        self.task_ongoing = False
        self.m_ongoingTime = 0
        self.m_Timer.Stop()
        self.m_valueCurrentTimeSpent.SetLabel("(+00:00:00)")
        
    
    def on_log_create(self, event):
        """Does not clear m_newDescription text"""
        log_desc = self.m_newDescription.GetLineText(0)
        
        self.create_log(log_desc)
        
            
    def on_export(self, event):
        if self.m_listCtrl.GetItemCount() == 0:
            return
        index = self.m_listCtrl.GetFirstSelected()
        selected = [index]
        while index != -1:
            index = self.m_listCtrl.GetNextSelected(index)
            selected.append(index)
        dlg = wx.MessageDialog(self, "What do you want to export?", "Export", wx.HELP|wx.YES_NO|wx.CANCEL)
        dlg.SetYesNoCancelLabels("Full", "Unbilled", "Selected")
        dlg.SetHelpLabel("Cancel")
        selection = dlg.ShowModal()
        if selection == wx.ID_HELP:
            return
        dlg = wx.MessageDialog(self, "Mark rows as billed?", "Bill", wx.YES_NO)
        bill = dlg.ShowModal()
        with wx.FileDialog(self, "Open txt file", wildcard="txt files (*.txt)|*.txt",
                           style=wx.FD_OPEN) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
            try:
                with open(fileDialog.GetPath(), "w") as file:
                    exported = []
                    for row in range(self.m_listCtrl.GetItemCount()):
                        if selection == wx.ID_CANCEL and row not in selected:
                            continue
                        start_time = self.m_listCtrl.GetItem(row, 1).GetText()
                        if selection == wx.ID_NO and self.logs.get_billed_by_time(start_time)[0] == 1:
                            continue
                        desc = self.m_listCtrl.GetItem(row, 0).GetText()
                        end_time = self.m_listCtrl.GetItem(row, 2).GetText()
                        if end_time == "":
                            wx.MessageDialog(self, f"Skipping ongoing task.", "Export", wx.ICON_INFORMATION).ShowModal()
                            continue
                        time_spent = self.m_listCtrl.GetItem(row, 3).GetText()
                        file.write(f"{desc},{start_time},{end_time},{time_spent}\n")
                        exported.append((row, start_time))
            except Exception as e:
                wx.MessageDialog(self, f"Error Occured: {e}", "Export", wx.ICON_ERROR).ShowModal()
                return
            if bill == wx.ID_YES:
                for row, time in exported:
                    self.m_listCtrl.SetItemBackgroundColour(row, self.billed_colour)
                    self.logs.update_billed_by_time(time, 1)
        wx.MessageDialog(self, "Export Completed", "Export", wx.OK).ShowModal()
        self.get_category_logs(self.m_comboCategory.GetValue())
        
        
    def on_full_export(self, event):
        cats, logs, app_state = self.logs.get_full_database()
        with wx.DirDialog(self, "Open Folder", style=wx.FD_OPEN) as DirDialog:
            if DirDialog.ShowModal() == wx.ID_CANCEL:
                    return
            try:
                directory = DirDialog.GetPath()
                print(os.path.join(directory, "categories.csv"))
                with open(os.path.join(directory, "categories.csv"), "w") as file:
                    for c in cats:
                        file.write(str(c)[1:-1])
                with open(os.path.join(directory, "logs.csv"), "w") as file:
                    for l in logs:
                        file.write(str(l)[1:-1])
                with open(os.path.join(directory, "app_state.csv"), "w") as file:
                    for a in app_state:
                        file.write(str(a)[1:-1])
            except Exception as e:
                wx.MessageDialog(self, f"Error Occured: {e}", "Open", wx.ICON_ERROR).ShowModal()
                return
        
    def on_window_close(self, event):
        if self.task_ongoing:
            choice = wx.MessageDialog(self, "There is a task currently ongoing. Close Anyway?", "Task Ongoing", wx.YES_NO).ShowModal()
            if choice == wx.ID_NO:
                return
        
        self.Destroy()
app = wx.App()
tl = TimeLogger(None)
tl.Show()
tl.about_app()
app.MainLoop()
