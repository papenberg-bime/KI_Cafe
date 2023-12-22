import requests
import json
import numpy as np
import pandas as pd
from keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf

def make_prediction(instances):
    """
    Sends the images to the AI model and returns its predictions

    :param instances: the images to be classified by the AI model
    :return: the predictions of the provided images
    """
    # server URL
    url = 'http://localhost:8501/v1/models/tool_classifier:predict'
    data = json.dumps({"signature_name": "serving_default", "instances": instances.tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return predictions


def print_predictions(images, img_label):
    """
    prints the results from make_prediction() and their corresponding true label

    :param img_label: True value corresponding to the image, representing the expert classification of the tool wear.
    :param images: image of the tool
    :return:
    """
    predictions = make_prediction(images)
    for i, pred in enumerate(predictions):
        print(pred)
        print(f"True Value: {img_label[i]}, Predicted Value: {np.argmax(pred)} \n")


def read_data_from_csv_file(filepath):
    """
    Help function for testing purposes!
    Creates a pandas dataframe based on the given .csv file using the column names listed in "names"

    Bedeutung der Zahlen in den Spalten Licht und Zustand:
    Licht 0: Ringlicht, Licht 1: Koaxialleuchte
    Zustand 0: in Ordnung, Zustand 1: nicht in Ordnung

    :param filepath: filepath to the .csv file
    :return: pandas dataframe containing the data from the .csv file
    """
    return pd.read_csv(filepath, sep=",", dtype=str,
                       names=["Datum", "Uhrzeit", "Dateiname", "Durchmesser", "Licht", "Zustand", "Werkzeug", "Pruefer",
                              "Anmerkungen", "Rotation"], index_col=False)


def data_generator(path, dataframe):
    """
    Help function for testing purposes!
    Creates a data generator that is used to load the images from the image_dataset

    :param path: path to the directory of the image dataset
    :param dataframe: dataframe containing the images to select from the image dataset
    :return: generator that contains a set of 8 (see batch_size) pairs of images and the corresponding label.
    """
    datagen = ImageDataGenerator()
    batch_size = 8
    generator = datagen.flow_from_dataframe(
        dataframe=dataframe,
        directory=path,
        x_col="Dateiname",
        y_col="Zustand",
        target_size=(705, 380),  # height and width of the images
        batch_size=batch_size,  # sets how many pairs of images and labels are to be selected per generator cycle
        class_mode="categorical",
        shuffle=True,
        seed=42
    )
    return generator


if __name__ == "__main__":
    # path to the csv-file
    path_csv = "testdata.csv"
    # path to the image dataset
    path_dataset = "testdataset"
    dataframe = read_data_from_csv_file(filepath=path_csv)
    data_gen = data_generator(path=path_dataset, dataframe=dataframe)
    # next(data_gen) return one cycle of images and their corresponding labels. In this case 8 (see batch_size in data_generator()) pairs.
    img, label = next(data_gen)
    # Gets the numerical value of the label.
    label = np.argmax(label, axis=-1)
    print_predictions(img, label)

