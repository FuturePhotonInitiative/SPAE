import datetime
import json
import os
from shutil import copyfile
import matplotlib.pyplot as plt

class ExperimentResultsModel:
    def __init__(self,
                 experiment_results_directory,
                 experiment_config_location=None,
                 experiments_results_files=None,
                 start_datetime=datetime.datetime.today(),
                 end_datetime=datetime.datetime.today(),
                 experiment_result_config=None):
        self.experiment_results_directory = experiment_results_directory
        if experiment_result_config is None:
            if self.experiment_config_location is not None:
                self.experiment_config_location = json.load(experiment_config_location)
            if experiments_results_files is None:
                experiments_results_files = []
            self.start_datetime = start_datetime
            self.end_datetime = end_datetime
            self.experiments_results_files = experiments_results_files
        else:
            self.load_from_json(experiment_results_directory)

    def load_from_json(self, filename):
        """
        Write the configuration stored in this Experiment object to a json formatted file
        :param filename:
            The name of the file to write to.  WARNING: The specified file will be overwritten
        :param pretty_print:
            If true, print the json with indentation, otherwise keep the JSON compact
        :return:
        None
        """
        config_dict = json.load(filename)
        self.experiment_results_directory = config_dict["experiment_results_directory"]
        self.experiment_config_location = config_dict["experiment_config_location"]
        self.start_datetime = config_dict["start_datetime"]
        self.end_datetime = config_dict["end_datetime"]
        self.experiments_results_files = config_dict["experiments_results_files"]

    def export_to_json(self, filename, pretty_print=True):
        """
        Write the configuration stored in this Experiment object to a json formatted file
        :param filename:
            The name of the file to write to.  WARNING: The specified file will be overwritten
        :param pretty_print:
            If true, print the json with indentation, otherwise keep the JSON compact
        :return:
        None
        """
        config_dict = {}
        config_dict["experiment_results_directory"] = self.experiment_results_directory
        config_dict["experiment_config_location"] = self.experiment_config_location
        config_dict["start_datetime"] = self.start_datetime
        config_dict["end_datetime"] = self.end_datetime
        config_dict["experiments_results_files"] = self.experiments_results_files

        with open(filename, 'w') as config_file:
            json.dump(config_dict, config_file, indent=4 if pretty_print else None)

    def add_result_file(self, experiment_file_location):
        path_of_file = os.path.dirname(file)
        if path_of_file != self.experiment_results_directory:
            file_name = experiment_file_location.replace(path_of_file, "")
            copyfile(experiment_file_location, self.experiment_results_directory + file_name)
            self.experiments_results_files.append(self.experiment_results_directory + file_name)
        else:
            self.experiments_results_files.append(experiment_file_location)

    def add_scatter_chart(self, x_axis, y_axis, file_name, x_label="", y_label = "", title=""):
        return_dir = os.getcwd()
        figure = plt.figure()
        axes = figure.add_axes((0.1, 0.2, 0.8, 0.7))

        axes.set_title(title)
        axes.set_xlabel(x_label)
        axes.set_ylabel(y_label)

        axes.scatter(x_axis, y_axis)

        os.chdir(self.experiment_results_directory)
        text = os.getcwd() + file_name + ".png"

        self.experiments_results_files.append(text)

        figure.text(0.0, 0.06, text[:len(text) / 2], ha='left')
        figure.text(0.0, 0.02, text[len(text) / 2:], ha='left')

        axes.set_xlim((0, 10))
        axes.set_ylim((0, 8))
        # plt.autoscale()
        plt.savefig(file_name)
        os.chdir(return_dir)

    def add_csv(self, data, file_name, column_labels=None, row_labels=None, title="",
                seperator=",", surround_character="\"", new_line="\n"):
        out_data = ""
        if column_labels is not None:
            if row_labels is not None:
                out_data += surround_character + title + surround_character + seperator
            out_data = seperator.join(map(lambda s: surround_character + str(s) + surround_character,
                                          column_labels))
            out_data += new_line
        for i in range(max(len(row_labels), len(data))):
            if row_labels is not None and len(row_labels) > i:
                out_data += surround_character + row_labels[i] + surround_character + seperator
            if len(data) > i:
                out_data += seperator.join(map(lambda s: surround_character + str(s) + surround_character, data[i]))
                out_data += new_line
        out_file_name = self.experiment_results_directory + "//" + file_name + ".csv"
        out_file = open(out_file_name, "w")
        out_file.write(out_data)
        self.experiments_results_files.append(out_file_name)

    def add_text_file(self, data, file_name):
        out_file_name = self.experiment_results_directory + "//" + file_name + ".txt"
        out_file = open(out_file_name, "w")
        out_file.write(data)
        self.experiments_results_files.append(out_file_name)
    #
    # def add_binary_data_file(self, data, file_name):
    #     out_file_name = self.experiment_results_directory + "//" + file_name + ".data"
    #     out_file = open(out_file_name, "wb")
    #     out_file.write(data)
    #     self.experiments_results_files.append(out_file_name)

    def start_experiment(self):
        self.start_datetime = datetime.datetime.today()

    def end_experiment(self):
        self.end_datetime = datetime.datetime.today()

    def set_start(self, start_datetime):
        self.start_datetime = start_datetime

    def set_end(self, end_datetime):
        self.end_datetime = end_datetime

    def get_experiment_results_file_list(self):
        return self.experiments_results_files

