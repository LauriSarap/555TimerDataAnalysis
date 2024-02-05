import os
import pandas as pd
import numpy as np
from datetime import datetime

DECIMAL_PLACES = 5


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
        file_data = pd.read_csv(file_path, sep=';', header=None)
        time_column = np.linspace(0.001, 20.000, 20000)
        time_column = np.round(time_column, DECIMAL_PLACES)

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
                'Charging End': np.round(discharging_start_time - 0.001, DECIMAL_PLACES),
                'Discharging Start': discharging_start_time,
                'Discharging End': np.round(current_time - 0.001, DECIMAL_PLACES),
                'Period Start': charging_start_time,
                'Period End': np.round(current_time - 0.001, DECIMAL_PLACES)
            })
            # Reset for the next cycle
            charging_start_time = current_time
            discharging_start_time = None

    if cycles:
        cycles.pop(0)

    #for i, cycle in enumerate(cycles, 1):
    #    print(f"Cycle {i}:")
    #    print(f"  Charging Start: {cycle['Charging Start']}, Charging End: {cycle['Charging End']}")
    #    print(f"  Discharging Start: {cycle['Discharging Start']}, Discharging End: {cycle['Discharging End']}")
    #    print(f"  Total Period Start: {cycle['Period Start']}, Total Period End: {cycle['Period End']}")

    # Print the total number of full cycles
    #print(f"Total number of full cycles found: {len(cycles)}")

    return cycles


def calculate_periods(cycles, cycle_dir, new_cycles_file_name):
    cycle_times_data = []

    for cycle in cycles:
        charge_time = cycle['Charging End'] - cycle['Charging Start']
        discharge_time = cycle['Discharging End'] - cycle['Discharging Start']
        total_period = cycle['Period End'] - cycle['Period Start']

        cycle_times_data.append({
            'Charge Time': round(charge_time, DECIMAL_PLACES),
            'Discharge Time': round(discharge_time, DECIMAL_PLACES),
            'Total Period': round(total_period, DECIMAL_PLACES)
        })

    # Convert the new list to a DataFrame
    cycle_times_df = pd.DataFrame(cycle_times_data)

    # Save the new DataFrame to a CSV file
    cycle_times_file_path = os.path.join(cycle_dir, new_cycles_file_name)
    cycle_times_df.to_csv(cycle_times_file_path, index=False, sep=',')


def process_cycles_data(processed_dir, cycles_dir):
    for file_name in os.listdir(processed_dir):
        if file_name.startswith("processed_"):  # Ensure processing only processed files
            # Construct the full path of the current file
            processed_file_path = os.path.join(processed_dir, file_name)

            # Load the data from the current file
            processed_data = pd.read_csv(processed_file_path, sep=',')

            # Identify cycles in the data
            cycles = identify_cycles(processed_data)

            original_file_name = file_name.replace('processed_', '')
            new_cycles_file_name = f"cycles_{original_file_name}"
            calculate_periods(cycles, cycle_dir=cycles_dir, new_cycles_file_name=new_cycles_file_name)
            print("Cycles data processed for file: ", original_file_name)

    print("\n")
    print("Cycles data processing complete!")


def calculate_average_cycle_lengths(cycle_dir, final_dir):
    # Define the output file names
    total_periods_file = os.path.join(final_dir, 'average_total_periods.csv')
    charge_times_file = os.path.join(final_dir, 'average_charge_times.csv')
    discharge_times_file = os.path.join(final_dir, 'average_discharge_times.csv')

    data = {}

    for file_name in os.listdir(cycle_dir):
        if file_name.startswith("cycles_"):
            parts = file_name.split('_')
            resistance_type = '_'.join(parts[1:3])  # e.g., Ra_5M
            date_text = '_'.join(parts[4:6])
            date_text = date_text.replace('.csv', '')
            timestamp = datetime.strptime(date_text, "%Y-%m-%d_%H-%M-%S")

            if resistance_type not in data:
                data[resistance_type] = []
            data[resistance_type].append((timestamp, file_name))

    for resistance_type in data.keys():
        data[resistance_type].sort(key=lambda x: x[0])

    print(data.keys())

    total_periods_results = {}
    charge_times_results = {}
    discharge_times_results = {}

    for resistance_type, files in data.items():
        total_periods = []
        charge_times = []
        discharge_times = []

        for _, file_name in files:
            df = pd.read_csv(os.path.join(cycle_dir, file_name), sep=',')
            total_periods.append(round(df['Total Period'].mean(), DECIMAL_PLACES))
            charge_times.append(round(df['Charge Time'].mean(), DECIMAL_PLACES))
            discharge_times.append(round(df['Discharge Time'].mean(), DECIMAL_PLACES))

        total_periods_results[resistance_type] = total_periods
        charge_times_results[resistance_type] = charge_times
        discharge_times_results[resistance_type] = discharge_times


    def save_results_to_csv(results, filename):
        df = pd.DataFrame(results).T
        df.columns = ['Trial 1', 'Trial 2', 'Trial 3']
        df.to_csv(os.path.join(final_dir, filename))

    save_results_to_csv(total_periods_results, 'average_total_periods.csv')
    save_results_to_csv(charge_times_results, 'average_charge_times.csv')
    save_results_to_csv(discharge_times_results, 'average_discharge_times.csv')

    print("CSV files for average cycle times created successfully.")