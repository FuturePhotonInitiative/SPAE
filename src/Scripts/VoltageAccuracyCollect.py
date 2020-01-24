import time


def main(data_map, experiment_result):
    """
    This stage varies an applied voltage to an oscilloscope and collects the resulting samples
    :param data_map: The dictionary to store data between tasks
    :param experiment_result: ExperimentResultsModel object
    :return: None
    """
    voltage_source = data_map['Devices']['Voltage_Source']
    osc = data_map['Devices']['Oscilloscope']
    data_map['Data']['Collect'] = {}
    start_voltage = float(data_map['Data']['Initial']["Start_Voltage"])
    final_voltage = float(data_map['Data']['Initial']["Final_Voltage"])
    step_voltage = float(data_map['Data']['Initial']["Step_Voltage"])
    oscilloscope_channel = int(data_map['Data']['Initial']["Oscilloscope_Channel"])

    voltage_source.set_voltage(0)
    voltage_source.set_output_switch(1)

    voltage = start_voltage

    start_time = time.time()
    while voltage <= final_voltage:
        print("Applying " + str(voltage) + " volts")
        voltage_source.set_voltage(voltage)
        osc.autoscale()
        data_map['Data']['Collect'][str(voltage)] = osc.measure_vaverage(oscilloscope_channel)
        voltage += step_voltage

    end_time = time.time()
    print("Collection took: " + str(end_time - start_time) + " seconds")

    voltage_source.set_voltage(0)
    voltage_source.set_output_switch(0)

    return
