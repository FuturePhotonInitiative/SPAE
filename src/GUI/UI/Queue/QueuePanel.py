import wx
import os

from src.GUI.UI.DisplayPanel import DisplayPanel
from src.GUI.Util.CONSTANTS import LIST_PANEL_COLOR, LIST_PANEL_FOREGROUND_COLOR, SAVED_EXPERIMENTS_DIR, CONFIGS
import src.GUI.Util.Globals as Globals


class QueuePanel(DisplayPanel):
    """
    Panel for rendering a queue of experiments
    """
    def __init__(self, parent):
        """
        Sets up the Queue Panel
        :param parent: The parent to display the panel on
        """
        DisplayPanel.__init__(self, parent)

        self.list_box = wx.ListBox(self)
        # self.list_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.list_box_sizer.Add(self.list_box, 5)
        self.run_button = wx.Button(self)
        self.run_button.SetLabelText("Run Queue")
        # self.run_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.sizer.Add(self.list_box_sizer, 5)

        self.clear_button = wx.Button(self)
        self.clear_button.SetLabelText("Clear Queue")

        self.save_button = wx.Button(self)
        self.save_button.SetLabelText("Save Queue")

        self.load_button = wx.Button(self)
        self.load_button.SetLabelText("Load Queue")

        self.save_exp = wx.TextCtrl(self)

        self.load_exp = wx.Choice(self, choices=self.get_loadable_experiments())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.sizer.Add(self.list_box, 5, wx.EXPAND | wx.ALL)

        self.midbar = wx.BoxSizer(wx.HORIZONTAL)
        self.midbar.Add(self.clear_button, 1, wx.EXPAND | wx.ALL)

        self.btn_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer.Add(self.save_button, 1, wx.EXPAND | wx.ALL)
        self.btn_sizer.Add(self.load_button, 1, wx.EXPAND | wx.ALL)

        self.input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_sizer.Add(self.save_exp, 1, wx.EXPAND | wx.ALL)
        self.input_sizer.Add(self.load_exp, 1, wx.EXPAND | wx.ALL)

        self.midbar.Add(self.btn_sizer, 0.5, wx.EXPAND | wx.ALL)
        self.midbar.Add(self.input_sizer, 0.5, wx.EXPAND | wx.ALL)

        self.sizer.Add(self.midbar, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.run_button, 2, wx.EXPAND | wx.ALL)

        # Sets up the colors display Constants are in Util.CONSTANTS
        self.list_box.SetBackgroundColour(LIST_PANEL_COLOR)
        self.list_box.SetForegroundColour(LIST_PANEL_FOREGROUND_COLOR)

        # Adds all the experiments in the application queue to the display list
        self.reload()

        # Runs deselected on a double click or when escape is pressed
        self.Bind(wx.EVT_KEY_DOWN, self.deselected)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.deselected)

        # Runs the selected function when an experiment is selected
        self.Bind(wx.EVT_LISTBOX, self.selected)

        # Runs the queue when the run button is pressed
        self.Bind(wx.EVT_BUTTON, self.run_the_queue)
        self.save_button.Bind(wx.EVT_BUTTON, self.save_queue)
        self.load_button.Bind(wx.EVT_BUTTON, self.load_queue)
        self.clear_button.Bind(wx.EVT_BUTTON, self.clear_queue)

    def set_up_ui_control(self, ui_control):
        ui_control.add_control_to_text_list(self.run_button)

    def reload(self):
        """
        Reloads the display list with the current Queue contents
        """
        self.list_box.Clear()
        for experiment in Globals.systemConfigManager.get_queue_manager().get_experiment_names():
            self.list_box.Append(experiment)

    def deselected(self, event):
        """
        Deselects the selected experiment, and tells the parent to render the default control panel
        :param event: The event that cause the call
        """
        self.GetParent().render_control_panel(None)
        if (not isinstance(event, wx.KeyEvent)) or event.GetKeyCode() == wx.WXK_ESCAPE:
            for selected in self.list_box.GetSelections():
                self.list_box.Deselect(selected)

    def selected(self, event):

        """
        Tells the parent to render the control panel with the selected experiment
        :param event: The event that caused the call
        """

        queue_manager = Globals.systemConfigManager.get_queue_manager()
        selected_experiment = queue_manager.get_ith_experiment(self.list_box.GetSelection())
        self.GetParent().render_control_panel(selected_experiment)
        pass

    @staticmethod
    def run_the_queue(event):
        """
        Runs the queue.
        :param event: The triggering event.
        """
        ui_control = Globals.systemConfigManager.get_ui_controller()
        if ui_control is not None:
            ui_control.switch_queue_to_running()
        Globals.systemConfigManager.get_queue_manager().run()

    def clear_queue(self, event):
        """
        Clears the queue.
        :param event: The triggering event.
        """
        self.deselected(event)
        Globals.systemConfigManager.get_queue_manager().clear_queue()

    def save_queue(self, event):
        """
        Saves the queue.
        :param event: The triggering event.
        """
        st = self.save_exp.GetValue().replace(" ", "_")
        while os.path.isfile(os.path.join(SAVED_EXPERIMENTS_DIR, "Saved_Experiment_" + st)):
            st += "-"
        Globals.systemConfigManager.get_queue_manager().save_queue_to_file(SAVED_EXPERIMENTS_DIR, st)
        print(("Queue saved: " + st))
        self.load_exp.Append(st.replace("_", " "))

    def load_queue(self, event):
        """
        Loads the queue in the load box.
        :param event: The triggering event.
        """
        nm = self.load_exp.GetString(self.load_exp.GetSelection()).replace(" ", "_")
        mgr = Globals.systemConfigManager.get_queue_manager()
        mgr.clear_queue()
        mgr.read_queue_from_file(os.path.join(SAVED_EXPERIMENTS_DIR, "Saved_Experiment_" + nm), CONFIGS)

    @staticmethod
    def get_loadable_experiments():
        """
        Gets possible experiments to load.
        :return: A list of loadable experiments.
        """
        res = []
        try:
            for fl in os.listdir(SAVED_EXPERIMENTS_DIR):
                res.append(fl[17:].replace("_", " "))
        except WindowsError as e:
            if e.errno == 2:
                os.mkdir(SAVED_EXPERIMENTS_DIR)
            else:
                raise e
        return res
