import csv
import datetime
from helper.tool_assessment import ToolState, NUMBER_OF_PICTURES
from pathlib import Path


def create_line(timestamp, image_path, prediction, operator, rotation):
    datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    date_formatted = datetime_obj.strftime("%d.%m.%Y")
    time_formatted = datetime_obj.strftime("%H:%M:%S")
    line = [date_formatted, time_formatted, image_path, -1, 0, prediction, "_", operator, "", rotation]
    return line


def load_csv(csv_file):
    Path(csv_file).touch(exist_ok= True)
    return list(csv.reader(open(csv_file)))


def save_csv(csv_file, lines):
    print("Saving ", len(lines), " assessments to ", csv_file)
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(lines)


def save_tool_states(tools, csv_file):
    lines = load_csv(csv_file)

    for tool in tools:
        for image_number in range(NUMBER_OF_PICTURES):
            if not tool.get_state(image_number) or tool.get_state(image_number) == ToolState.NONE:
                continue
            
            state = tool.get_state(image_number).value
            image_data = tool.get_image_paths(image_number)
            timestamp = image_data["timestamp"]
            path = image_data["image_path"]
            rotation = image_data["rotation"]
            user = "Operator" if tool.get_operator_assessment(image_number) != ToolState.NONE else "AI"

            lines.append(create_line(timestamp, path, state, user, rotation))

    save_csv(csv_file, lines)