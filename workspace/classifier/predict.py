import sys
sys.path.append('.')
import requests
import json
import numpy as np
import pandas as pd
from keras.preprocessing.image import ImageDataGenerator
from PIL import Image
from helper.tool_assessment import ToolState
from helper.config import PREDICTION_URL

PREDICTION_DIR = 'storage/prediction.json'


def write_predict_result(data):
    with open(PREDICTION_DIR, "w") as file:
        json.dump(data, file)


def read_predict_result():
    with open(PREDICTION_DIR, "r") as file:
        data = json.load(file)
    return data


def make_prediction(instances):
    """
    Sends the images to the AI model and returns its predictions

    :param instances: the images to be classified by the AI model
    :return: the predictions of the provided images
    """
    # server URL
    url = PREDICTION_URL
    data = json.dumps({"signature_name": "serving_default",
                      "instances": instances.tolist()})
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
        print(
            f"True Value: {img_label[i]}, Predicted Value: {np.argmax(pred)} \n")
    return predictions


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
        # sets how many pairs of images and labels are to be selected per generator cycle
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=True,
        seed=42
    )
    return generator


def create_states_arr(predictions, path_list, is_verify=False):
    ret = []
    for prediction in range(0, len(predictions)):
        state = ToolState.GOOD
        if is_verify:
            res = int(predictions[prediction])
        else:
            res = int(np.argmax(predictions[prediction]))
        #print("Result:", str(res))
        if res > 2:
            print("Warning, result value is not in range 0-1")
            print("Predictions output: ")
            print(predictions[prediction])
        if res == 1:
            state = ToolState.BAD
        elif res == 2: 
            state = ToolState.RECYCLE
        result_object = {
            'tool': path_list[prediction],
            'state': state
        }
        #print("Result Object: " + str(result_object))
        ret.append(result_object)
    return ret

# ToDo image predictions might not be on the same sort as put


def predict_image_list(path_list):
    images = []
    for item in path_list:
        images.append(np.array(Image.open(item)))
    predictions = make_prediction(np.array(images))
    return create_states_arr(predictions, path_list)


def verify_predcit():
    path_csv = "classifier/testdata.csv"
    # path to the image dataset
    path_dataset = "classifier/testdataset"
    dataframe = read_data_from_csv_file(filepath=path_csv)
    data_gen = data_generator(path=path_dataset, dataframe=dataframe)
    # next(data_gen) return one cycle of images and their corresponding labels. In this case 8 (see batch_size in data_generator()) pairs.
    img, label = next(data_gen)
    # Gets the numerical value of the label.
    label = np.argmax(label, axis=-1)
    res = print_predictions(img, label)
    print("Res text is:")
    print(res)
    print("Label is:")
    print(label)
    pred_states_arr = create_states_arr(res, res)
    real_states_arr = create_states_arr(label, label, is_verify=True)
    return pred_states_arr, real_states_arr


def verify():
    path_csv = "classifier/testdata.csv"
    # path to the image dataset
    path_dataset = "classifier/testdataset"
    dataframe = read_data_from_csv_file(filepath=path_csv)
    data_gen = data_generator(path=path_dataset, dataframe=dataframe)
    # next(data_gen) return one cycle of images and their corresponding labels. In this case 8 (see batch_size in data_generator()) pairs.
    img, label = next(data_gen)
    # Gets the numerical value of the label.
    label = np.argmax(label, axis=-1)
    res = print_predictions(img, label)
    return create_states_arr(res, res)
