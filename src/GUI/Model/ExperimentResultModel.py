import json
import os
from shutil import copyfile
import matplotlib.pyplot as plt

from src.GUI.Util.Timestamp import Timestamp


class ExperimentResultsModel:
    """
    This contains the data and functionality that saves a json file after an experiment is run that logs
    what happened in that experiment. This also contains functions to take data and make graphs out of it.
    """
    def __init__(self,
                 experiment_results_directory,
                 experiment_config_location=None,
                 experiments_results_files=None,
                 experiment_result_config=None):
        self.experiment_results_directory = experiment_results_directory
        if experiment_result_config is None:
            if experiment_config_location is not None:
                self.experiment_config_location = json.load(open(experiment_config_location, "r"))
            if experiments_results_files is None:
                experiments_results_files = []
            self.start_datetime = Timestamp()
            self.end_datetime = Timestamp()
            self.experiments_results_files = experiments_results_files
        else:
            self.load_from_json(experiment_result_config)

    def __enter__(self):
        """
        Enter method for ability to use "with open" statements
        :return: Class Object
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit to close object
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        pass

    def load_from_json(self, filename):
        """
        Write the configuration stored in this Experiment object to a json formatted file
        :param filename:
            The name of the file to write to.  WARNING: The specified file will be overwritten
        :return:
        None
        """
        config_dict = json.load(open(filename))
        self.experiment_results_directory = config_dict["experiment_results_directory"]
        self.experiment_config_location = config_dict["experiment_config_location"]
        self.start_datetime = Timestamp.from_str(config_dict["start_datetime"])
        self.end_datetime = Timestamp.from_str(config_dict["end_datetime"])
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
        config_dict["start_datetime"] = str(self.start_datetime)
        config_dict["end_datetime"] = str(self.end_datetime)
        config_dict["experiments_results_files"] = self.experiments_results_files

        with open(filename, 'w') as config_file:
            json.dump(config_dict, config_file, indent=4 if pretty_print else None, default=str)

    def add_result_file(self, file_path):
        """
        If the file given is not already in that experiment result's folder, then
        copy the file from the place where it is into the experiment result's directory under the same name
        :param file_path: the path of the file to copy/keep track of
        """
        dirname = os.path.dirname(file_path)
        if dirname != self.experiment_results_directory:
            new_file_path = os.path.join(self.experiment_results_directory, os.path.basename(file_path))
            copyfile(file_path, new_file_path)
            self.experiments_results_files.append(new_file_path)
        else:
            self.experiments_results_files.append(file_path)

    def add_scatter_chart(self, file_name, x_axis, y_axis, autoscale=True, x_lim=(-10, 10), y_lim=(-10, 10),
                          x_label="", y_label="", title=""):
        return_dir = os.getcwd()
        figure = plt.figure()
        axes = figure.add_axes((0.1, 0.2, 0.8, 0.7))

        axes.set_title(title)
        axes.set_xlabel(x_label)
        axes.set_ylabel(y_label)

        # print x_axis, y_axis
        axes.scatter(x_axis, y_axis)

        os.chdir(self.experiment_results_directory)
        text = os.path.join(os.getcwd(), file_name + ".png")

        self.experiments_results_files.append(text)

        figure.text(0.0, 0.06, text[:(len(text) // 2)], ha='left')
        figure.text(0.0, 0.02, text[(len(text) // 2):], ha='left')

        if autoscale is True:
            plt.autoscale()
        else:
            axes.set_xlim(x_lim)
            axes.set_ylim(y_lim)

        plt.savefig(file_name)
        # this should be called to free up memory but because it is not the main thread, it will error
        # plt.close()
        os.chdir(return_dir)

    def add_heat_map(self, graph_data,  title, colormap, path='', aspect='auto', graph_extent=(-0.5, 0.5, -127, 127),
                     colorbar_title="Bit Error Rate [Percentage]", y_label="Voltage (Codes)",
                     x_label="Unit Interval", vmin=0, vmax=50):
        """
        This function creates a heat map. Defaults are for Eye Scan
        :param graph_data: unicode data provided from data_map
        :param title: string, title of the plot
        :param colormap: colormap for colorbar
        :param path: the place to save the file
        :param aspect: aspect ratio
        :param graph_extent: range for data in heat map
        :param colorbar_title: Title for colorbar
        :param y_label: label for y axis
        :param x_label: label for x axis
        :param vmin: min value for colorbar
        :param vmax: max value for colorbar
        :return: None
        """
        return_dir = os.getcwd()
        os.chdir(self.experiment_results_directory)

        # Plot all of the data points on one plot
        fig, ax = plt.subplots()

        im = ax.imshow(graph_data, aspect=aspect, extent=graph_extent, cmap=colormap, vmin=vmin, vmax=vmax)

        # Create colorbar for heat map to meet requirements for eyescan colorbar
        colorbar = ax.figure.colorbar(im)
        colorbar.ax.set_ylabel(colorbar_title, rotation=-90, va="bottom")
        ax.set_title(title)
        ax.set_xlabel(x_label)  # -0.5 to 0.5 every time
        ax.set_ylabel(y_label)  # no higher than 127 in either direction
        if path == '':
            path = title
        plt.savefig(path.replace(' ', "_"))
        os.chdir(return_dir)

    def add_csv(self, file_name, data, column_labels=None, row_labels=None, title="",
                separator=",", surround_character="\"", new_line="\n"):
        out_data = ""
        if column_labels is not None:
            if row_labels is not None:
                out_data += surround_character + title + surround_character + separator
            out_data = separator.join([surround_character + str(s) + surround_character for s in column_labels])
            out_data += new_line
        for i in range(max(len(row_labels), len(data))):
            if row_labels is not None and len(row_labels) > i:
                out_data += surround_character + row_labels[i] + surround_character + separator
            if len(data) > i:
                if type(data[i]) is list:
                    out_data += separator.join([surround_character + str(s) + surround_character for s in data[i]])
                else:
                    out_data += surround_character + str(data[i]) + surround_character
                # out_data += separator.join(map(lambda s: surround_character + str(s) + surround_character, data[i]))
                out_data += new_line
        out_file_name = os.path.join(self.experiment_results_directory, file_name + ".csv")
        with open(out_file_name, "w") as out_file:
            out_file.write(out_data)
        self.experiments_results_files.append(out_file_name)

    def add_csv_dict(self, file_name, data_dict, row_labels, column_labels=None, title="",
                     separator=",", surround_character="\"", new_line="\n"):
        """
        :param file_name: the file name (without spaces and without a .csv) to save the file to
        :param data_dict: the dictionary with the data to save
        :param row_labels: i think this is just data_dict.keys()
        :param column_labels:
        :param title:
        :param separator:
        :param surround_character:
        :param new_line:
        """
        out_data = ""
        if column_labels is not None:
            out_data += surround_character + title + surround_character + separator
            out_data = separator.join([surround_character + str(s) + surround_character for s in column_labels])
            out_data += new_line
        for key in row_labels:
            out_data += surround_character + key + surround_character + separator
            if key in data_dict:
                if type(data_dict[key]) is list:
                    out_data += separator.join([surround_character + str(s) + surround_character for s in data_dict[key]])
                else:
                    out_data += surround_character + str(data_dict[key]) + surround_character
                out_data += new_line
        out_file_name = os.path.join(self.experiment_results_directory, file_name + ".csv")
        with open(out_file_name, "w") as out_file:
            out_file.write(out_data)
        self.experiments_results_files.append(out_file_name)

    def add_text_file(self, file_name, data):
        out_file_name = os.path.join(self.experiment_results_directory, file_name + ".txt")
        with open(out_file_name, "w") as out_file:
            out_file.write(data)
        self.experiments_results_files.append(out_file_name)

    def add_json_file(self, file_name, data):
        out_file_name = os.path.join(self.experiment_results_directory, file_name + ".json")
        with open(out_file_name, "w") as out_file:
            out_file.write(data)
        self.experiments_results_files.append(out_file_name)

    def add_json_file_dict(self, file_name, config):
        out_file_name = os.path.join(self.experiment_results_directory, file_name + ".json")

        with open(out_file_name, 'w') as out_file:
            json.dump(config, out_file, separators=(',', ": "), indent=4)
        self.experiments_results_files.append(out_file_name)

    def add_binary_data_file(self, data, file_name):
        out_file_name = os.path.join(self.experiment_results_directory, file_name + ".data")
        with open(out_file_name, "wb") as out_file:
            out_file.write(data)
        self.experiments_results_files.append(out_file_name)

    def add_image_file(self, data, file_name):
        out_file_name = os.path.join(self.experiment_results_directory, file_name)
        with open(out_file_name, "wb") as out_file:
            out_file.write(data)
        self.experiments_results_files.append(out_file_name)

    def start_experiment(self):
        self.start_datetime = Timestamp()

    def end_experiment(self):
        self.end_datetime = Timestamp()

    def set_start(self, start_datetime: Timestamp):
        self.start_datetime = start_datetime

    def set_end(self, end_datetime):
        self.end_datetime = Timestamp.from_str(end_datetime)

    def get_experiment_results_file_list(self):
        return self.experiments_results_files
