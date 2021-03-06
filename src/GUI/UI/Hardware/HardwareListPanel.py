import wx
from src.GUI.UI.DisplayPanel import DisplayPanel
from src.GUI.Util import CONSTANTS
import src.GUI.Util.Globals as Globals


class HardwareListPanel(DisplayPanel):
    """
    Panel for displaying a list of hardware configs
    """

    def __init__(self, parent):
        """
        Sets up the Hardware List Panel
        :param parent: The parent to display the panel on
        """
        DisplayPanel.__init__(self, parent)

        self.list_box = wx.ListBox(self, style=wx.LB_HSCROLL)
        self.list_box.SetFont(wx.Font(wx.FontInfo(12)))
        # Setting up display for the Hardware list panel
        # Display constants can be found in Util.CONSTANTS
        self.list_box.SetBackgroundColour(CONSTANTS.LIST_PANEL_COLOR)
        self.list_box.SetForegroundColour(CONSTANTS.LIST_PANEL_FOREGROUND_COLOR)

        # Adds all the hardware to the display
        for hardware in Globals.systemConfigManager.get_hardware_manager().get_all_hardware_names():
            driver_name = Globals.systemConfigManager.get_hardware_manager().get_hardware_object(hardware).driver
            index_of__ = driver_name.find("_")
            driver_name = driver_name[:index_of__] + " " + driver_name[index_of__+1:]
            self.list_box.Append("{} ({})".format(hardware, driver_name))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL)

        # Runs the deselect and default function when hardware is deselected
        self.Bind(wx.EVT_KEY_DOWN, self.deselected)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.deselected)

        # Renders the selected hardware config
        self.Bind(wx.EVT_LISTBOX, self.selected)

    def reload(self):
        """
        Reloads the list of hardware names
        :return:
        """
        self.list_box.Clear()
        for hardware in Globals.systemConfigManager.get_hardware_manager().get_all_hardware_names():
            self.list_box.Append(hardware)

    def deselected(self, event):
        """
        Deselects the selected hardware config, and tells the parent to render the default config control panel
        :param event: The event that cause the call
        """
        if (not isinstance(event, wx.KeyEvent)) or event.GetKeyCode() == wx.WXK_ESCAPE:
            for selected in self.list_box.GetSelections():
                self.list_box.Deselect(selected)

    def selected(self, event):
        """
        Renders a selected hardware config
        :param event: The event that triggered the call
        """
        # Todo add call to render in parent
        pass
