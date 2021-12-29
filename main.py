import time
from datetime import datetime

import wx
from wx.lib import plot as wxplot
from wx.lib import newevent as wxnewevent

import threading
import numpy  as np
import serial

from SerialDialog import SerialDialog


# -----------------------------------------------------------
SeiralRxEvent, EVT_SERIALRX = wxnewevent.NewEvent()

# ----------------------------------------------------------

ID_START = wx.NewId()
ID_STOP = wx.NewId()
ID_SAVE = wx.NewId()

def _draw_test_object():

    data = 2. * np.pi * np.arange(-200, 200) / 200.
    data.shape = (200, 2)
    data[:, 1] = np.sin(data[:, 0])
    marker = wxplot.PolyMarker(data,
                               legend='Green Markers',
                               colour='green',
                               marker='circle',
                               size=1,
                               )
    # 50 points cos function, plotted as red line and markers
    data1 = 2. * np.pi * np.arange(-100, 100) / 100.
    data1.shape = (100, 2)
    data1[:, 1] = np.cos(data1[:, 0])
    lines = wxplot.PolySpline(data1, legend='Red Line', colour='black')
    markers3 = wxplot.PolyMarker(data1,
                                 legend='Red Dot',
                                 colour='red',
                                 marker='circle',
                                 size=1,
                                 )

    return wxplot.PlotGraphics([marker, lines, markers3],
                               "Graph Title",
                               "X Axis",
                               "Y Axis",
                               )

class ControlPlanel(wx.Panel):
    
    def __init__(self, parent, size):
        super().__init__(parent, size=size)

        self.staticbox_control = wx.StaticBox(self, label='Control')

        self.button_start = wx.Button(self, label='Start', id=ID_START)
        self.button_stop = wx.Button(self, label='Stop', id=ID_STOP)
        self.button_save = wx.Button(self, label='Save', id=ID_SAVE)
        self.label_log = wx.StaticText(self, label='Log:')
        self.textctrl_log = wx.TextCtrl(self, size=(425,25))

        self._layout()
    
    def _layout(self):

        sizer_ver = wx.BoxSizer(wx.VERTICAL)
        length = 2
        log_length = 10
        flexgridsizer = wx.FlexGridSizer(cols=6, hgap=2, vgap=2)
        sizer_box = wx.StaticBoxSizer(self.staticbox_control)
        flexgridsizer.Add(self.button_start, length, wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.button_stop, length, wx.CENTER)
        flexgridsizer.Add(self.button_save, length, wx.CENTER)
        flexgridsizer.Add(self.label_log, length, wx.CENTER)
        flexgridsizer.Add(self.textctrl_log, log_length, wx.CENTER)
        sizer_box.Add(flexgridsizer, 0, wx.EXPAND, 0)
        sizer_ver.Add(sizer_box)
        self.SetSizer(sizer_ver)

class SettingPlanel(wx.Panel):

    def __init__(self, parent, size):
        super().__init__(parent, size=size)
    
        self.staticbox_date_analyze = wx.StaticBox(self, label='Data Analyze')

        self.label_scale_factor = wx.StaticText(self.staticbox_date_analyze, label='Scale factor:')
        self.textctrl_scale_factor = wx.TextCtrl(self.staticbox_date_analyze)

        self.label_mean_windowsize = wx.StaticText(self.staticbox_date_analyze, label='Mean window size:')
        self.textctrl_mean_windowsize = wx.TextCtrl(self.staticbox_date_analyze)

        self.label_slide_windowsize = wx.StaticText(self.staticbox_date_analyze, label='Slide window size:')
        self.textctrl_slide_windowsize = wx.TextCtrl(self.staticbox_date_analyze)

        self.label_sample_size = wx.StaticText(self.staticbox_date_analyze, label='Sample size:')
        self.textctrl_sample_size = wx.TextCtrl(self.staticbox_date_analyze)

        self.label_std = wx.StaticText(self.staticbox_date_analyze, label='Standard deviation:')
        self.textctrl_std = wx.TextCtrl(self.staticbox_date_analyze)

        self.label_select_datasize =  wx.StaticText(self.staticbox_date_analyze, label='Select data size:')
        self.textctrl_select_datasize = wx.TextCtrl(self.staticbox_date_analyze)

        self.label_error_datasize =  wx.StaticText(self.staticbox_date_analyze, label='Error data size:')
        self.textctrl_error_datasize = wx.TextCtrl(self.staticbox_date_analyze)

        self._layout()

    def _layout(self):

        label_length = 1
        textctrl_length = 2
        sizer_ver = wx.BoxSizer(wx.VERTICAL)
        
        flexgridsizer = wx.FlexGridSizer(cols=6, hgap=2, vgap=2)
        sizer_box = wx.StaticBoxSizer(self.staticbox_date_analyze)
        
        flexgridsizer.Add(self.label_scale_factor, label_length, wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_scale_factor, textctrl_length,  wx.CENTER)

        flexgridsizer.Add(self.label_mean_windowsize, label_length,  wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_mean_windowsize, textctrl_length, wx.CENTER)

        flexgridsizer.Add(self.label_slide_windowsize, label_length,  wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_slide_windowsize, textctrl_length, wx.CENTER)

        flexgridsizer.Add(self.label_std, label_length, wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_std, textctrl_length, wx.CENTER)

        flexgridsizer.Add(self.label_sample_size, label_length, wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_sample_size, textctrl_length, wx.CENTER)

        flexgridsizer.Add(self.label_select_datasize, label_length, wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_select_datasize, textctrl_length, wx.CENTER)

        flexgridsizer.Add(self.label_error_datasize, label_length, wx.CENTER|wx.LEFT, 5)
        flexgridsizer.Add(self.textctrl_error_datasize, textctrl_length, wx.CENTER)

        sizer_box.Add(flexgridsizer, 0, wx.EXPAND, 0)

        sizer_ver.Add(sizer_box)
        self.SetSizer(sizer_ver)


class MainFrame(wx.Frame):

    def __init__(self, ser):
        super().__init__(None, title='Demo.exe',size=(900, 600))

        # 初始化串口以及串口参数 
        self._init_setting_serial()

        # 初始化线程
        self.thread = None
        self.alive = threading.Event()
    
        # 初始化数据结构
        self.init_data_struct()
        
        # 初始化动态刷新timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer) 
        self.timer.Start(100) 
        # self.timer.Stop()

        # 初始化菜单页面
        self.mainmenu = wx.MenuBar()
        self._init_serial_menu()
        self._file_menu() 
        self._init_option_menu()
        self.SetMenuBar(self.mainmenu)

        # 初始化页面下角标显示
        self.CreateStatusBar(1)

        #　初始化页面
        self.panel_data_pre = wxplot.PlotCanvas(self, size=(700,300))
        self.panel_data_pro = wxplot.PlotCanvas(self, size=(700,300))
        self.panel_setting = SettingPlanel(self, size=(700,100))
        self.panel_control = ControlPlanel(self, size=(700,50))
        
        # 设置 Point Label 的样式
        self.panel_data_pre.pointLabelFunc = self.DrawPointLabel
        self.panel_data_pro.pointLabelFunc = self.DrawPointLabel

        self.panel_data_pre.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDownPre)
        self.panel_data_pro.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDownPro)
        self.panel_data_pre.canvas.Bind(wx.EVT_MOTION, self.OnMotionPre)
        self.panel_data_pro.canvas.Bind(wx.EVT_MOTION, self.OnMotionPro)
        self.panel_data_pre.canvas.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUpPre)
        self.init_plot()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.panel_control)
        main_sizer.Add(self.panel_data_pre)
        main_sizer.Add(self.panel_setting)
        main_sizer.Add(self.panel_data_pro)
        main_sizer.SetSizeHints(self)
        self.SetSizer(main_sizer)

        self._attach_events()
        self.flush()

    def _init_setting_serial(self):
        self.ser = ser
        self.ser.timeout = 0.5
        self.ser.baudrate = 460800
        self.ser.parity = 'E'
        
    def _init_serial_menu(self):
        serial_menu = wx.Menu()
        serial_menu.Append(wx.ID_ANY, "Setting", "Set the Serial...")
        self.Bind(wx.EVT_MENU, self.SettingSerial)
        self.mainmenu.Append(serial_menu, "&Serial")

    def _file_menu(self):
        """ 创建保存文件菜单 """
        menu = wx.Menu()
        menu.Append(200, 'Save Pre Plot', 'Save current pre plot')
        self.Bind(wx.EVT_MENU, self.OnSavePlotPre, id=200)

        menu.Append(201, 'Save Pro Plot', 'Save current pro plot')
        self.Bind(wx.EVT_MENU, self.OnSavePlotPro, id=201)

        menu.Append(202, 'Save Ori Data', 'Save Origion Data')
        self.Bind(wx.EVT_MENU, self.OnSaveOriData, id=202)

        menu.Append(203, 'Save Mean Data', 'Save Mean Data')
        self.Bind(wx.EVT_MENU, self.OnSaveMeanData, id=203)

        menu.Append(204, 'Save Slide Data', 'Save Slide Data')
        self.Bind(wx.EVT_MENU, self.OnSaveSlideData, id=204)

        self.mainmenu.Append(menu, '&File')

    def _init_option_menu(self):
        menu = wx.Menu()

        menu.Append(212, '&Clear', 'Clear canvas')
        self.Bind(wx.EVT_MENU, self.OnPlotClear, id=212)

        menu.Append(213, 'Dynamic', 'Start Timer', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnEnableTimer, id=213)
        menu.Check(213, True)
        self.timerFlag = True

        menu.Append(215, 'Slide', 'Slide mean data', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnEnableSlide, id=215)
        menu.Check(215, True)
        self.slideFlag = False

        menu.AppendSeparator()

        menu.Append(214, 'Enable &Zoom','Enable Mouse Zoom', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnEnableZoom, id=214)

        menu.Append(217, 'Enable &Drag','Activates dragging mode', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnEnableDrag, id=217)

        menu.Append(2550, 'Enable &Select','Activates Select mode', kind=wx.ITEM_CHECK)
        menu.Check(2550, True)
        self.Bind(wx.EVT_MENU, self.OnEnableSelect, id=2550)

        menu.AppendSeparator()

        # -------------------------------------
        # 测试增加关于 Legend 的子菜单
        # -------------------------------------
        submenu = wx.Menu()
        self.legendSubMenu = submenu
        submenu.AppendCheckItem(2120, "Enable &pre_Legend", "Trun on pre_Legend")
        submenu.AppendCheckItem(2121, "Enable &pro_Legend", "Trun on pro_Legend")
        submenu.Check(2121, False)
        submenu.Check(2120, False)
        self.Bind(wx.EVT_MENU, self.OnEnableLegendPro, id=2121)
        self.Bind(wx.EVT_MENU, self.OnEnableLegendPre, id=2120)

        menu.AppendSubMenu(submenu, 'Enable  Legend',  'Turn on Legend')

        # ----------------------------------------
        # Plot Title  : 与lengend实现结果相同，但代码更容易复制
        # ---------------------------------------
        key_str = 'Plot Title'
        key_id = 2500
        submenu_items = ('pre {}'.format(key_str), 'pro {}'.format(key_str))
        self.plotSubMenu = self._creat_submenu(submenu_items=submenu_items,
                                               id = key_id,
                                               title=key_str)
       
        self.Bind(wx.EVT_MENU, self.OnEnablePlotTitlePre, id=key_id)
        self.Bind(wx.EVT_MENU, self.OnEnablePlotTitlePro, id=key_id+1)
        self.plotSubMenu.Check(key_id, True)
        self.plotSubMenu.Check(key_id+1, True)
        menu.AppendSubMenu(self.plotSubMenu, 'Enable {}'.format(key_str), 
                                             'Turn on {}'.format(key_str))

        #------------------------------------------
        # Point Label
        #------------------------------------------
        key_str = 'Point Label'
        key_id = 2504
        submenu_items = ('pre {}'.format(key_str), 'pro {}'.format(key_str))
        self.pointLabelSubMenu = self._creat_submenu(submenu_items=submenu_items,
                                               id = key_id,
                                               title=key_str)
       
        self.Bind(wx.EVT_MENU, self.OnEnablePointLabelPre, id=key_id)
        self.Bind(wx.EVT_MENU, self.OnEnablePointLabelPro, id=key_id+1)
        self.pointLabelSubMenu.Check(key_id, False)
        self.pointLabelSubMenu.Check(key_id+1, False)
        menu.AppendSubMenu(self.pointLabelSubMenu, 'Enable {}'.format(key_str), 
                                             'Turn on {}'.format(key_str))

        #-------------------------------------------
        # Log-Y 
        #-----------------------------------------
        key_str = 'Log Y'
        key_id = 2502
        submenu_items = ('pre {}'.format(key_str), 'pro {}'.format(key_str))
        self.logYSubmenu = self._creat_submenu(submenu_items=submenu_items,
                                               id = key_id,
                                               title=key_str)
       
        self.Bind(wx.EVT_MENU, self.OnLogYPre, id=key_id)
        self.Bind(wx.EVT_MENU, self.OnLogYPro, id=key_id+1)
        self.logYSubmenu.Check(key_id, False)
        self.logYSubmenu.Check(key_id+1, False)
        menu.AppendSubMenu(self.logYSubmenu, 'Enable {}'.format(key_str), 
                                             'Turn on {}'.format(key_str))


        self.mainmenu.Append(menu, '&Plot Options')

    def _creat_submenu(self, submenu_items, id, title):
        submenu = wx.Menu()
        help_text = "Enables {item} {title}"
        for _i, item in enumerate(submenu_items, id):
            submenu.AppendCheckItem(_i, item, help_text.format(item=item, title=title))
        return submenu
            
    def _attach_events(self):
        """ 事件绑定 """
        self.Bind(EVT_SERIALRX, self.OnSerialRead)
        
        self.Bind(wx.EVT_BUTTON, self.OnStartSerial, id=ID_START)
        self.Bind(wx.EVT_BUTTON, self.OnStopSerial, id=ID_STOP)
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=ID_SAVE) 
        
    def init_data_struct(self):

        self.original_fogdata = []  # 陀螺原始数据（十进制）
        self.fogdata = []  # 陀螺求平均缓冲数据 buffer
        self.pre_mean_data = []  # 陀螺求平均后的数据
        self.pro_slide_data = []  # 陀螺求平滑后的数据

        self.scale_factor = -392677.57 * 3.5   # 标度因数
        self.sample_length = 0  # 陀螺原始采样数据
        self.mean_window_size = 10  # 陀螺均值窗口大小
        self.slide_window_size = 10  # 陀螺平滑窗口值
        self.std = 0 # 取样值的均方差
        self.error_data_size = 0 #错误数据

        self.selectFlag = True # 是否开始选择数据
        self.timerFlag = True  # 是否开始动态更新
        self.slideFlag = False # 是否开启平滑
        self.data_len = 0  # 测试用的数据

    def init_plot(self):
        # 初始化数预处理和处理图像
        # --------------------------------------------
        # 测试画图
        self.select_min = 0
        self.select_max = 0
        self.x = []
        self.y = []
        self.data = np.array([self.x, self.y]).T
        # print(self.data.shape)

        self.markers = wxplot.PolyMarker(self.data,
                                 legend='Pre Data',
                                 colour='blue',
                                 marker='circle',
                                 size=1,
                                 )
                
        self.plotgraphicsPre = wxplot.PlotGraphics([self.markers],
                               "Data preprocessing Plot",
                               "X Axis",
                               "°/h",
                               )
        self.plotgraphicsPro = wxplot.PlotGraphics([],
                               "Data post-processing Plot",
                               "X Axis",
                               "°/h",
                               )
        self.panel_data_pre.Draw(self.plotgraphicsPre)
        # self.panel_data_pro.Draw(self.plotgraphicsPro)
        
    def Draw(self):
        self.data = np.array([self.x, self.y]).T
        self.markers = wxplot.PolyLine(self.data,
                                legend='Pre Data',
                                colour='blue',
                                #  marker='circle',
                                width=1,
                                style=wx.PENSTYLE_DOT_DASH,
                                # drawstyle='steps-post',
                                 )
        self.plotgraphicsPre = wxplot.PlotGraphics([self.markers],
                               "Data preprocessing Plot",
                               "X Axis",
                               "°/h",
                               )
        self.panel_data_pre.Draw(self.plotgraphicsPre)
    
    def StartThread(self):
        self.thread = threading.Thread(target=self.ComPortThread)
        self.thread.setDaemon(1)
        self.thread.start()
        
        self.alive.set()
        
    def StopThread(self):
        if self.thread is not None:
            self.alive.clear()
            self.thread.join()
            self.thread = None

    def ComPortThread(self):
        """ 线程任务处理 """
        while self.alive.isSet():
            # 这里如果电脑连接串口，并且有串口处理函数的话可以使用
            # if not self.ser.isOpen():
            #     self.ser.open()
            # temp_databytes = self.ser.read()
            data, temp, error_info = simulation_serial() # 这里使用随机函数模拟串口读取的进程
            wx.PostEvent(self, SeiralRxEvent(data=data, temp=temp, error_info=error_info))
                
    def flush(self):
        """刷新 标度因数，均值窗口大小，平滑窗口大小"""
        self.panel_setting.textctrl_scale_factor.SetValue(str(self.scale_factor))
        self.panel_setting.textctrl_mean_windowsize.SetValue(str(self.mean_window_size))
        self.panel_setting.textctrl_slide_windowsize.SetValue(str(self.slide_window_size))
     
    def SaveDataFile(self, datas):
        """保存文件"""

        wildcard = "txt files (*.txt)|*.txt" 
        now_time = datetime.now()
        now_time_str = now_time.strftime('%y_%m%d_%I%M')
        defaultfile = '{time}-mean window size_{mean_size}-slide window size_{slide_size}'.format(time=now_time_str,
                                                                                                                mean_size = self.mean_window_size,
                                                                                                                slide_size = self.slide_window_size)
        print(defaultfile)
        with wx.FileDialog( self, message="Save file as ...", 
                                defaultDir='',
                                defaultFile=defaultfile,
                                # defaultDir=wx.StandardPaths.Get().GetDocumentsDir(),  
                                wildcard=wildcard, style=wx.FD_SAVE ) as dlg: 
            if dlg.ShowModal() == wx.ID_OK: 
                path = dlg.GetPath() 
                try:
                    # with open(path, "w") as f: 
                    #     for data in datas:
                    #         f.write(str(data))
                    np.savetxt(path, datas)
                    message = 'File saved successfully'
                    with wx.MessageDialog(None, message=message, caption='Save Successful', style=wx.ICON_INFORMATION) as dlg:
                        dlg.ShowModal()
                except Exception as e: 
                    print(str(e))
                    message = str(e) + 'Save failed'
                    with wx.MessageDialog(None, message=message, caption='Save Failed', style=wx.ICON_ERROR) as dlg:
                        dlg.ShowModal()
            else:
                message = 'No data selected' 
                with wx.MessageDialog(None, message=message, caption='Cannot Save', style=wx.ICON_ERROR) as dlg:
                    dlg.ShowModal()
        
    def DrawPointLabel(self, dc, mDataDict):
        """
        This is the fuction that defines how the pointLabels are plotted

        :param dc: DC that will be passed
        :param mDataDict: Dictionary of data that you want to use
                          for the pointLabel

        As an example I have decided I want a box at the curve point
        with some text information about the curve plotted below.
        Any wxDC method can be used.

        """
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetBrush(wx.Brush(wx.BLACK, wx.BRUSHSTYLE_SOLID))

        sx, sy = mDataDict["scaledXY"]  # scaled x,y of closest point
        # 10by10 square centered on point
        dc.DrawRectangle(sx - 5, sy - 5, 10, 10)
        px, py = mDataDict["pointXY"]
        cNum = mDataDict["curveNum"]
        pntIn = mDataDict["pIndex"]
        legend = mDataDict["legend"]
        # make a string to display
        s = "Crv# %i, '%s', Pt. (%.2f,%.2f), PtInd %i" % (
            cNum, legend, px, py, pntIn)
        dc.DrawText(s, sx, sy + 1)

    # ---------------------------------------------------------------------------------
    # Event Setting 
    # ----------------------------------------------------------------------------------
    
    # 菜单相关事件绑定 ------------------------------------
    # &Flie ---------------------------------------------
    def OnSavePlotPre(self, event):
        self.panel_data_pre.SaveFile()

    def OnSavePlotPro(self, event):
        self.panel_data_pro.SaveFile()
    
    def OnSaveOriData(self, event):
        self.SaveDataFile(self.original_fogdata)
        # self.SaveDataFile()

    def OnSaveMeanData(self, event):
        self.SaveDataFile(self.pre_mean_data)

    def OnSaveSlideData(self, event):
        self.SaveDataFile(self.pro_slide_data)

    # &Serial ------------------------------------------
    def SettingSerial(self, event):
        # 设置 串口， 这时要关闭读取线程
        if event is not None:
            self.StopThread()
            self.ser.close()
        with SerialDialog(self, -1, "", serial=self.ser) as Sdlg:
            Sdlg.CenterOnParent()
            result = Sdlg.ShowModal()
        if result == wx.ID_OK:
            try:
                self.ser.open()
            except serial.SerialException as e:
                with wx.MessageDialog(self, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)as dlg:
                    dlg.ShowModal() 
        print(self.ser)

    # & Plot Option ------------------------------------  
    def OnEnableTimer(self, event):
        self.timerFlag = event.IsChecked()
        if self.timerFlag:
            self.timer.Start(100)
        else:
            self.timer.Stop()
        # pass  

    def OnEnableSlide(self, event):
        self.slideFlag = event.IsChecked()


    def OnMouseLeftUpPre(self, event):
        # self.selectFlag = False
        # 清理pre 中的直方图
        if len(self.plotgraphicsPre.objects) > 1 :
            self.panel_data_pre.Clear()
            self.plotgraphicsPre.objects = []
            self.plotgraphicsPre.objects.append(self.markers)
            self.panel_data_pre.Draw(self.plotgraphicsPre)
    
    def OnMotionPre(self, event):
        # show closest point (when enbled)
        if self.panel_data_pre.enablePointLabel:
            dlst = self.panel_data_pre.GetClosestPoint(
                self.panel_data_pre.GetXY(event),
                pointScaled=True,
            )
            if dlst != []:  # returns [] if none
                curveNum, legend, pIndex, pointXY, scaledXY, distance = dlst
                mDataDict = {"curveNum": curveNum,
                             "legend": legend,
                             "pIndex": pIndex,
                             "pointXY": pointXY,
                             "scaledXY": scaledXY}
                self.panel_data_pre.UpdatePointLabel(mDataDict)
        # 判断左键按下，并且在拖动
        if self.selectFlag:
            if event.Dragging() and event.LeftIsDown(): 
                now = self.panel_data_pre.GetXY(event)[0]
                if now > self.select_min:
                    self.select_max = now
                else: 
                    self.select_min = now
                
                indmin, indmax =  np.searchsorted(self.data[:,0], (self.select_min, self.select_max))
                # region_data = self.data[indmin, indmax]
                region_x = list(self.data[indmin:indmax, 0])
                region_y = list(self.data[indmin:indmax, 1])

                
                self.select_data_size = len(region_y)

                
                self.std = np.std(region_y)

                if len(region_x) > 1:
                    region_x.append(region_x[-1])
                else:
                    region_x.append(0)
                
                # 将pre图中选中的部分作直方图标注
                ploybars = wxplot.PolyHistogram(region_y,
                                            region_x,
                                            legend = 'ploy bars',
                                            edgecolour=wx.Colour((170,255,255)),
                                            fillcolour=wx.Colour((170,255,255)),
                                            edgewidth = 0.2)
                self.plotgraphicsPre.objects.append(ploybars)
                self.panel_data_pre.Draw(self.plotgraphicsPre)
                self.plotgraphicsPre.objects.pop()

                if len(self.plotgraphicsPro.objects) >=  1:
                    self.plotgraphicsPro.objects = []
                
                mean_line = wxplot.PolyLine(self.data[indmin:indmax,:],
                                    legend='Select Data',
                                    colour='blue',
                                    width=1,
                                    style=wx.PENSTYLE_DOT_DASH,
                                    )
                
                self.plotgraphicsPro.objects.append(mean_line)
                
                self.panel_data_pro.Draw(self.plotgraphicsPro)   

                self.panel_setting.textctrl_select_datasize.SetValue(str(self.select_data_size))
                self.panel_setting.textctrl_std.SetValue('%.6f' %self.std)         
        event.Skip()  # go to next handler

    def OnMotionPro(self, event):
        # show closest point (when enbled)
        if self.panel_data_pro.enablePointLabel:
            dlst = self.panel_data_pro.GetClosestPoint(
                self.panel_data_pro.GetXY(event),
                pointScaled=True,
            )
            if dlst != []:  # returns [] if none
                curveNum, legend, pIndex, pointXY, scaledXY, distance = dlst
                # make up dictionary to pass to my user function (see
                # DrawPointLabel)
                mDataDict = {"curveNum": curveNum,
                            "legend": legend,
                            "pIndex": pIndex,
                            "pointXY": pointXY,
                            "scaledXY": scaledXY}
                # pass dict to update the pointLabel
                self.panel_data_pro.UpdatePointLabel(mDataDict)
        event.Skip()  # go to next handle

    def OnMouseLeftDownPre(self, event):
        if self.panel_data_pre.GetXY(event):
            s = "Left Mouse Down at Point: (%.4f, %.4f)" % self.panel_data_pre.GetXY(
                event)
            self.select_min = self.panel_data_pre.GetXY(event)[0]
            self.select_max = self.panel_data_pre.GetXY(event)[0]
        else:
            s = 'Mouse Down shoule  in a plot'
        self.SetStatusText(s)
        # print(self.panel_data_pre.xCurrentRange)
        event.Skip()
    
    def OnMouseLeftDownPro(self, event):
        if self.panel_data_pro.GetXY(event):
            s = "Left Mouse Down at Point: (%.4f, %.4f)" % self.panel_data_pre.GetXY(
                event)
        else:
            s = 'Mouse Down shoule  in a plot'
        self.SetStatusText(s)
        event.Skip()

    def OnPlotClear(self, event):
        self.original_fogdata = []
        self.pre_mean_data = []
        self.pro_slide_data = []
        self.error_data_size = 0
        self.panel_data_pre.Clear()
        self.panel_data_pro.Clear()

    def OnEnableZoom(self, event):
        # pre 图开启该功能会有bug，未解决，故放弃 
        # self.panel_data_pre.enableZoom = event.IsChecked()
        self.panel_data_pro.enableZoom = event.IsChecked()
        if self.mainmenu.IsChecked(217):
            self.mainmenu.Check(217, False)
        if self.mainmenu.IsChecked(2550):
            self.mainmenu.Check(2550, False)
            self.selectFlag = False

    def OnEnableDrag(self, event):
        # 有bug
        # self.panel_data_pre.enableDrag = event.IsChecked()
        self.panel_data_pro.enableDrag = event.IsChecked()
        if self.mainmenu.IsChecked(214):
            self.mainmenu.Check(214, False)
        if self.mainmenu.IsChecked(2550):
            self.mainmenu.Check(2550, False)
            self.selectFlag = False
            
    def OnEnableSelect(self, event):
        self.selectFlag = event.IsChecked()
        if self.mainmenu.IsChecked(217):
            self.mainmenu.Check(217, False)
        if self.mainmenu.IsChecked(214):
            self.mainmenu.Check(214, False)
    
    def OnEnableLegendPre(self, event):
        self.panel_data_pre.enableLegend = event.IsChecked()

    def OnEnableLegendPro(self, event):
        self.panel_data_pro.enableLegend = event.IsChecked()

    def OnEnablePlotTitlePre(self, event):
        self.panel_data_pre.enablePlotTitle = event.IsChecked()

    def OnEnablePlotTitlePro(self, event):
        self.panel_data_pro.enablePlotTitle = event.IsChecked()

    def OnLogYPre(self, event):
        self.panel_data_pre.logScale = (self.panel_data_pre.logScale[0], event.IsChecked())
        self.panel_data_pre.Redraw()
    
    def OnLogYPro(self, event):
        self.panel_data_pro.logScale = (self.panel_data_pro.logScale[0], event.IsChecked())
        self.panel_data_pro.Redraw()

    def OnEnablePointLabelPre(self, event):
        self.panel_data_pre.enablePointLabel = event.IsChecked()

    def OnEnablePointLabelPro(self, event):
        self.panel_data_pro.enablePointLabel = event.IsChecked()

    # Setting 界面事件绑定 -------------------------------
    def OnSave(self, event):
        try:
            self.mean_window_size = int(self.panel_setting.textctrl_mean_windowsize.GetValue())
            self.slide_window_size = int(self.panel_setting.textctrl_slide_windowsize.GetValue())
            self.scale_factor = float(self.panel_setting.textctrl_scale_factor.GetValue())
        except Exception as e:
            self.panel_control.textctrl_log.SetValue(str(e))
        # print(type(self.mean_window_size))
        
        
    # Control 界面事件绑定 -------------------------------
    def OnStartSerial(self, event):
        """start 按键事件绑定"""
        # 为了测试方便，没有判断串口是否开启，如果需要判断，则取消注释
        # if  not self.ser.isOpen():
        #     try:
        #         self.ser.open()
        #     except serial.SerialException as e:
        #         with wx.MessageDialog(self, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)as dlg:
        #             dlg.ShowModal()
        # else:
        #     self.StartThread()
        self.StartThread()
    
    def OnStopSerial(self, event):
        self.StopThread()
        self.ser.close()

    def OnClose(self, event):
        self.ser.close()
        self.StopThread()

    # Timer 事件绑定
    def OnTimer(self, event):
        # self.x.append(self.data_len)
        # self.y.append(random.randint(8,9))
        # self.data_len += 1

        data_length = len(self.pre_mean_data)
        self.x = [i+1 for i in range(data_length) ]
        self.y = self.pre_mean_data

        # 更新采样总数
        self.sample_length = len(self.original_fogdata)
        self.panel_setting.textctrl_sample_size.SetValue(str(self.sample_length))
        self.panel_setting.textctrl_error_datasize.SetValue(str(self.error_data_size))
        self.Draw()

    # 线程任务 事件绑定
    def OnSerialRead(self, event):
        """
        处理串口读回数据
        """
        # print(event.data)
        # print(event.error_info)
        if not event.error_info or event.error_info == 'Test data':
            self.original_fogdata.append(event.data)
            self.fogdata.append(event.data)
            if len(self.fogdata) == self.mean_window_size:
                self.pre_mean_data.append(np.mean(self.fogdata))
                self.fogdata = []
        else:
            self.error_data_size += 1
            self.panel_control.textctrl_log.SetValue(event.error_info)


def simulation_serial():
    """模拟串口返回数据"""
    time.sleep(0.001)
    omega = np.random.randint(1,10)
    temp = np.random.randint(1,10)
    error_info = 'Test data'
    return omega, temp, error_info
     

if __name__ == '__main__':

    ser = serial.Serial()
    app = wx.App()
    frame = MainFrame(ser)
    frame.Show()
    app.SetTopWindow(frame)
    app.MainLoop()

    