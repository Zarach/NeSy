import datetime
import json

import roman
from clearml import Task, Dataset

#task = Task.init(project_name='NeSy', task_name='classificator training')
# cloned_task = Task.clone(source_task=task)
# Task.enqueue(task=cloned_task, queue_name='default')
#task.execute_remotely(queue_name="default")

from tensorflow.keras.layers import TimeDistributed, LSTM, Reshape

from numpy.lib.stride_tricks import sliding_window_view

import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, Flatten, Dropout
from tensorflow.keras.callbacks import TensorBoard

import matplotlib.pyplot as plt
from sklearn import preprocessing
#import tensorflow_addons as tfa

import os
import Utils

class TimeSeriesPatternRecognition():

    WINDOW_SIZE = 599
    RESAMPLING_RATE = '1s'

    def create_model(self):

        model = Sequential()#add model layers
        model.add(Conv1D(30, kernel_size=10, activation="relu", strides=1, input_shape=(self.WINDOW_SIZE, 1)))
        model.add(Conv1D(30, kernel_size=8, activation="relu", strides=1))
        model.add(Conv1D(40, kernel_size=6, activation="relu", strides=1))
        #model.add(Dropout(0.1))
        model.add(Conv1D(50, kernel_size=5, activation="relu", strides=1))
        #model.add(Dropout(0.2))
        model.add(Conv1D(50, kernel_size=5, activation="relu", strides=1))
        #model.add(Dropout(0.4))
        model.add(Flatten())
        model.add(Dense(1024, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(1, activation='sigmoid'))
        return model

    def create_dataset(self, dataset_X, dataset_Y, window_size=599):
        gap = int((window_size-1)/2)
        dataX, dataY = [], []
        # for i in range(len(dataset_X)-window_size-1):
        #     a = dataset_X.iloc[i:(i+window_size), 0]
        #     dataX.append(a)
        #     dataY.append(dataset_Y.iloc[i + int(window_size/2)])
        #     print(i)
        # dataX = np.reshape(np.array(dataX), [-1, window_size, 1])
        dataX = np.reshape(dataset_X.to_numpy(), [len(dataset_X)])
        dataX = sliding_window_view(dataX, window_size)
        index = dataset_Y.index[(int(window_size/2)):-(int(window_size/2))]
        dataY = np.array(dataset_Y.iloc[gap:-gap])
        dataY[dataY > 10] = 1
        return dataX, dataY, index

    def run(self, experiment_number, period_start, period_end, database_root="DataBases", results_root="Results", models_path='', load=True, finetune=True):
        df_power_consumption = Utils.load_csv_from_folder(database_root+"/Barthi/power_consumption", "timestamp")[['smartMeter']]



        # Finetuning Labels
        if load is True:
            path = f'{results_root}/evaluation_plausibility_manual_{roman.toRoman(experiment_number-1)}.csv'
            df_active_phase_all = pd.read_csv(path, header=0, index_col=0, parse_dates=[0])
            df_active_phase_plausibility = df_active_phase_all.drop(['ground truth'], axis=1).dropna()
            # df_active_phase_plausibility = df_active_phase_all.fillna(0)
            df_active_phase_plausibility = df_active_phase_plausibility.resample(self.RESAMPLING_RATE).median()

        # Pretraining Labels
        df_active_phase_all = Utils.load_csv_from_folder(database_root+"/Barthi/active_phases", "timestamp")

        df_active_phase = pd.DataFrame()

        df_active_phase['activity'] = df_active_phase_all['kettle'] #+ \
        #                                 df_active_phase_all['coffee machine'] + \
        #                                 df_active_phase_all['washing machine'] + \
        #                                 df_active_phase_all['microwave'] + \
        #                                 df_active_phase_all['toaster'] + \
        #                                 df_active_phase_all['television'] + \
        #                                 df_active_phase_all['thermomix']

        #df_active_phase = pd.read_csv('DataBases/Barthi/active_phases/hund.csv', header=0, index_col=0)

        pd.to_datetime(df_power_consumption.index)
        df_active_phase.index = pd.to_datetime(df_active_phase.index)

        df_active_phase = df_active_phase.fillna(0)
        df_power_consumption = df_power_consumption.resample(self.RESAMPLING_RATE).mean()

        df_active_phase = df_active_phase.resample(self.RESAMPLING_RATE).median()
        #df = pd.concat([df_power_consumption, df_active_phase], axis=1, ignore_index=False)
        #df_power_consumption = df_power_consumption.iloc[:-360] #241920, 51840
        #df_active_phase = df_active_phase.iloc[360:]
        #df_active_phase.index = df_power_consumption.index

        min_max_scaler = preprocessing.MinMaxScaler()
        df_power_consumption_scaled = pd.DataFrame(min_max_scaler.fit_transform(df_power_consumption.values.reshape([-1,1])))
        df_power_consumption_scaled.index = df_power_consumption.index

        #train_X, test_X, train_y, test_y = train_test_split(df_power_consumption_scaled, df_active_phase, test_size=.5,random_state=10)

        # plt.plot(pd.DataFrame(df_power_consumption))
        # plt.plot(pd.DataFrame(df_active_phase)*1000)
        # plt.show()

        # cut = int(df_active_phase.shape[0]/2)



        # finetuning Barthi
        # Train: "2022-12-05 00:00:00":"2022-01-18 23:59:59"
        # Test I: "2022-12-19 00:00:00":"2023-01-01 23:59:59"
        # Test II: "2023-01-02 00:00:00":"2023-01-15 23:59:59"
        # Test III: "2023-01-16 00:00:00":"2023-01-29 23:59:59"
        # Test IV: "2023-01-30 00:00:00":"2023-02-12 23:59:59"
        # Test V: "2023-02-13 00:00:00":"2023-02-26 23:59:59"
        # Test VI: "2023-02-27 00:00:00":"2023-03-12 23:59:59"
        # Test VII: "2023-03-13 00:00:00":"2023-03-26 23:59:59"

        test_period_start = (datetime.datetime.strptime(period_start, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
        test_period_end = (datetime.datetime.strptime(period_end, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")

        print(f'Train model on {period_start} - {period_end}')
        print(f'Test model on {test_period_start} - {test_period_end}')



        train_X, test_X = df_power_consumption_scaled.loc[period_start:period_end], df_power_consumption_scaled.loc[
                                                                                    test_period_start:test_period_end]

        # pretraining round Barthi
        if load is False:
            train_y, test_y = df_active_phase.loc[period_start:period_end], df_active_phase.loc[test_period_start:test_period_end]
            recall_weight = 20.
            lr = 0.0001
        else:
            train_y, test_y = df_active_phase_plausibility.loc[period_start:period_end], df_active_phase.loc[test_period_start:test_period_end]
            recall_weight = 1.
            lr = 0.00001
        #
        # plt.plot(pd.DataFrame(train_X))
        # plt.plot(pd.DataFrame(train_y))
        # plt.show()
        #plt.plot(train_X)
        #plt.plot(train_y)
        #plt.show()

        # train_y = train_y*2-1
        # test_y = test_y*2-1
        # train_X_time, train_y_time, index = self.create_dataset(train_X, train_y)
        # test_X_time, test_y_time, index = self.create_dataset(test_X, test_y)
        # train_dataset = tf.data.Dataset.from_tensor_slices((train_X_time, train_y_time))
        # test_dataset = tf.data.Dataset.from_tensor_slices((test_X_time, test_y_time))

        train_dataset = tf.keras.utils.timeseries_dataset_from_array(
            train_X, train_y.iloc[int(self.WINDOW_SIZE/2):, :], sequence_length=self.WINDOW_SIZE)
        test_dataset = tf.keras.utils.timeseries_dataset_from_array(
            test_X, test_y.iloc[int(self.WINDOW_SIZE/2):, :], sequence_length=self.WINDOW_SIZE)

        # dataset = tf.data.Dataset.from_tensor_slices(train_X[:500, :], train_y[:500, :])
        # dataset = dataset.window(5, shift=1, drop_remainder=True)
        # dataset = dataset.flat_map(lambda window: window.batch(5))
        # for x, y  in dataset:
        #     print(x.numpy(), y.numpy())

        #test_X = test_X.set_index(test_y.index)
        y_time_index = test_y.iloc[int(self.WINDOW_SIZE/2):, :].index

        logdir = "logs/scalars/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        tensorboard_callback = TensorBoard(log_dir=logdir)


        #f1 = tfa.metrics.F1Score(num_classes=1, average=None, threshold=0.2)

        metrics = []
        metrics.append(tf.keras.metrics.BinaryAccuracy())
        metrics.append(tf.keras.metrics.Precision(thresholds=0.2))
        metrics.append(tf.keras.metrics.Recall(thresholds=0.2))
        #metrics.append(f1)
        #metrics.append(tf.keras.metrics.TruePositives())
        #metrics.append(tf.keras.metrics.TrueNegatives())
        #metrics.append(tf.keras.metrics.FalsePositives())
        #metrics.append(tf.keras.metrics.FalseNegatives())



        #Kettle
        class_weight = {0: 1.,
                        1: recall_weight}
        modelKettle = self.create_model()

        optimizer = tf.keras.optimizers.Adam(learning_rate=lr)

        modelKettle.compile(optimizer, loss='binary_crossentropy', metrics=metrics)

        if load:
            print(f'model {roman.toRoman(experiment_number-1)} loaded')
            modelKettle.load_weights(f"{models_path}/model_finetuned_{roman.toRoman(experiment_number-1)}.h5")
            # modelKettle = model
        if finetune:
            for layer in modelKettle.layers[:5]:
                layer.trainable = False

        modelKettle.summary()



        if not load or finetune:
            modelKettle.fit(train_dataset, epochs=5, class_weight=class_weight, callbacks=[tensorboard_callback])#, verbose=2)
            modelKettle.save_weights(f"Models/model_finetuned_{roman.toRoman(experiment_number)}.h5")

        eval_metrics = modelKettle.evaluate(test_dataset)
        print(f"Evaluation Metrics: {eval_metrics}")
        evalKettle = pd.DataFrame(modelKettle.predict(test_dataset))

        modelKettle.load_weights(f"{models_path}/model_finetuned_N.h5")
        eval_metrics_compare_N = modelKettle.evaluate(test_dataset)



        #Microwave
        # modelMicrowave = create_model()
        # modelMicrowave.compile('adam', loss='binary_crossentropy', metrics=metrics)
        # modelMicrowave.fit(train_X_time, train_y_time, epochs=50)
        # print(modelMicrowave.evaluate(test_X_time, test_y_time))
        # evalMicrowave = pd.DataFrame(modelMicrowave.predict(test_X_time), index=index)


        start = None
        end = None
        activity_values = []
        activity_id = 0
        threshold = 0.2
        facts = []

        evalKettle[evalKettle < threshold] = 0
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"{results_root}/evaluation_nn_{roman.toRoman(experiment_number)}.csv"
        abs_file_path = os.path.join(script_dir, rel_path)

        evalKettle.to_csv(abs_file_path)


        for idx, value in enumerate(evalKettle.values):
            if value < threshold and start is not None and end is not None:
                print(str(y_time_index[start]) + " - " + str(y_time_index[end]))
                probability = (sum(activity_values) / len(activity_values))[0]

                activity_predicate_string = f"{probability}::kettle({activity_id})."
                facts.append(activity_predicate_string)

                start_date_predicate_string = f"start({activity_id}, \'{y_time_index[start]}\')."
                #print(start_date_predicate_string)
                facts.append(start_date_predicate_string)

                end_date_predicate_string = f"end({activity_id}, \'{y_time_index[end]}\')."
                #print(end_date_predicate_string)
                facts.append(end_date_predicate_string)

                activity_id += 1

                activity_values = []
                start = None
                end = None
            elif start is None and value >= threshold:
                start = evalKettle.index[idx]
                activity_values.append(value)
            elif value >= threshold:
                activity_values.append(value)
            elif value < threshold and start is not None:
                end = evalKettle.index[idx]

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"{database_root}/Facts/facts_from_ml_sensors_finetuned_{roman.toRoman(experiment_number)}.json"
        print(f"Saving Facts from Model to '{database_root}/Facts/facts_from_ml_sensors_finetuned_{roman.toRoman(experiment_number)}.json'")
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path, 'w') as facts_file:
            json_string = json.dumps(facts, ensure_ascii=False, indent=4)
            facts_file.write(json_string)

        # plt.plot(pd.DataFrame(test_X, index=index))
        # plt.plot(pd.DataFrame(test_y_time, index=index))
        # plt.plot(evalKettle)
        # plt.show()
        # print('--------------------------------------------------------')
        print('Time Series Pattern Recognition done')
        return eval_metrics, eval_metrics_compare_N
