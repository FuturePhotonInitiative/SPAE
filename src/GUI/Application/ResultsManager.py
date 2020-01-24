import os

from src.GUI.Model import QueueResultModel
from src.GUI.Model.ExperimentModel import Experiment
from src.GUI.Model.ExperimentResultModel import ExperimentResultsModel
from src.GUI.Util.Functions import clean_name_for_file
from src.GUI.Util.CONSTANTS import QUEUE_FILE_TITLE
from src.GUI.Util.Timestamp import Timestamp


class ResultsManager:
    def __init__(self, results_directory, results_config_directory):
        self.queue_result_list = []
        self.experiment_result_dict = {}
        self.results_directory = results_directory
        self.results_config_directory = results_config_directory
        if not os.path.exists(results_config_directory):
            os.mkdir(results_config_directory)
        for config in os.listdir(results_config_directory):
            if QUEUE_FILE_TITLE in config:
                self.queue_result_list.append(QueueResultModel.QueueResultsModel(
                    queue_result_config=os.path.join(results_config_directory, config))
                )
            else:
                self.experiment_result_dict[config.replace(".json", "")] = (ExperimentResultsModel(
                    results_directory,
                    experiment_result_config=os.path.join(results_config_directory, config))
                )

    def get_list_of_queue_results(self):
        pass

    def get_experiment_result(self, key):
        return self.experiment_result_dict[key]

    def get_list_of_experiment_result_names(self):
        return list(self.experiment_result_dict.keys())

    def make_new_experiment_result(self, exeriment_config_location, queue_result):
        now = Timestamp()
        if queue_result.time is not None:
            now = queue_result.time
        exp = Experiment(exeriment_config_location)

        name = exp.get_name() + now.for_filename()
        name = clean_name_for_file(name)

        if not os.path.exists(self.results_directory):
            os.mkdir(self.results_directory)
        this_result_folder = os.path.join(self.results_directory, name)
        if not os.path.exists(this_result_folder):
            os.mkdir(this_result_folder)

        result = ExperimentResultsModel(os.path.join(self.results_directory, name), exeriment_config_location)
        result.set_start(now)
        self.experiment_result_dict[name] = result
        if queue_result:
            queue_result.add_experiment_result(name)
        return [result, name]

    def make_new_queue_result(self):
        result = QueueResultModel.QueueResultsModel()
        self.queue_result_list.append(result)
        # print "STUFF HAPPENS HERE", len(self.queue_result_list)
        return result

    def save_experiment_results(self):
        for name in list(self.experiment_result_dict.keys()):
            self.save_experiment_result(name, self.experiment_result_dict[name])

    def save_queue_results(self):
        for queue_result in self.queue_result_list:
            queue_result.save()

    def save_experiment_result(self, name, experiment_result):
        experiment_result.export_to_json(os.path.join(self.results_config_directory, name + ".json"))

    def get_queue_results(self):
        return self.queue_result_list
