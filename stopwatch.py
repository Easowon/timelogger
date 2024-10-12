# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import math

import gettext
_ = gettext.gettext

###########################################################################
## Class Stopwatch
###########################################################################

class Stopwatch ( wx.Frame ):

    def __init__( self, parent ):
        self.m_hh_mm_ss = False
        self.m_hours = 0
        self.m_minutes = 0
        self.m_seconds = 0
        
        
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Time Logger"), pos = wx.DefaultPosition, size = wx.Size( 601,472 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        OuterSizer = wx.BoxSizer( wx.VERTICAL )

        TimeSizer = wx.BoxSizer( wx.VERTICAL )

        ClockSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.m_Time = wx.StaticText( self, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_Time.Wrap( -1 )
        self.m_Time.SetFont( wx.Font( 40, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
        ClockSizer.Add( self.m_Time, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )

        TimeSizer.Add( ClockSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.m_comboFormatChoices = ["Seconds","HH:MM:SS.SSS"]
        self.m_comboFormat = wx.ComboBox( self, wx.ID_ANY, _(u"Combo!"), wx.DefaultPosition, wx.DefaultSize, self.m_comboFormatChoices, 0 )
        self.m_comboFormat.Bind(wx.EVT_COMBOBOX, self.change_format)
        TimeSizer.Add( self.m_comboFormat, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        self.m_comboFormat.SetSelection(0)
        
        self.m_listCtrl = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, 160), style=wx.LC_REPORT )
        self.m_listCtrl.AppendColumn("Split", width=50)
        self.m_listCtrl.AppendColumn("Difference", width=100)
        self.m_listCtrl.AppendColumn("Time", width=100)
        TimeSizer.Add( self.m_listCtrl, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        OuterSizer.Add( TimeSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )

        ControlSizer = wx.BoxSizer( wx.VERTICAL )

        ButtonSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.m_StartPauseTimer = wx.Button( self, wx.ID_ANY, _(u"Start"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_StartPauseTimer.Bind(wx.EVT_BUTTON, self.on_initial_start)
        ButtonSizer.Add( self.m_StartPauseTimer, 0, wx.ALL, 5 )

        self.m_StopSplitResetTimer = wx.Button( self, wx.ID_ANY, _(u"Split"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_StopSplitResetTimer.Bind(wx.EVT_BUTTON, self.on_split)
        ButtonSizer.Add( self.m_StopSplitResetTimer, 0, wx.ALL, 5 )
        
        self.m_ExportData = wx.Button( self, wx.ID_ANY, _(u"Export"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_ExportData.Bind(wx.EVT_BUTTON, self.on_export)
        ButtonSizer.Add( self.m_ExportData, 0, wx.ALL, 5 )
        
        ControlSizer.Add( ButtonSizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )

        OuterSizer.Add( ControlSizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.SetSizer( OuterSizer )
        self.Layout()

        self.Centre( wx.BOTH )
        
        
        self.m_Timer = wx.Timer()
        self.m_Stopwatch = wx.StopWatch()
        self.m_TimeInterval = -1
        self.m_Timer.Bind(wx.EVT_TIMER, self.on_timer)
        
        self.reset_timer()
    
    def __del__( self ):
        pass
    
    def format_time(self, time=0):
        if self.m_hh_mm_ss:
            time_s = math.floor(time)
            milliseconds = time - time_s
            hours = time_s // 3600
            minutes = (time_s - hours * 60) // 60
            seconds = (time_s % 60) + milliseconds
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        
        return f"{time:012.3f}"

    def change_format(self, event):
        format_idx = self.m_comboFormat.GetSelection()
        if format_idx:
            self.m_hh_mm_ss = True
        else:
            self.m_hh_mm_ss = False
        
        #self.reset_timer()
        
    def reset_timer(self):
        self.m_hours = 0
        self.m_minutes = 0
        
        self.m_Time.SetLabel(self.format_time())
        self.m_listCtrl.DeleteAllItems()
        self.m_StopSplitResetTimer.Disable()
    
    def on_export(self, event):
        file = open("stopwatch_export.txt", "w")
        for row in range(self.m_listCtrl.GetItemCount()):
            split_n = self.m_listCtrl.GetItem(row, 0).GetText()
            split_diff = self.m_listCtrl.GetItem(row, 1).GetText()
            split_time = self.m_listCtrl.GetItem(row, 2).GetText()
            file.write(f"{split_n},{split_diff},{split_time}\n")
        file.close()
        
    def on_timer(self, event):
        time_s = float(self.m_Stopwatch.Time())/1000
        self.m_Time.SetLabel(self.format_time(time_s))
    
    def after_start_pressed(self):
        self.m_StopSplitResetTimer.Enable()
        self.m_StartPauseTimer.Bind(wx.EVT_BUTTON, self.on_pause)
        self.m_StartPauseTimer.SetLabel("Pause")
        self.m_StopSplitResetTimer.Bind(wx.EVT_BUTTON, self.on_split)
        self.m_StopSplitResetTimer.SetLabel("Split")
        self.m_StopSplitResetTimer.Enable()
    
    def on_initial_start(self, event):
        self.m_Timer.Start(self.m_TimeInterval)
        self.m_Stopwatch.Start()
        
        self.after_start_pressed()

    def on_start(self, event):
        self.m_Timer.Start(self.m_TimeInterval)
        self.m_Stopwatch.Resume()
        
        self.after_start_pressed()
    
    def on_pause(self, event):
        self.m_Timer.Stop()
        self.m_Stopwatch.Pause()
        
        self.m_StopSplitResetTimer.Bind(wx.EVT_BUTTON, self.on_reset)
        self.m_StopSplitResetTimer.SetLabel("Reset")
        self.m_StartPauseTimer.Bind(wx.EVT_BUTTON, self.on_start)
        self.m_StartPauseTimer.SetLabel("Start")
    
    def on_split(self, event):
        n_rows = self.m_listCtrl.GetItemCount()
        previous = 0
        if n_rows > 0:
            previous = float(self.m_listCtrl.GetItemText(n_rows-1, 2))
        time_s = float(self.m_Stopwatch.Time())/1000
        lap_n = n_rows+1
        data = [lap_n,round(time_s-previous, 3),time_s]
        self.m_listCtrl.Append(data)
        self.m_listCtrl.EnsureVisible(n_rows)
    
    def on_reset(self, event):
        self.reset_timer()
        self.m_StartPauseTimer.Bind(wx.EVT_BUTTON, self.on_initial_start)
        self.m_StartPauseTimer.SetLabel("Start")

app = wx.App()
sw = Stopwatch(None)
sw.Show()
app.MainLoop()
