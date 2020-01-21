import os
import threading
import time

from .QueueRunner import QueueRunner
from src.GUI.Model.ExperimentQueue import ExperimentQueue
from src.GUI.Model.ExperimentModel import Experiment


class QueueManager:
    def __init__(self, temp_dir, results_config_manager):
        self.results_config_manager = results_config_manager
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        self.experiment_queue = ExperimentQueue()

    def remove_from_queue(self, experiment):
        self.experiment_queue.remove_from_queue(experiment)

    def get_ith_experiment(self, index):
        return self.experiment_queue.get_ith_experiment(index)

    def run_queue(self, to_run):
        """
            Starts the thread that runs the queue.
        :param to_run:
            The queue to be run
        :return:
            None, immediately
        """
        queue_result = self.results_config_manager.get_results_manager().make_new_queue_result()
        runner = QueueRunner(to_run, queue_result)
        runner.start()

    def get_experiment_names(self):
        return self.experiment_queue.get_experiment_names()

    def add_to_queue(self, experiment):
        self.experiment_queue.add_to_queue(experiment)

    def run(self):
        self.run_queue(self.experiment_queue)

    def clear_queue(self):
        self.experiment_queue.clear_queue()

    def save_queue_to_file(self, folder_path, name):
        """
        Save the queue to a file
        :param folder_path:
            The folder to save it in.
        :return:
            The index of the saved queue
        """
        index = len(os.listdir(folder_path)) + 1
        output = ""
        for i in range(len(self.experiment_queue)):
            exp = self.experiment_queue.get_ith_experiment(i)
            output += "*" + exp.config_file_name.split("/")[-1][:-5] + "\n"
            for field in (list(exp.config.data.keys()) if exp.config.data else dict()):
                output += str(exp.config.data[field]) + " // " + str(field) + "\n"

        with open(folder_path + "/Saved_Experiment_" + name, "w") as f:
            f.write(output)
        return index

    def read_queue_from_file(self, file_path, config_root):
        """
        Construct a queue from a file
        :param file_path:
            The file to read from.
        :param config_root:
            The folder to read config files from.
        :return:
            The constructed queue.
        """
        rqueue = []
        if not os.path.isfile(file_path):
            return False
        with open(file_path) as f:
            exp = None
            for line in f.readlines():
                if line.startswith('*'):
                    if exp is not None:
                        rqueue.append(exp)
                    exp = Experiment(line[1:-1] + ".json")
                else:
                    ind = line.find(' // ')
                    if ind > -1:
                        val = line[:ind]
                        if len(val) > 0 and ('0' <= val[0] <= '9' or val[0] == '.') and '_' not in val:
                            try:
                                val = int(val)
                            except ValueError:
                                ux = 0
                                while val[ux] in ' .0123456789':
                                    ux += 1
                                uv = QueueManager.parse_units(line[ux:])
                                if exp.config.data.get('Units', None) is not None:
                                    uv /= QueueManager.parse_units(exp.config.data['Units'])
                                val = float(line[:ux].replace(" ", ""))*uv
                            if float(int(val)) == val:
                                val = int(val)
                        exp.config.data[line[ind+4:-1]] = val
            rqueue.append(exp)
        self.experiment_queue.queue.clear()
        self.experiment_queue.queue.extend(rqueue)
        return True

    @staticmethod
    def parse_units(s):
        """
        Determine the multiplier for a given unit string.
        :param s: Unit string.
        :return: Multiplier.
        """
        units = {"T": 1000000000000, "G": 1000000000, "M": 1000000, "K": 1000, "k": 1000,
                 "m": .001, "u": .000001, "n": .000000001, "p": .000000000001}
        if len(s) > 1:
            for u in units:
                if s.startswith(u):
                    return units[u]
        return 1
