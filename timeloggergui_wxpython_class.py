import wx
import wx.xrc
import time
from functools import partial
import sqlite3
from timelogger_model import *

import gettext
_ = gettext.gettext

###########################################################################
## Class TimeLogger
###########################################################################

class TimeLogger ( wx.Frame ):

    def __init__( self, parent ):
        
        self.logs = LogBook("TimeLogger.db")
        
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Time Logger"), pos = wx.DefaultPosition, size = wx.Size( 601,472 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        OuterSizer = wx.BoxSizer( wx.VERTICAL )

        # -- CATEGORY SIZER
        
        CategorySizer = wx.BoxSizer( wx.VERTICAL )

        self.m_comboCategoryChoices = self.logs.get_cat_names()
        self.m_comboCategory = wx.ComboBox( self, wx.ID_ANY, _(u""), wx.DefaultPosition, wx.Size(200, 30), self.m_comboCategoryChoices, 0)
        self.m_comboCategory.SetSelection(0)
        self.m_comboCategory.Bind(wx.EVT_COMBOBOX, self.on_combobox_select)
        
        CategorySizer.Add( self.m_comboCategory, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        # ---- CATEGORY CONTROLS SIZER
        
        CategoryControlsSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_textCategory = wx.TextCtrl(self, wx.ID_ANY, _(u""), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCategory.SetHint("Category Name...")
        CategoryControlsSizer.Add( self.m_textCategory, 0, wx.ALL, 5 )

        self.m_buttonCreateCategory = wx.Button( self, wx.ID_ANY, _(u"Create"), wx.DefaultPosition, wx.DefaultSize, 0 )
        CategoryControlsSizer.Add( self.m_buttonCreateCategory, 0, wx.ALL, 5 )
        self.m_buttonCreateCategory.Bind(wx.EVT_BUTTON, self.on_category_create)

        self.m_buttonEditCategory = wx.Button( self, wx.ID_ANY, _(u"Edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        CategoryControlsSizer.Add( self.m_buttonEditCategory, 0, wx.ALL, 5 )
        self.m_buttonEditCategory.Bind(wx.EVT_BUTTON, self.on_category_edit)

        self.m_buttonDelCategory = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
        CategoryControlsSizer.Add( self.m_buttonDelCategory, 0, wx.ALL, 5 )
        self.m_buttonDelCategory.Bind(wx.EVT_BUTTON, self.on_category_del)
        
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
        self.m_listCtrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_listctrl_edit)
            
        self.m_listCtrl.AppendColumn("Row", width=40)
        self.m_listCtrl.AppendColumn("Description", width=200)
        self.m_listCtrl.AppendColumn("Start", width=150)
        self.m_listCtrl.AppendColumn("End", width=150)
        
        LogsButtonSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_buttonStartStopLog = wx.Button( self, wx.ID_ANY, _(u"Stop"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonStartStopLog.Bind(wx.EVT_BUTTON, self.on_listctrl_stop)
        LogsButtonSizer.Add( self.m_buttonStartStopLog, 0, wx.ALL, 5 )
        
        self.m_buttonEditLog = wx.Button( self, wx.ID_ANY, _(u"Edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonEditLog.Bind(wx.EVT_BUTTON, self.on_listctrl_edit)
        LogsButtonSizer.Add( self.m_buttonEditLog, 0, wx.ALL, 5 )

        self.m_buttonDelLog = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonDelLog.Bind(wx.EVT_BUTTON, self.on_listctrl_del)
        LogsButtonSizer.Add( self.m_buttonDelLog, 0, wx.ALL, 5 )
                
        LogsSizer.Add(LogsButtonSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        # ---- TIME SIZER

        TimeSizer = wx.BoxSizer( wx.VERTICAL )

        self.m_labelTimeSpent = wx.StaticText( self, wx.ID_ANY, _(u"Total Time Spent:"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_labelTimeSpent.Wrap( -1 )

        TimeSizer.Add( self.m_labelTimeSpent, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.m_valueTimeSpent = wx.StaticText( self, wx.ID_ANY, _(u"HH:MM:SS"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_valueTimeSpent.Wrap( -1 )

        self.m_valueTimeSpent.SetFont( wx.Font( 20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

        TimeSizer.Add( self.m_valueTimeSpent, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

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
        
        if len(self.m_comboCategoryChoices) > 0:
            self.get_category_logs(self.m_comboCategory.GetValue())   
    
    def __del__( self ):
        pass
    
    def get_category_logs(self, cat):
        self.m_listCtrl.DeleteAllItems()
        cat_id = self.logs.get_cat_id_by_name(cat)
        cat_logs = self.logs.get_logs(cat_id)
        
        for i, entry in enumerate(cat_logs):
            self.m_listCtrl.Append([i, entry.details, entry.time_start, entry.time_end])
    
    def on_combobox_select(self, event):
        combobox_value = self.m_comboCategory.GetValue()
        print(combobox_value)
        self.get_category_logs(combobox_value)
    
    def refresh_combobox_choices(self):
        self.m_comboCategory.Clear()
        self.m_comboCategory.AppendItems(self.m_comboCategoryChoices)
        self.m_comboCategory.SetSelection(0)
        
    def on_category_create(self, event):
        category = self.m_textCategory.GetLineText(0)
        #print("test", category)
        cat_count = len(self.m_comboCategoryChoices)
        self.logs.add_cat(Category(cat_count, name=category))
        self.m_comboCategoryChoices.append(category)
        self.m_comboCategory.Append(category)
        
        self.m_comboCategory.SetSelection(self.m_comboCategory.GetCount()-1)
        
        self.get_category_logs(category)
            
    def on_category_edit(self, event):
        category = self.m_textCategory.GetLineText(0)
        combobox_value = self.m_comboCategory.GetValue()
        combobox_value_index = self.m_comboCategory.GetSelection()
        
        print(combobox_value_index, combobox_value, "->", category)
        
        self.m_comboCategoryChoices[combobox_value_index] = category
        self.logs.update_cat_name_by_name(combobox_value, category)
        
        self.refresh_combobox_choices()
        
    def on_category_del(self, event):
        category = self.m_textCategory.GetLineText(0)
        
        if category in self.m_comboCategoryChoices:
            self.m_comboCategoryChoices.remove(category)
            self.logs.del_cat_by_name(category)
        
            self.refresh_combobox_choices()
    
    def on_listctrl_select(self, event):
        row_idx = self.m_listCtrl.GetFocusedItem()
        print(row_idx)
    
    def on_listctrl_edit(self, event):
        row_idx = self.m_listCtrl.GetFocusedItem()
        current_desc = self.m_listCtrl.GetItem(row_idx, 1)
        self.m_newDescription.SetValue(current_desc.GetText())
        print(current_desc.GetText())
        
        self.m_newCreate.SetLabel("Edit")
        self.m_newCreate.Bind(wx.EVT_BUTTON, partial(self.on_desc_edit, row_idx))
        
    def on_desc_edit(self, row_idx, event):
        new_desc = self.m_newDescription.GetLineText(0)
        self.m_listCtrl.SetItem(row_idx, 1, new_desc)
        
        self.m_newCreate.SetLabel("Create")
        self.m_newCreate.Bind(wx.EVT_BUTTON, self.on_log_create)
        
    def on_listctrl_del(self, event):
        row_idx = self.m_listCtrl.GetFocusedItem()
        self.m_listCtrl.DeleteItem(row_idx)
        
    
    def on_listctrl_stop(self, event):
        row_idx = self.m_listCtrl.GetFocusedItem()
        end_time = time.asctime(time.localtime())
        self.m_listCtrl.SetItem(row_idx, 3, end_time)
    
    def on_log_create(self, event):
        log_desc = self.m_newDescription.GetLineText(0)
        log_start_time = time.asctime(time.localtime())
        #time.strptime(log_start_time), time.mktime(time.strptime(log_start_time)))
        
        last_row_idx = self.m_listCtrl.GetItemCount() - 1
        row_val = 0 if self.m_listCtrl.IsEmpty() else int(self.m_listCtrl.GetItem(last_row_idx,0).GetText()) + 1
        self.m_listCtrl.Append([row_val, log_desc, log_start_time, ""])
        '''
        print("get string selection", self.m_comboCategory.GetValue())
        
        print(LogEntry(row_val, cat_id=self.logs.get_cat_id_by_name(self.m_comboCategory.GetValue()), \
                                   time_start=log_start_time, details=log_desc))
        '''

        self.logs.add_log(LogEntry(row_val, cat_id=self.logs.get_cat_id_by_name(self.m_comboCategory.GetValue()), \
                                   time_start=log_start_time, details=log_desc))
        
        self.m_listCtrl.EnsureVisible(last_row_idx+1)
                
        #print(log_desc, log_start_time, time.strptime(log_start_time), time.mktime(time.strptime(log_start_time)))
        
        
        
app = wx.App()
tl = TimeLogger(None)
tl.Show()
app.MainLoop()
