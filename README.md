# wxpython
利用 wxpython 实现读取实时读取串口数据
效果如下：
![动画](https://typora-guohongjie.oss-cn-beijing.aliyuncs.com/img/动画.gif)

代码有两个文件: `main.py` 为主界面，`SerialDialog.py`为串口设置界面。串口设置界面根据 [pyserial 官网案例](https://github.com/pyserial/pyserial/tree/master/examples)修改而成，如果对界面布局满意，可以直接引用。

`main.py`文件按照Panel→Frame→App的思路写的，如下图所示。分为四个Panel，由于画布Panel继承`wxplot.PlotCanvas`会出现部分功能丢失的情况，故没有单独封装为类，伪代码为

![image-20211229224412223](https://typora-guohongjie.oss-cn-beijing.aliyuncs.com/img/image-20211229224412223.png)

```python
class ControlPlanel(wx.Panel):
    """对应 Panel 1 → 控制界面"""
    
class SettingPlanel(wx.Panel):
    """对应 Panel 3 → 设置界面"""
    
class MainFrame(wx.Frame):
    def __init__(self):
        self.panel_data_pre = wxplot.PlotCanvas(self, size=(700,300)) #注册 Panel 2
        self.panel_data_pro = wxplot.PlotCanvas(self, size=(700,300)) # 注册 Panel 4
        self.panel_setting = SettingPlanel(self, size=(700,100)) # 注册 Panel 1 
        self.panel_control = ControlPlanel(self, size=(700,50))  # 注册 Panel 3
```


关于代码中其他细节

1. 画布为Pre和Pro两个Panel，故在事件绑定的时候分开定义事件函数，比如`OnMotionPre` 和`OnMotionPro`表示Pre的鼠标移动事件函数和Pro的鼠标移动事件函数。

2. 有些变量名字较长，但遵循规律：**组件属性-名字** , 比如 `self.panel_setting.textctrl_sample_size.SetValue(test)`表示将Setting Panel 也就是Panel3 中的Textctrl组件设置为'test',其中Textctrl组件的名字是`textctrl_sample_size`

   ![image-20211229231120035](https://typora-guohongjie.oss-cn-beijing.aliyuncs.com/img/image-20211229231120035.png)

3. 因为不确定代码可以在不同的电脑中跑起来，故将串口读取数据的部分注释，用随机函数模拟串口读取数据，如果需要使用，需要取消注释

   
