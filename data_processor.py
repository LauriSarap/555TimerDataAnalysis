import os
import pandas
import numpy as np


def preprocess_data(data_dir, processed_dir):
    file_list = os.listdir(data_dir)
    csv_files = [file for file in file_list if file.endswith(".csv")]
    sorted_files = sorted(csv_files, key=lambda x: x.split('_')[3])

    trials = {
        'trial_1': sorted_files[0::3],
        'trial_2': sorted_files[1::3],
        'trial_3': sorted_files[2::3],
    }


    # Data preprocessing
    def process_file(file_path):
        file_data = pandas.read_csv(file_path, sep=';', header=None)
        time_column = np.linspace(0.001, 20.000, 20000)
        time_column = np.round(time_column, 3)

        file_data.insert(0, 'Time', time_column)
        column_names = ['Time', 'Output Voltage', 'Capacitor Voltage']
        file_data.columns = column_names
        return file_data


    for trial_name, files in trials.items():
        for file_name in files:
            file_path = os.path.join(data_dir, file_name)
            processed_data = process_file(file_path)
            new_file_name = f"processed_{file_name}"
            save_path = os.path.join(processed_dir, new_file_name)
            processed_data.to_csv(save_path, index=False, sep=',')
    print("Data preprocessing complete!")


def identify_cycles(data_file):
    charging_start_time = None
    discharging_start_time = None
    cycles = []

    # Iterate over the rows of the DataFrame
    for index, row in data_file.iterrows():
        output_voltage = row['Output Voltage']
        current_time = row['Time']

        if charging_start_time is None and output_voltage > 1:
            charging_start_time = current_time
        if charging_start_time is None and output_voltage < 1:
            discharging_start_time = current_time

        elif charging_start_time is not None and discharging_start_time is None and output_voltage < 3:
            discharging_start_time = current_time

        elif discharging_start_time is not None and output_voltage > 3:
            cycles.append({
                'Charging Start': charging_start_time,
                'Charging End': np.round(discharging_start_time - 0.001, 3),
                'Discharging Start': discharging_start_time,
                'Discharging End': np.round(current_time - 0.001, 3),
                'Period Start': charging_start_time,
                'Period End': np.round(current_time - 0.001, 3)
            })
            # Reset for the next cycle
            charging_start_time = current_time
            discharging_start_time = None

    if cycles:
        cycles.pop(0)

    for i, cycle in enumerate(cycles, 1):
        print(f"Cycle {i}:")
        print(f"  Charging Start: {cycle['Charging Start']}, Charging End: {cycle['Charging End']}")
        print(f"  Discharging Start: {cycle['Discharging Start']}, Discharging End: {cycle['Discharging End']}")
        print(f"  Total Period Start: {cycle['Period Start']}, Total Period End: {cycle['Period End']}")

    # Print the total number of full cycles
    print(f"Total number of full cycles found: {len(cycles)}")

    return cycles


def calculate_periods(cycles, cycle_dir, new_cycles_file_name):
    cycle_times_data = []

    for cycle in cycles:
        charge_time = cycle['Charging End'] - cycle['Charging Start']
        discharge_time = cycle['Discharging End'] - cycle['Discharging Start']
        total_period = cycle['Period End'] - cycle['Period Start']

        cycle_times_data.append({
            'Charge Time': round(charge_time, 3),
            'Discharge Time': round(discharge_time, 3),
            'Total Period': round(total_period, 3)
        })

    # Convert the new list to a DataFrame
    cycle_times_df = pandas.DataFrame(cycle_times_data)

    # Save the new DataFrame to a CSV file
    cycle_times_file_path = os.path.join(cycle_dir, new_cycles_file_name)
    cycle_times_df.to_csv(cycle_times_file_path, index=False, sep=',')