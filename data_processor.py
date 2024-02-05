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