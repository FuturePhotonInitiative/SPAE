import os
from shutil import copyfile
from threading import Thread
import contextlib2

from src.GUI import RunAConfigFileMain
from src.GUI.Util import Globals
from src.GUI.Util.Functions import clean_name_for_file
from src.GUI.Util.Timestamp import Timestamp
from src.GUI.RunAConfigFile.DeviceSetup import DeviceSetup

from src.GUI.Model.ExperimentModel import Experiment
from src.GUI.Model.ExperimentScriptModel import ExperimentScript

from src.GUI.Util.CONSTANTS import TEMP_DIR
from src.GUI.Util.CONSTANTS import SCRIPTS_DIR
from src.GUI.Util.CONSTANTS import PROJ_DIR
from src.GUI.Util.CONSTANTS import VIVADO_LOCATION


class QueueRunner(Thread):
    """
    Thread class to run a provided queue
    """

    def __init__(self, queue, queue_result):
        """
        Create a new QueueRunner that will run the provided queue using the provided temporary directory
        :param queue:
            The queue to run with Prober
        """
        Thread.__init__(self)
        self.queue = queue
        self.queue_result = queue_result
        # Initialize the status of all of the experiments in the queue to "not yet run"
        self.experiment_status = {}
        for i in range(len(queue)):
            self.experiment_status[queue.get_ith_experiment(i)] = -1
        self.current_experiment = None

    def run(self):
        """
        Run the provided queue
        :return:
            Nothing
        """
        print("Verifying devices...")
        if not self.verify_devices():
            print("\nA device was not connected properly. Aborting experiment.\n")
            return
        print("\n====================\nStarting the Queue\n====================\n")
        self.queue_result.start_queue()
        # TODO catch any exceptions run by prober and try to continue, but only if a flag in the __init__ has been
        # set
        self.queue.schedule_experiments()
        i = 0
        while i < len(self.queue):
            if self.queue.get_ith_experiment(i).config.data is not None:
                rt = self.queue.get_ith_experiment(i).config.data.get('Results', None)
                if rt is not None:
                    if rt != "":
                        Globals.systemConfigManager.get_results_manager().results_directory = rt
            if self.queue.get_ith_experiment(i).get_name() == 'Repeat Experiment':
                if i > 0:
                    ex = self.queue.get_ith_experiment(i)
                    vary_param = ex.config.data['Parameter']
                    start = float(ex.config.data['Start'])
                    if float(int(start)) == start:
                        start = int(start)
                    count = int(ex.config.data['Count'])
                    step = float(ex.config.data['Step'])
                    if float(int(step)) == step:
                        step = int(step)
                    base_exp = self.queue.get_ith_experiment(i - 1)
                    rq = self.add_test_series(base_exp, vary_param, start, count, step)
                    tq = self.queue.queue[:i-1]
                    tq.extend(rq)
                    tq.extend(self.queue.queue[i+1:])
                    self.queue.queue = tq
                else:
                    self.queue.queue = self.queue.queue[1:]
                i -= 1
            else:
                i += 1
        i = 0
        while i < len(self.queue):
            self.current_experiment = self.queue.get_ith_experiment(i)
            print((self.current_experiment.get_name()))
            if self.current_experiment.get_name()[-5:] == '(Tcl)':
                # Run a contiguous sequence of Tcl tests
                tcl_end = i + 1
                while tcl_end < len(self.queue) and self.queue.get_ith_experiment(tcl_end).get_name()[-5:] == '(Tcl)':
                    tcl_end += 1
                self.run_tcl_tests(tcl_end, i)
                i = tcl_end
            else:
                self.experiment_status[self.current_experiment] = 0
                # The file to store the json to call prober on to run the experiment

                tmp_file_name = os.path.join(TEMP_DIR, "tmp" + self.current_experiment.get_name().replace(" ", "_") + ".json")
                self.current_experiment.export_to_json(tmp_file_name)
                try:
                    RunAConfigFileMain.main(
                        ["RunAConfigFileMain.py", "-c", tmp_file_name],
                        config_manager=Globals.systemConfigManager,
                        queue_result=self.queue_result
                    )
                finally:
                    os.remove(tmp_file_name)
                self.experiment_status[self.current_experiment] = 1
                i += 1
        self.current_experiment = None
        self.queue_result.end_queue()
        self.queue_result.save()
        print("\n====================\nQueue has finished\n====================\n")

    def run_tcl_tests(self, tcl_end, start_index=0):
        """
                Run a series of TCL tests
                :param tcl_end:
                    The ending index
                :param start_index:
                    The starting index
                :return:
                    Nothing
                """
        # Create the main results directory for this test series
        self.queue.schedule_experiments()
        now = Timestamp()
        name = "Tcl_Experiment" + now.for_filename()
        self.queue_result.time = now
        result_dir = Globals.systemConfigManager.get_results_manager().results_directory
        master_tcl = ""
        output_folder = os.path.join(result_dir, name).replace("\\", "/")
        os.mkdir(output_folder)
        for i in range(start_index, tcl_end):
            with open(PROJ_DIR + "/" + self.queue.get_ith_experiment(i).config.tcl, "r") as f:
                # Edit the Tcl scripts with the test parameters
                done_sets = False
                ex_name = clean_name_for_file(self.queue.get_ith_experiment(i).get_name())
                # Create a subdirectory for results from this specific test
                os.mkdir(output_folder + "/" + ex_name + "_" + str(i+1))
                master_tcl += "set output \"" + output_folder + "/" + ex_name + "_" + str(i+1) + \
                              "/Collected_Data.csv\"\n"
                master_tcl += "set index " + str(i+1) + "\n"
                for line in f.readlines():
                    if not done_sets:
                        if not line.startswith("#"):
                            if not line.startswith("set"):
                                done_sets = True
                            else:
                                words = line.split(' ')
                                val = words[1]
                                for k in list(self.queue.get_ith_experiment(i).config.data.keys()):
                                    if k == val:
                                        dt = self.queue.get_ith_experiment(i).config.data[k]
                                        if isinstance(dt, str) or isinstance(dt, str):
                                            dt = "\"" + dt + "\""
                                        line = words[0]+" "+words[1]+" " + str(dt) + "\n"
                    master_tcl += line
        target_location = os.path.join(output_folder, "combined.tcl")
        # Save the combined Tcl script to be run
        with open(target_location, "w") as f:
            f.writelines(master_tcl)

        # Read in necessary devices and scripts
        master_experiment = Experiment(PROJ_DIR + "/template.json")
        for i in range(start_index, tcl_end):
            if self.queue.get_ith_experiment(i).config.devices is not None:
                for key in self.queue.get_ith_experiment(i).config.devices:
                    if key not in master_experiment.config.devices:
                        master_experiment.config.devices.append(key)
            if self.queue.get_ith_experiment(i).config.experiment is not None:
                for key in self.queue.get_ith_experiment(i).config.experiment:
                    if key not in master_experiment.config.experiment:
                        master_experiment.config.experiment.append(key)
        # Generate the script to run the Tcl script through the Vivado command line
        tmp_file_name = TEMP_DIR + "\\tmp\\" + master_experiment.get_name().replace(" ", "_") + ".json"
        pyLoc = os.path.join(SCRIPTS_DIR, "script" + str(name) + ".py")
        exp = dict()
        exp['type'] = 'PY_SCRIPT'
        exp['source'] = 'script' + str(name) + '.py'
        exp['order'] = 1
        with open(pyLoc, "w") as f:
            f.write("import os\ndef main(data_map, experiment_result):\n\t" +
                    "os.system('" + VIVADO_LOCATION + " -mode tcl < ' + '\""
                    + target_location + "\"')")
        copyfile(pyLoc, output_folder + "/script.py")
        master_experiment.config.experiment.append(ExperimentScript(exp))
        master_experiment.export_to_json(tmp_file_name)
        # Run the experiment
        RunAConfigFileMain.main(["RunAConfigFileMain.py", "-c", tmp_file_name], config_manager=Globals.systemConfigManager,
                            queue_result=self.queue_result)
        for i in range(start_index, tcl_end):
            ex_name = clean_name_for_file(self.queue.get_ith_experiment(i).get_name())
            if len(os.listdir(result_dir + "/" + name + "/" + ex_name + "_" + str(i+1))) == 0:
                os.rmdir(result_dir + "/" + name + "/" + ex_name + "_" + str(i+1))
        # Get rid of the annoying files Vivado creates
        for fl in os.listdir("."):
            try:
                if fl.endswith(".jou") or fl.endswith(".log"):
                    os.remove(fl)
            except WindowsError:
                pass

        os.remove(pyLoc)

    def get_current_experiment(self):
        """
        :return:
            The experiment this class is currently running, or None if the thread has not yet been started or
            has finished
        """
        return self.current_experiment

    def get_run_status(self, experiment):
        """
        :param experiment:
            The experiment object to get the run status of
        :return:
            The current run status of the provided experiment in the currently running queue
        """
        return self.experiment_status[experiment]

    def verify_devices(self):
        """
        Verify that all the devices in the tests are connected.
        :return: If all the selected devices are connected.
        """
        device_list = []
        for test in self.queue.queue:
            d = test.config.devices
            if d is not None:
                for dev in d:
                    if dev not in device_list:
                        device_list.append(dev)
        with contextlib2.ExitStack() as stack:
            device_setup = DeviceSetup()
            try:
                devs = device_setup.connect_devices(device_list, stack)
            except Exception:
                return False
        return True

    @staticmethod
    def add_test_series(base_exp, vary_param, start, count, step=1):
        """
        Create a series of tests to add to the queue the at runtime.
        :param config_file: The config file for the test in question.
        :param base_config: The base config object.
        :param vary_param: The name of the parameter to vary.
        :param start: The starting value of vary_param.
        :param count: The number of tests to add.
        :param step: The amount to change vary_param by each time.
        :return: The created test series.
        """
        rqueue = []
        i = start
        for it in range(0, count):
            exp = Experiment(base_exp.config_file_name)
            exp.config.data[vary_param] = i
            rqueue.append(exp)
            i += step
        return rqueue
