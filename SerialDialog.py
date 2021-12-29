import wx
import serial
import serial.tools.list_ports

BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
                 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
                 3000000, 3500000, 4000000)

                 
class SerialDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        
        self.serial = kwds['serial']
        del kwds['serial']
        wx.Dialog.__init__(self, *args, **kwds)
        self.max_size = 300
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.panel_base = wx.Panel(self, -1)
        self.label_port = wx.StaticText(self.panel_base, -1, 'Port')
        self.choice_port = wx.Choice(self.panel_base, -1, choices=[])
        self.label_baudrate = wx.StaticText(self.panel_base, -1, 'Baudrate')
        self.combo_box_baudrate = wx.ComboBox(self.panel_base, -1, choices=[], style=wx.CB_DROPDOWN)
        self.staticbox_basics = wx.StaticBox(self.panel_base, -1, 'Basics')

        self.panel_format = wx.Panel(self, -1)
        self.label_data_bits = wx.StaticText(self.panel_format, -1, 'Data Bits')
        self.choice_data_bits = wx.Choice(self.panel_format, -1, choices=[])
        self.label_stop_bits = wx.StaticText(self.panel_format, -1, 'Stop Bits')
        self.choice_stop_bits = wx.Choice(self.panel_format, -1, choices=[])
        self.label_parity = wx.StaticText(self.panel_format, -1, 'Parity')
        self.choice_parity = wx.Choice(self.panel_format, -1, choices=[])
        self.staticbox_format = wx.StaticBox(self.panel_format, -1, 'Data Format')

        self.panel_timeout = wx.Panel(self, -1)
        self.checkbox_timeout = wx.CheckBox(self.panel_timeout, -1, 'Use Timeout')
        self.textctrl_timeout = wx.TextCtrl(self.panel_timeout, -1, "")
        self.label_seconds = wx.StaticText(self.panel_timeout, -1, 'seconds')
        self.staticbox_timeout = wx.StaticBox(self.panel_timeout, -1, 'Timeout')

        self.panel_flow = wx.Panel(self, -1)
        self.checkbox_rtxctx = wx.CheckBox(self.panel_flow, -1, "RTS/CTS")
        self.checkbox_xonxoff = wx.CheckBox(self.panel_flow, -1, "Xon/Xoff")
        self.staticbox_flow = wx.StaticBox(self.panel_flow, -1, "Flow control")

        self.button_ok = wx.Button(self, wx.ID_OK, "")
        self.button_off = wx.Button(self, wx.ID_CANCEL, "")

        self._set_properties()
        self._layout()
        self._attach_events()

    def _set_properties(self):
        
        self.SetTitle("Serial Port Configuration")
        self.choice_data_bits.SetSelection(0)
        self.choice_stop_bits.SetSelection(0)
        self.choice_parity.SetSelection(0)
        self.textctrl_timeout.Enable(False)
        self.button_ok.SetDefault()

        # 设置串口
        preferred_index = 0
        self.choice_port.Clear()
        self.ports = []
        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            self.choice_port.Append(u'{} - {}'.format(portname, desc))
            self.ports.append(portname)
            if self.serial.port == portname:
                preferred_index = n
        self.choice_port.SetSelection(preferred_index)
        # 设置波特率
        preferred_index = None
        self.combo_box_baudrate.Clear()
        # print(self.serial.BAUDRATES)
        for n, baudrate in enumerate(BAUDRATES):
            self.combo_box_baudrate.Append(str(baudrate))
            if self.serial.baudrate == baudrate:
                preferred_index = n
        if preferred_index is not None:
            self.combo_box_baudrate.SetSelection(preferred_index)
        else:
            self.combo_box_baudrate.SetValue(u'{}'.format(self.serial.baudrate))
        # 设置databits
        self.choice_data_bits.Clear()
        for n, bytesize in enumerate(self.serial.BYTESIZES):
            self.choice_data_bits.Append(str(bytesize))
            if self.serial.bytesize == bytesize:
                index = n
        self.choice_data_bits.SetSelection(index)
        # 设置stopbits
        self.choice_stop_bits.Clear()
        for n, stopbits in enumerate(self.serial.STOPBITS):
            self.choice_stop_bits.Append(str(stopbits))
            if self.serial.stopbits == stopbits:
                index = n
        self.choice_stop_bits.SetSelection(index)
        # 设置parities 
        self.choice_parity.Clear()
        for n, parity in enumerate(self.serial.PARITIES):
            self.choice_parity.Append(str(serial.PARITY_NAMES[parity]))
            if self.serial.parity == parity:
                index = n
        self.choice_parity.SetSelection(index)
        # 设置 timeout
        if self.serial.timeout is None:
            self.checkbox_timeout.SetValue(False)
            self.textctrl_timeout.Enable(False)
        else:
            self.checkbox_timeout.SetValue(True)
            self.textctrl_timeout.Enable(True)
            self.textctrl_timeout.SetValue(str(self.serial.timeout))
        # 设置 rtscts
        self.checkbox_rtxctx.SetValue(self.serial.rtscts)
        self.checkbox_xonxoff.SetValue(self.serial.xonxoff)

    def _layout(self):
        
        sizer_ver = wx.BoxSizer(wx.VERTICAL)
        sizer_hor = wx.BoxSizer(wx.HORIZONTAL)

        self.staticbox_basics.Lower()
        sizer_base = wx.StaticBoxSizer(self.staticbox_basics, wx.HORIZONTAL)

        self.staticbox_flow.Lower()
        sizer_flow = wx.StaticBoxSizer(self.staticbox_flow, wx.HORIZONTAL)

        self.staticbox_timeout.Lower()
        sizer_timeout = wx.StaticBoxSizer(self.staticbox_timeout, wx.HORIZONTAL)

        self.staticbox_format.Lower()
        sizer_format = wx.StaticBoxSizer(self.staticbox_format, wx.VERTICAL)

        
        sizer_flexgrid_1 = wx.FlexGridSizer(3, 2, 0, 0)
        sizer_flexgrid_1.Add(self.label_port, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flexgrid_1.Add(self.choice_port, 0, wx.EXPAND, 0)
        sizer_flexgrid_1.Add(self.label_baudrate, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flexgrid_1.Add(self.combo_box_baudrate, 0, wx.EXPAND, 0)
        sizer_flexgrid_1.AddGrowableCol(1)
        sizer_base.Add(sizer_flexgrid_1, 0, wx.EXPAND, 0)
        self.panel_base.SetSizer(sizer_base)
        sizer_ver.Add(self.panel_base, 0, wx.EXPAND, 0)

        sizer_flexgrid_2 = wx.FlexGridSizer(3, 2, 0, 0)
        sizer_flexgrid_2.Add(self.label_data_bits, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flexgrid_2.Add(self.choice_data_bits, 1, wx.EXPAND|wx.ALIGN_RIGHT, 0)
        sizer_flexgrid_2.Add(self.label_stop_bits, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flexgrid_2.Add(self.choice_stop_bits, 1, wx.EXPAND|wx.ALIGN_RIGHT, 0)
        sizer_flexgrid_2.Add(self.label_parity, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flexgrid_2.Add(self.choice_parity, 1, wx.EXPAND|wx.ALIGN_RIGHT, 0)
        sizer_format.Add(sizer_flexgrid_2)
        self.panel_format.SetSizer(sizer_format)
        sizer_ver.Add(self.panel_format, 0, wx.EXPAND, 0)

        sizer_timeout.Add(self.checkbox_timeout, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_timeout.Add(self.textctrl_timeout, 0, 0, 0)
        sizer_timeout.Add(self.label_seconds, 0, wx.ALL|wx.ALIGN_CENTRE_VERTICAL, 4)
        self.panel_timeout.SetSizer(sizer_timeout)
        sizer_ver.Add(self.panel_timeout, 0, wx.EXPAND, 0)

        sizer_flow.Add(self.checkbox_rtxctx, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flow.Add(self.checkbox_xonxoff, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_flow.Add((10, 10), 1, wx.EXPAND, 0)
        self.panel_flow.SetSizer(sizer_flow)
        sizer_ver.Add(self.panel_flow, 0, wx.EXPAND, 0)

        sizer_hor.Add(self.button_ok, 0, 0, 0)
        sizer_hor.Add(self.button_off, 0, 0, 0)
        sizer_ver.Add(sizer_hor, 0, wx.ALL|wx.ALIGN_RIGHT, 4)

        self.SetSizer(sizer_ver)
        sizer_ver.Fit(self)
        self.Layout()


    def _attach_events(self):
        self.button_ok.Bind(wx.EVT_BUTTON, self.OnOK)
        self.button_off.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.checkbox_timeout.Bind(wx.EVT_CHECKBOX, self.OnTimeout)

    def OnOK(self, events):
        success = True
        try:
            self.serial.port = self.ports[self.choice_port.GetSelection()]
        except IndexError:
            with wx.MessageDialog(
                    self,
                    'No Ports found',
                    'Value Error',
                    wx.OK | wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            success = False

        try:
            b = int(self.combo_box_baudrate.GetValue())
        except ValueError:
            with wx.MessageDialog(
                    self,
                    'Baudrate must be a numeric value',
                    'Value Error',
                    wx.OK | wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            success = False
        else:
            self.serial.baudrate = b

        
        self.serial.bytesize = self.serial.BYTESIZES[self.choice_data_bits.GetSelection()]
        self.serial.stopbits = self.serial.STOPBITS[self.choice_stop_bits.GetSelection()]
        self.serial.parity = self.serial.PARITIES[self.choice_parity.GetSelection()]
        
        self.serial.rtscts = self.checkbox_rtxctx.GetValue()
        self.serial.xonxoff = self.checkbox_xonxoff.GetValue()
    
        if self.checkbox_timeout.GetValue():
            try:
                self.serial.timeout = float(self.textctrl_timeout.GetValue())
            except ValueError:
                with wx.MessageDialog(
                        self,
                        'Timeout must be a numeric value',
                        'Value Error',
                        wx.OK | wx.ICON_ERROR) as dlg:
                    dlg.ShowModal()
                success = False
        else:
            self.serial.timeout = None

        if success:
            self.EndModal(wx.ID_OK)

    def OnCancel(self, events):
        self.EndModal(wx.ID_CANCEL)

    def OnTimeout(self, events):
        if self.checkbox_timeout.GetValue():
            self.textctrl_timeout.Enable(True)
        else:
            self.textctrl_timeout.Enable(False)


# class SerialFrame(wx.Frame): 
#     def __init__(self): 
#         super().__init__(None, title='Serial demo', size=(1200, 800))
#         panel = SerialPanel(self)
#         self.Show()

class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        ser = serial.Serial()
        print(ser)
        while True:
            dialog_serial_cfg = SerialDialog(None, -1, "", serial=ser)
            self.SetTopWindow(dialog_serial_cfg)
            result = dialog_serial_cfg.ShowModal()
            print(ser)
            if result != wx.ID_OK:
                break
        return 0


if __name__ == '__main__': 
    # app = wx.App(False) 
    # frame = SerialFrame()
    # app.MainLoop()
    app = MyApp(0)
    app.MainLoop()




