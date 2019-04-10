from src.GUI.Util.Functions import fix_text_size


class UIController:
    def __init__(self, mainframe):
        assert (mainframe is not None)
        self.mainframe = mainframe
        self.controls_to_fix_text_size = []
        self.mainframe.queue_page.set_up_ui_control(self)
        self.mainframe.hardware_page.set_up_ui_control(self)
        self.mainframe.build_experiments_page.set_up_ui_control(self)
        self.mainframe.experiment_results_page.set_up_ui_control(self)

    def rebuild_all_pages(self):
        self.rebuild_queue_page()
        self.rebuild_experiment_results_page()

    def rebuild_queue_page(self):
        self.mainframe.queue_page.reload_display_panel()

    def rebuild_experiment_results_page(self):
        self.mainframe.experiment_results_page.reload_display_panel()

    def add_control_to_text_list(self, control):
        if control is not None:
            self.controls_to_fix_text_size.append(control)
            self.fix_control_list()

    def remove_control_from_text_list(self, control):
        if control is not None and control in self.controls_to_fix_text_size:
            self.controls_to_fix_text_size.remove(control)

    def fix_control_list(self):
        for control in self.controls_to_fix_text_size:
            fix_text_size(control, 10)

    def switch_to_result(self):
        # self.mainframe.notebook
        pass
