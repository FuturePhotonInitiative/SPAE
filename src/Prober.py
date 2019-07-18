import inspect
import sys
import types
import contextlib2
import imp
import os

from Probe.Args import Args
from Probe.ConfigFile import ConfigFile
from Probe.DeviceSetup import DeviceSetup
from src.GUI.Util.CONSTANTS import SCRIPTS_DIR
from src.GUI.Util.CONSTANTS import JSON_SCHEMA_FILE_NAME


def spawn_scripts(scripts, data_map, experiment_result):
    """
    Runs the scripts defined in the JSON config. The tasks are called based on the order specified in the config,
        two different tasks can have the same order, meaning they should be spawned at the same time.
    :param scripts: The scripts pulled from the config
    :param data_map: The dictionary to store data between tasks
    :return: None
    """
    for script in scripts:
        threads = []  # TODO add multithreading support here
        module = script.source[:-3]
        if module not in [i[0] for i in globals().items() if isinstance(i[1], types.ModuleType)]:
            globals()[module] = imp.load_source(module, os.path.join(SCRIPTS_DIR, module + '.py'))
        [i[1] for i in inspect.getmembers(globals()[module], inspect.isfunction) if i[0] is 'main'][0](data_map, experiment_result)
    print "Scripts Completed"
    return


def main(args, config_manager=None, queue_result=None):
    """
    Entry point of PTCS.
    Loads config file, parses parameters, sets up the devices, and runs the scripts specified.
    :param args: run Prober.py with no arguments to see the argument specification
    :param config_manager: the ConfigurationManager object to obtain configuration data for running the scripts
    :param queue_result: the QueueResult object to add run result data to
    :return: None
    """
    from GUI.Application.SystemConfigManager import SystemConfigManager
    if config_manager is None:
        config_manager = SystemConfigManager()

    print('Starting PTCS...')

    arguments = Args()
    arguments.parse(args[1:])
    file_name = arguments.obtain_config_file()
    if not file_name:
        print('Goodbye')
        sys.exit(1)

    config = ConfigFile.from_json_file(file_name, JSON_SCHEMA_FILE_NAME)

    data_map = {'Data': {}, 'Config': config.to_dict()}

    """
    Argument location precedence:
    First the arguments are read from the data section of the experiment json file
    Then, if one is provided, arguments are read from the parameter file
    Finally, arguments explicitly defined on the command line are added
    Arguments added later may override ones added previously if they have the same name
    """
    config.initialize_data(data_map)
    arguments.add_parameters(data_map)

    print("Running Experiment: " + config.name + "\n\n")
    experiment_result, experiment_result_name = \
        config_manager.get_results_manager().make_new_experiment_result(file_name, queue_result)

    with contextlib2.ExitStack() as stack:
        device_setup = DeviceSetup()
        data_map['Devices'] = device_setup.connect_devices(
            config.devices,
            stack
        )
        # Create json file for Config used in experiment
        experiment_result.add_json_file_dict("Config", data_map['Config'])
        spawn_scripts(config.experiment, data_map, experiment_result)

    experiment_result.end_experiment()
    config_manager.get_results_manager().save_experiment_result(experiment_result_name, experiment_result)
    print 'Experiment complete, goodbye!'


if __name__ == '__main__':
    main(sys.argv)
