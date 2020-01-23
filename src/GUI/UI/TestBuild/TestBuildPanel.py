import wx
import json
import inspect
import os

from src.GUI.UI.DisplayPanel import DisplayPanel
from src.GUI.Util import CONSTANTS
import src.GUI.Model.TestBuildModel as build
import src.GUI.Util.Globals as Globals


class TestBuildPanel(DisplayPanel):
    """
    Panel for rendering a test being built and some controls for editing it.
    """
    def __init__(self, parent):
        """
        Sets up the Test Build Panel
        :param parent: The parent to display the panel on
        """
        DisplayPanel.__init__(self, parent)

        # Reduction area
        self.reduce_x_line = wx.BoxSizer(wx.HORIZONTAL)
        self.reduce_checkbox_label = wx.StaticText(self)
        self.reduce_checkbox_label.SetLabelText("Reduce?")
        self.reduce_checkbox = wx.CheckBox(self)
        self.reduce_checkbox.SetValue(False)
        self.csv_checkbox_label = wx.StaticText(self)
        self.csv_checkbox_label.SetLabelText("CSV?")
        self.csv_checkbox = wx.CheckBox(self)
        self.csv_checkbox.SetValue(False)
        self.reduce_x_label_text = wx.StaticText(self)
        self.reduce_x_label_text.SetLabelText("X Label:")
        self.reduce_x_label = wx.TextCtrl(self)
        self.reduce_x_min = wx.TextCtrl(self)
        self.reduce_x_range_text = wx.StaticText(self)
        self.reduce_x_range_text.SetLabelText("< X <")
        self.reduce_x_max = wx.TextCtrl(self)
        self.reduce_x_line.AddMany([(self.reduce_checkbox_label),
                                    (self.reduce_checkbox),
                                    (self.csv_checkbox_label),
                                    (self.csv_checkbox),
                                    (self.reduce_x_label_text),
                                    (self.reduce_x_label, wx.ALL),
                                    (self.reduce_x_min, wx.ALL),
                                    (self.reduce_x_range_text),
                                    (self.reduce_x_max, wx.ALL)])

        self.reduce_y_line = wx.BoxSizer(wx.HORIZONTAL)
        self.reduce_title_label = wx.StaticText(self)
        self.reduce_title_label.SetLabelText("Title:")
        self.reduce_title = wx.TextCtrl(self)
        self.reduce_y_label_text = wx.StaticText(self)
        self.reduce_y_label_text.SetLabelText("Y Label:")
        self.reduce_y_label = wx.TextCtrl(self)
        self.reduce_y_min = wx.TextCtrl(self)
        self.reduce_y_range_text = wx.StaticText(self)
        self.reduce_y_range_text.SetLabelText("< Y <")
        self.reduce_y_max = wx.TextCtrl(self)
        self.reduce_y_line.AddMany([(self.reduce_title_label),
                                    (self.reduce_title, wx.ALL),
                                    (self.reduce_y_label_text),
                                    (self.reduce_y_label, wx.ALL),
                                    (self.reduce_y_min, wx.ALL),
                                    (self.reduce_y_range_text),
                                    (self.reduce_y_max, wx.ALL)])

        # Saving area
        self.save_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(self)
        self.save_button.SetLabelText("Save As")
        self.save_button.Bind(wx.EVT_BUTTON, self.save)
        self.save_field = wx.TextCtrl(self)
        self.save_sizer.Add(self.save_button, wx.EXPAND | wx.ALL)
        self.save_sizer.Add(self.save_field, wx.EXPAND | wx.ALL)

        self.list_box = wx.ListBox(self)

        self.delete_button = wx.Button(self)
        self.delete_button.SetLabelText("Delete")
        self.delete_button.Bind(wx.EVT_BUTTON, self.delete_line)

        self.input_line = wx.BoxSizer(wx.HORIZONTAL)

        # Parameter area
        self.param_line = wx.BoxSizer(wx.HORIZONTAL)
        self.param_text = wx.StaticText(self)
        self.param_text.SetLabelText("Function:  | Parameters: ")
        self.param_line.Add(self.param_text, wx.EXPAND | wx.ALL)

        self.items = []

        # self.param_items = []

        self.lines = []

        self.update_valid = True

        # Putting everything together and setting the ratios
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.reduce_x_line, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.reduce_y_line, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.save_sizer, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.list_box, 15, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.delete_button, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.input_line, 1, wx.EXPAND | wx.ALL)
        self.sizer.Add(self.param_line, 1, wx.EXPAND | wx.ALL)

        # Binding update functions for tying the list and the parameter editing area together
        self.Bind(wx.EVT_LISTBOX, self.load_on_click)

        self.Bind(wx.EVT_TEXT, self.update_text)
        self.Bind(wx.EVT_CHOICE, self.update_on_choice)

        self.SetSizer(self.sizer)

        self.list_box.SetBackgroundColour(CONSTANTS.TEST_BUILD_PANEL_COLOR)
        self.list_box.SetForegroundColour(CONSTANTS.TEST_BUILD_PANEL_FOREGROUND_COLOR)

        self.reload()

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.deselected)

        self.device_functions = {}
        self.fcs = []
        self.fc_args = {}

        # Getting the hardware functions from the hardware manager
        hwm = Globals.systemConfigManager.get_hardware_manager()
        for dev in hwm.get_all_hardware_names():
            drv = hwm.get_hardware_object(dev).driver

            # from src.Instruments.DeviceClass import DeviceClass
            mod = __import__("src.Instruments." + drv, fromlist=[drv])
            klass = getattr(mod, drv)

            methods_of_class = [m for m in inspect.getmembers(klass, inspect.isfunction) if m[0][0] != "_"]
            self.device_functions[dev] = methods_of_class
            for func in methods_of_class:
                if func[0] not in [f[0] for f in self.fcs]:
                    self.fcs.append((func[0], len(inspect.getfullargspec(func[1])[0]) - 1, func[0]))
                    self.fc_args[func[0]] = inspect.getfullargspec(func[1])[0][1:]

        # This sort exists so that the test parser will match longer functions before shorter ones and not break
        self.fcs.sort(key=lambda fn: fn[0], reverse=True)

    def save(self, event):
        """
        Save the current test.
        :param event: The triggering event. This function triggers when the "save" button is pressed.
        """
        # Parse the test into a text file
        ip = build.parse_input([p[0] for p in self.lines])
        test_name = self.save_field.GetLineText(0)
        test_v = test_name.replace(" ", "_")
        ip.insert(0, "Test- " + test_name)
        config, script = build.parse_lines(ip, test_v, self.fcs)
        # If reduction was selected, add the reduction script with the appropriate parameters to the config
        if self.reduce_checkbox.GetValue() or self.csv_checkbox.GetValue():
            config['experiment'].append({
                "type": "PY_SCRIPT",
                "source": "CustomTestReduce.py",
                "order": 2
            })
        if self.reduce_checkbox.GetValue():
            config['data']['Title'] = self.reduce_title.GetLineText(0)
            config['data']['X Label'] = self.reduce_x_label.GetLineText(0)
            config['data']['X Lower'] = float(self.reduce_x_min.GetLineText(0))
            config['data']['X Upper'] = float(self.reduce_x_max.GetLineText(0))
            config['data']['Y Label'] = self.reduce_y_label.GetLineText(0)
            config['data']['Y Lower'] = float(self.reduce_y_min.GetLineText(0))
            config['data']['Y Upper'] = float(self.reduce_y_max.GetLineText(0))
            config['data']['Reduce?'] = True
        if self.csv_checkbox.GetValue():
            config['data']['Csv?'] = True
        else:
            config['data']['Csv?'] = False

        # Save the config file
        with open(os.path.join(CONSTANTS.CONFIGS, test_v + ".json"), "w") as f:
            json.dump(config, f)
        # Save the script file
        with open(os.path.join(CONSTANTS.SCRIPTS_DIR, test_v + ".py"), "w") as f:
            f.write(script)
        if not os.path.exists(CONSTANTS.CUSTOM_TESTS_DIR):
            os.mkdir(CONSTANTS.CUSTOM_TESTS_DIR)
        # Save the test file
        with open(os.path.join(CONSTANTS.CUSTOM_TESTS_DIR, test_v + ".txt"), "w") as f:
            f.writelines([l + "\n" for l in ip])
        # Clear the save field so the user knows the saving was successful
        self.save_field.Clear()
        Globals.systemConfigManager.experiments_manager.cache_is_valid = False
        Globals.systemConfigManager.ui_controller.test_added_to_config_directory()

    def deselected(self, event):
        """
        Deselect a line.
        :param event: The triggering event. This is called on a double-click.
        """
        i = self.list_box.GetSelection()
        if i > -1:
            self.list_box.Deselect(i)
        # Update the parameter display
        self.check_param_display()

    def add_symbol(self, event, pattern):
        """
        Add a new line to the test.
        :param event: The triggering event. This is called, with the pattern parameter through a lambda, by the
        buttons in the TestButtonPanel.
        :param pattern: The pattern of element types.
        """
        output = self.get_load_output(pattern)

        i = self.list_box.GetSelection()
        if i > -1:
            self.list_box.Insert(output, i)
            self.lines.insert(i, [[k.replace("[STR]", "???").replace("[OP]", "-?-") for k in pattern], pattern])
        else:
            self.list_box.Append(output)
            self.lines.append([[k.replace("[STR]", "???").replace("[OP]", "-?-") for k in pattern], pattern])

    def load_on_click(self, event):
        """
        Load a line that's been clicked on.
        :param event: The triggering event. Occurs when the user clicks on a line.
        """
        i = self.list_box.GetSelection()
        output = self.load_symbol(self.lines[i])

    def get_load_output(self, pattern):
        """
        Determine what the starting value of a line should be, when it's added.
        :param pattern: The line pattern.
        :return: A string of how the line should be displayed.
        """
        output = ""
        for i in range(0, len(pattern)):
            symbol = pattern[i]
            if symbol == "[STR]":
                output += "??? "
            elif symbol == "[OP]":
                output += "-?- "
            else:
                output += symbol + " "
        output = output[:-1]
        return output

    def load_params(self, function):
        """
        Display the parameters for a selected function.
        :param function: The function to display parameters for.
        """
        keywords = {"wavelength": "nm", "time_ps": "ps", "time_ns" : "ns", "time": "s", "voltage": "V", "current": "A",
                    "bitrate": "kbps", "path": "string", "amplitude": "Vp-p", "bits": "bits", "optical_power": "dBm"}
        params = self.fc_args.get(function, [])
        # The commented code was part of an abandoned idea to allow inputting parameters in this line rather than
        # in the main parameter line. If this is implemented, the code may come in handy.
        # pvs = param_string.split(' ')
        # self.param_line.Clear(delete_windows=True)
        ptxt = "Function: " + function + " | Parameters: "
        dl = ""
        for i in range(len(params)):
            p = params[i]
            # pv = pvs[i]
            # b = wx.StaticText(self)
            # b.SetLabelText(p)
            # self.param_items.append(b)
            # self.param_line.Add(b, wx.EXPAND | wx.ALL)
            units = ""
            for k in keywords:
                if k in p:
                    units = " (" + keywords[k] + ")"
            ptxt += dl + p + units
            dl = ", "

            # tx = wx.TextCtrl(self)
            # tx.SetLabelText(pv)
            # self.param_items.append(tx)
            # self.param_line.Add(tx, wx.EXPAND | wx.ALL)
        self.param_text.SetLabelText(ptxt)

    def load_symbol(self, patterns):
        """
        Load a selected line into the parameter line.
        :param patterns: A list of two lists. The first is the actual values of each element, and the
        second is the type of each element, so the program knows what object (choice, text box, static text) to use.
        :return: The line in text form.
        """
        # Set a lock so concurrency issues cannot arise
        self.update_valid = False
        items = []
        output = ""
        self.input_line.Clear(delete_windows=True)
        for i in range(0, len(patterns[1])):
            symbol = patterns[1][i]
            if symbol == "[STR]":
                # String
                b = wx.TextCtrl(self)
                b.SetLabelText(patterns[0][i].replace("???", ""))
                items.append(b)
                output += patterns[0][i] + " "
            elif symbol == "[OP]":
                # Operator
                b = wx.Choice(self)
                b.Append(["==", "/=", "<", ">", "<=", ">="])
                si = b.FindString(patterns[0][i])
                if si > -1:
                    b.SetSelection(si)
                items.append(b)
                output += patterns[0][i] + " "
            elif symbol == "[DEV]":
                # Device
                b = wx.Choice(self)
                b.Append(Globals.systemConfigManager.get_hardware_manager().get_all_hardware_names())
                si = b.FindString(patterns[0][i])
                if si > -1:
                    b.SetSelection(si)
                items.append(b)
                output += patterns[0][i] + " "
            elif symbol == "[FNC]":
                # Function
                b = wx.Choice(self)
                k = items[1].GetSelection()
                dev = ""
                if k > -1:
                    dev = items[1].GetString(k)
                for fc in self.device_functions.get(dev, []):
                    b.Append(fc[0])
                si = b.FindString(patterns[0][i])
                if si > -1:
                    b.SetSelection(si)
                items.append(b)
                output += patterns[0][i] + " "
            else:
                # Keyword that can just be printed as text
                b = wx.StaticText(self)
                b.SetLabelText(symbol)
                items.append(b)
                output += symbol + " "
        output = output[:-1]
        self.items = items
        self.load_input_line(items)
        # Release the lock
        self.update_valid = True
        self.update_text(None)
        self.check_param_display()
        return output

    def delete_line(self, event):
        """
        Delete a line.
        :param event: The triggering event. This occurs when the "delete" button is pressed.
        """
        i = self.list_box.GetSelection()
        if i > -1:
            self.update_valid = False
            self.list_box.Deselect(i)
            self.list_box.Delete(i)
            self.lines.pop(i)
            self.load_input_line([])
            self.update_valid = True

    def load_input_line(self, line):
        """
        Load a line of window objects in the parameter area.
        :param line: The objects to load.
        """
        self.input_line.Clear(delete_windows=True)
        for i in line:
            self.input_line.Add(i, wx.EXPAND | wx.ALL)
        self.sizer.Layout()
        self.items = line

    def update_text(self, event):
        """
        Update the text in the test line list corresponding to a parameter change.
        :param event: The triggering event. This occurs whenever the user edits something.
        """
        lind = self.list_box.GetSelection()
        if self.update_valid:
            output = ""
            ind = 0
            if lind > -1 and len(self.lines[lind][0]) == len(self.items):
                for i in range(len(self.items)):
                    s = self.get_text(self.items[i], i)
                    output += s + " "
                    if lind > -1:
                        self.lines[lind][0][ind] = s
                    ind += 1
                if len(output) > 0:
                    output = output[:-1]
                if lind > -1:
                    self.list_box.SetString(lind, output)

    def update_functions(self, event):
        """
        Update the list of functions available from the selected device, if applicable.
        :param event: The triggering event. This occurs when a Choice (drop-down) option is selected.
        """
        ob = event.GetEventObject()
        lind = self.list_box.GetSelection()
        if len(self.items) > 3 and len(self.lines[lind][1]) > 3 and lind > -1 and self.items[1] == ob \
                and self.lines[lind][1][3] == "[FNC]":
            # A device was just selected, and its functions need to be rendered
            i = self.items[1].GetSelection()
            dev = ""
            if i > -1:
                dev = self.items[1].GetString(i)
            self.items[3].Clear()
            for fc in self.device_functions.get(dev, []):
                self.items[3].Append(fc[0])
        if len(self.items) > 3 and len(self.lines[lind][1]) > 3 and lind > -1 and self.items[3] == ob \
                and self.lines[lind][1][3] == "[FNC]":
            self.check_param_display()

    def check_param_display(self):
        """
        Update the parameter display if a function was selected.
        """
        lind = self.list_box.GetSelection()
        if len(self.items) > 3 and len(self.lines[lind][1]) > 3 and lind > -1 and self.lines[lind][1][3] == "[FNC]":
            i = self.items[3].GetSelection()
            fnc = ""
            if i > -1:
                fnc = self.items[3].GetString(i)
            self.load_params(fnc)
        else:
            self.load_params("")

    def update_on_choice(self, event):
        """
        Update functions and text when a choice is selected.
        :param event: The triggering event. This occurs when a Choice (drop-down) option is selected.
        """
        self.update_functions(event)
        self.update_text(event)

    def get_text(self, item, index):
        """
        Get the text of a display object.
        :param item: The object.
        :param index: The object's index.
        :return: The text version of what the object contains.
        """
        s = ""
        if type(item) == wx.TextCtrl:
            s = item.GetLineText(0)
            if s == "":
                s = "???"
        elif type(item) == wx.Choice:
            i = item.GetSelection()
            if i == -1:
                if item.GetCount() > 0 and item.GetString(0) == "==":
                    s = "-?-"
                elif index == 1:
                    s = "[DEV]"
                else:
                    s = "[FNC]"
            else:
                s = item.GetString(i)
        elif type(item) == wx.StaticText:
            s = item.GetLabel()
        return s
