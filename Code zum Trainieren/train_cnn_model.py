import os
import pandas as pd
import numpy as np
from datetime import datetime
from keras.applications.efficientnet import EfficientNetB0
from keras.layers import Input, Conv2D, Flatten, Dense, MaxPool2D, BatchNormalization, GlobalAveragePooling2D, \
    Activation, ReLU, Dropout, Concatenate
from keras.utils import load_img, plot_model
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model, load_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import seaborn as sn
import tensorflow as tf
from matplotlib import pyplot as plt


def delete_first_lines(path, filename):
    """
       Deletes the first 6 lines from the file if not already done.

       :param path: Path of the file.
       :param filename: Name of the file.
    """
    filename = os.path.join(path, filename)
    file = open(filename, "r")
    lines = file.readlines()
    if lines[0][0:5] != "Datum":
        new_file = open(filename, "w+")
        for line in lines[6:]:
            new_file.write(line)


def create_dataframe(path, filename):
    """
        Creates a DataFrame from the given .txt file and adds a column named "Rotation".

        :param path: Path of the file.
        :param filename: Name of the file.

        :return: DataFrame created from the file.
    """
    filename = os.path.join(path, filename)
    df = pd.read_csv(filename, sep=";", dtype=str)
    columnName = "Rotation"
    degrees = [0, 45, 90, 135, 180, 225, 270, 315]
    df[columnName] = [str(degrees[int(x[12]) - 1]) for x in df["Dateiname"]]
    return df


def filter_dataframe(df, date=None, time=None, filename=None, diameter=None, light=None, states=None, tool=None,
                     operator=None, comment=None, rotation=None):
    """
       Filters the given DataFrame by the given parameters.

       :param df: Given DataFrame.
       :param date: Filter by date.
       :param time: Filter by time.
       :param filename: Filter by filename.
       :param diameter: Filter by diameter.
       :param light: Filter by light.
       :param state: Filter by state.
       :param tool: Filter by tool.
       :param operator: Filter by operator.
       :param comment: Filter by comment.
       :param rotation: Filter by rotation.

       :return: Filtered DataFrame.
    """
    df_return = df[0:0]
    if date is not None:
        df_return = df.loc[df["Datum"] == date]
    if time is not None:
        df_return = df.loc[df["Uhrzeit"] == time]
    if filename is not None:
        df_return = df.loc[df["Dateiname"] == filename]
    if diameter is not None:
        df_return = df.loc[df["Durchmesser"] == diameter]
    if light is not None:
        df_return = df.loc[df["Licht"] == light]
    if states is not None:
        for state in states:
            df_return = pd.concat([df_return,df.loc[df["Zustand"] == state]])
    if tool is not None:
        df_return = df.loc[df["Werkzeug"] == tool]
    if operator is not None:
        df_return = df.loc[df["Pruefer"] == operator]
    if comment is not None:
        df_return = df.loc[df["Anmerkungen"] == comment]
    if rotation is not None:
        df_return = df.loc[df["Rotation"] == rotation]
    return df_return


def create_subdatasets(df, validation_split=0.5, test_split=0.4):
    """
        Splits the DataFrame into training, validation, and test sets.

        :param df: Given DataFrame.
        :param validation_split: Percentage of data to use for validation based on the test_split.
        :param test_split: Percentage of data to use for testing.

        :return: DataFrames for training, validation, and testing.
    """
    df_train, df_test = train_test_split(df, stratify=df["Zustand"], test_size=test_split)
    df_test, df_validation = train_test_split(df_test, stratify=df_test["Zustand"], test_size=validation_split)
    return df_train, df_validation, df_test


def create_csv_from_dataframe(df_train, df_val, df_test):
    """
        Creates CSV files from the DataFrames.

        :param df_train: DataFrame for training data.
        :param df_val: DataFrame for validation data.
        :param df_test: DataFrame for test data.
    """
    date = datetime.now().strftime("%Y_%m_%d_%H_%M")
    new_dir_path = os.path.join(os.getcwd(), date + "_Trainingsdurchlauf_3_Classes")  # Name des Ordners ggf. anpassen
    os.mkdir(new_dir_path)
    os.chdir(new_dir_path)
    df_train.to_csv(date + '_train.csv', mode='a', index=False, header=False)
    df_val.to_csv(date + '_val.csv', mode='a', index=False, header=False)
    df_test.to_csv(date + '_test.csv', mode='a', index=False, header=False)


def data_generator(path, df):
    """
       Creates a data generator for the given DataFrame.

       :param path: Path to the images.
       :param df: DataFrame containing image file names and labels.

       :return: ImageDataGenerator object.
    """
    datagen = ImageDataGenerator()  # rescale=1./255
    batch_size = 8
    generator = datagen.flow_from_dataframe(
        dataframe=df,
        directory=path,
        x_col="Dateiname",
        y_col="Zustand",
        target_size=(705, 380),
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False,
        # seed=42
    )
    return generator


def create_subdatasets_from_csv_same_tool_same_light(path, filename, states):
    """
        Creates the subdatasets and makes sure that images of the same milling tool are placed in the same subdataset.

        :param path: Path to the data file.
        :param filename: Name of the data file.

        :return: DataFrames for training, validation, and testing after filtering.
    """
    df = create_dataframe(path=path, filename=filename)
    df = filter_dataframe(df=df, date=None, time=None, filename=None, diameter=None, light=None, states=states, tool=None,
                          operator=None, comment=None, rotation=None)
    df_dropped = df.drop_duplicates(subset=["Werkzeug"])
    df_train, df_val, df_test = create_subdatasets(df_dropped)
    df_train_tmp = df_train[0:0]
    df_val_tmp = df_val[0:0]
    df_test_tmp = df_test[0:0]
    for index, row in df_train.iterrows():
        df_temp = df.loc[df["Werkzeug"] == row["Werkzeug"]]
        df_train_tmp = pd.concat([df_train_tmp, df_temp])
    for index, row in df_val.iterrows():
        df_temp = df.loc[df["Werkzeug"] == row["Werkzeug"]]
        df_val_tmp = pd.concat([df_val_tmp, df_temp])
    for index, row in df_test.iterrows():
        df_temp = df.loc[df["Werkzeug"] == row["Werkzeug"]]
        df_test_tmp = pd.concat([df_test_tmp, df_temp])
    df_train_1 = df_train_tmp
    df_val_1 = df_val_tmp
    df_test_1 = df_test_tmp
    return df_train_1, df_val_1, df_test_1


def write_train_data(content):
    """
       Writes the content into a text file.

       :param content: String to write.
    """
    file_name = datetime.now().strftime("%Y_%m_%d_%H_%M") + '_Trainingsdaten.txt'
    with open(file_name, 'a') as file:
        file.write(content + '\n')


def confmat(model, test_g, n_classes):
    """
       Computes and displays the confusion matrix for the model's performance.

       :param model: Trained Keras model.
       :param test_g: Test data generator.
    """
    loss, accuracy = model.evaluate(test_g)
    test_g.reset()
    test_g.shuffle = False
    Y_pred = model.predict(test_g)
    y_pred = np.argmax(Y_pred, axis=1)
    print('Confusion Matrix:')
    cm = confusion_matrix(y_true=test_g.classes, y_pred=y_pred)
    print(cm)
    print('Accuracy:', accuracy)
    df_cm = pd.DataFrame(cm, range(n_classes), columns=range(n_classes))
    sn.set(font_scale=1)
    svm = sn.heatmap(df_cm, annot=True, annot_kws={"size": 14})
    figure = svm.get_figure()
    title = "confusion matrix"
    plt.title(title)
    plt.ylabel("True Label")
    plt.xlabel("Classified as")
    filename = datetime.now().strftime("%Y%m%d-%H%M%S") + "_" + title
    figure.savefig(filename, dpi=400)


def define_model(n_classes):
    """
       Defines the model architecture using EfficientNetB0.
        :param n_classes:, 2 for the classification between not worn and worn, 3 for the addition of regrinding
       :return: Compiled Keras model.
    """
    weights = "imagenet"
    base_model = EfficientNetB0(include_top=False, weights=weights)
    for layer in base_model.layers:
        layer.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dense(128, activation='relu')(x)
    x = Dense(64, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    predictions = Dense(n_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)
    model.summary()
    model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    return model


def train_net(path, filename, states):
    """
        Trains the defined model using the data in the given path and filename.

        :param path: Path to the data folder.
        :param filename: Name of the data file.
        :param n_classes:, ["0","1"] for the classification between not worn and worn, ["0","1","2"] for the addition of regrinding
    """
    model = define_model(n_classes=len(states))
    df_train, df_val, df_test = create_subdatasets_from_csv_same_tool_same_light(path, filename, states=states)

    train_generator = data_generator(df=df_train, path=path)
    validation_generator = data_generator(df=df_val, path=path)
    test_generator = data_generator(df=df_test, path=path)

    tf_reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001)
    model.fit(train_generator, validation_data=validation_generator, epochs=50, callbacks=[tf_reduce_lr])
    loss, accuracy = model.evaluate(test_generator)
    write_train_data('accuracy: ' + str(accuracy) + "\n" +
                     'loss: ' + str(loss) + "\n" +
                     'epoch: ' + str(accuracy))
    print('Loss:', loss)
    print('Accuracy:', accuracy)
    model.save(datetime.now().strftime("%Y%m%d-%H%M%S"), save_format='tf')
    confmat(model, test_generator, n_classes=len(states))


if __name__ == '__main__':
    path = r""  # path to the images
    filename = ".csv"  # Filename of the .csv file that lists all images
    train_net(path, filename, states=["0","1"])  #
