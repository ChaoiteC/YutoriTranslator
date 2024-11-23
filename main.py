#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
提供主要的GUI界面
'''
import wx
import os
import configparser

class ConfigWindow(wx.Frame):
    def __init__(self, parent, title):
        super(ConfigWindow, self).__init__(parent, title=title, size=(400, 500))
        self.Centre()
        self.SetBackgroundColour((240, 240, 240))
        vbox = wx.BoxSizer(wx.VERTICAL)

        warning_text = wx.StaticText(self, label="相关参数明文储存在config.ini，分享给其他人可能导致私钥被盗。")
        warning_text.SetForegroundColour((255, 0, 0))
        vbox.Add(warning_text, 0, wx.ALL | wx.EXPAND, 5)

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        param_names = ["百度人工智能平台A", "百度人工智能平台S", "百度翻译OCR A", "百度翻译OCR B", "DeppSeek A", "DeppSeek b"]
        self.text_ctrls = []

        for param in param_names:
            hbox = wx.BoxSizer(wx.HORIZONTAL)

            label = wx.StaticText(self, label=param)
            hbox.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

            text_ctrl = wx.TextCtrl(self, value=self.config.get('YUTORI_TRANS_CONFIG', param, fallback=""))
            self.text_ctrls.append(text_ctrl)
            hbox.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 5)

            vbox.Add(hbox, 0, wx.EXPAND)

        save_button = wx.Button(self, label="保存")
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        vbox.Add(save_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        self.SetSizer(vbox)

    def on_save(self, event):
        for i, param in enumerate(["param536", "param2", "param3", "param4", "param5", "param6"]):
            self.config.set('YUTORI_TRANS_CONFIG', param, self.text_ctrls[i].GetValue())

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        wx.MessageBox("配置已保存。", "保存成功", wx.OK | wx.ICON_INFORMATION)

class YutoriTransMainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(YutoriTransMainWindow, self).__init__(parent, title=title,
            size=(800, 600))
        
        self.Centre()
        icon = wx.Icon("yutori.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.BaseUI()

    def BaseUI(self):
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左面板
        left_panel = wx.Panel(panel)
        left_vbox = wx.BoxSizer(wx.VERTICAL)

        # 添加文本框和按钮的容器
        input_container = wx.Panel(left_panel)
        # 修改后的关键代码
        input_container_sizer = wx.BoxSizer(wx.VERTICAL)  # 保持垂直布局

        # 按钮和语言选择框放在同一行
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 改为水平布局
        self.add_file_button = wx.Button(input_container, label="添加文件")
        self.add_folder_button = wx.Button(input_container, label="添加文件夹")
        self.clear_button = wx.Button(input_container, label="清空")
        button_sizer.Add(self.add_file_button, 0, wx.EXPAND | wx.RIGHT, border=5)
        button_sizer.Add(self.add_folder_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        button_sizer.Add(self.clear_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        top_sizer.Add(button_sizer, 0, wx.EXPAND)

        # 源语言和目标语言下拉菜单
        language_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 改为水平布局
        source_language_label = wx.StaticText(input_container, label="源语言:")
        self.source_language_combo = wx.ComboBox(input_container, choices=["English", "Chinese", "Japanese", "Korean"], style=wx.CB_READONLY)
        self.source_language_combo.SetSelection(0)  # 默认选择英语

        target_language_label = wx.StaticText(input_container, label="目标语言:")
        self.target_language_combo = wx.ComboBox(input_container, choices=["English", "Chinese", "Japanese", "Korean"], style=wx.CB_READONLY)
        self.target_language_combo.SetSelection(1)  # 默认选择中文

        language_sizer.Add(source_language_label, 0, wx.EXPAND | wx.LEFT, border=5)
        language_sizer.Add(self.source_language_combo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border=15)
        language_sizer.Add(target_language_label, 0, wx.EXPAND | wx.LEFT, border=5)
        language_sizer.Add(self.target_language_combo, 0, wx.EXPAND | wx.LEFT, border=15)
        top_sizer.Add(language_sizer, 0, wx.EXPAND | wx.EXPAND | wx.LEFT, border=10)

        input_container_sizer.Add(top_sizer, 0, wx.EXPAND)

        # 文本框
        self.text_ctrl = wx.TextCtrl(input_container, style=wx.TE_MULTILINE | wx.TE_READONLY)
        input_container_sizer.Add(self.text_ctrl, 1, wx.EXPAND)
        self.text_ctrl.SetHint("使用上边的按键添加需要翻译的图片，你也可以直接拖放多个文件或文件夹到这里。")

        input_container.SetSizer(input_container_sizer)
        left_vbox.Add(input_container, 1, wx.EXPAND | wx.ALL, border=10)

        # 空box，使文本框占1/2高度
        left_vbox.Add((-1, -1), 1, wx.EXPAND)

        left_panel.SetSizer(left_vbox)
        hbox.Add(left_panel, 3, wx.EXPAND | wx.ALL)

        # 右面板
        right_panel = wx.Panel(panel)
        right_panel_vbox = wx.BoxSizer(wx.VERTICAL)

        config_button = wx.Button(right_panel, label="API 配置")
        right_panel_vbox.Add(config_button, 0, wx.EXPAND | wx.ALL, border=10)
        config_button.Bind(wx.EVT_BUTTON, self.open_config_window)

        right_panel.SetSizer(right_panel_vbox)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL)

        # 设置主面板的布局
        panel.SetSizer(hbox)

        # 绑定按钮事件
        self.add_file_button.Bind(wx.EVT_BUTTON, self.on_add_file)
        self.add_folder_button.Bind(wx.EVT_BUTTON, self.on_add_folder)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_text)

        # 绑定拖放事件
        self.text_ctrl.SetDropTarget(FileDropTarget(self.text_ctrl))

    def open_config_window(self, event):
        config_window = ConfigWindow(None, "API 配置")
        config_window.Show()

    def on_add_file(self, event):
        with wx.FileDialog(self, "选择（多个）文件", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            paths = fileDialog.GetPaths()
            self.append_paths_to_text_ctrl(paths)

    def on_add_folder(self, event):
        with wx.DirDialog(self, "选择文件夹", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = dirDialog.GetPath()
            self.append_paths_to_text_ctrl([path])

    def append_paths_to_text_ctrl(self, paths):
        current_text = self.text_ctrl.GetValue()
        new_text = "\n".join(paths)
        if current_text:
            new_text = current_text + "\n" + new_text
        self.text_ctrl.SetValue(new_text)

    def on_clear_text(self, event):
        self.text_ctrl.SetValue("")  # 清空文本框内容

    def get_source_language(self):
        return self.source_language_combo.GetStringSelection()

    def get_target_language(self):
        return self.target_language_combo.GetStringSelection()

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, text_ctrl):
        wx.FileDropTarget.__init__(self)
        self.text_ctrl = text_ctrl

    def OnDropFiles(self, x, y, filenames):
        current_text = self.text_ctrl.GetValue()
        new_text = "\n".join(filenames)
        if current_text:
            new_text = current_text + "\n" + new_text
        self.text_ctrl.SetValue(new_text)

    
def main():
    app = wx.App()
    yt = YutoriTransMainWindow(None,title="柚鸟翻译 Yutori Translator")
    yt.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()