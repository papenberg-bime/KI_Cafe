# KICafe - Prüfzelle

## Installation

to install pipenv:
```bash
pip install --user pipenv
```

to install the dependencies:
```bash
pipenv install
```

## Prepare AI

Ensure that the AI docker container is running.

## Run the program

When a python executable is selected in Visual Studio Code, the python version can be selected in the lower status bar. Select
`~\.virtualenvs\workspace-l7EAPbj7\Scripts\python.exe` (PipEnv). Now it is possible to run the program with the arrow in the upper right corner.

OR:

```bash
C:\Python39\Scripts\pipenv.exe shell

pipenv run python main.py
```

## General Structure of the Project

The project is structured in the following way:

- `main.py`: This is the main file which starts the program. It contains the code which should start the ui and perform the evaluation of the tools: The tools are picked up individually, guided to the camera and several photos are taken, then the tool is put down again. The photos are stored in a folder specified in `config.ini` and the evaluation is displayed in a separate window. 

- `config.ini`: Contains configuration variables for the application, like the directory to store photos and the file to store the tool assessment CSV file and the IP address of the robot.

  The defaults are as follows: 
  ```ini
  [DEFAULT]
  RobotHost = 169.254.46.85
  ClassifierApiUrl = http://localhost:8501/v1/models/tool_classifier:predict
  ImageDirectory = D:\Storage
  CsvPath = D:\Storage\tool_assessment.csv

  # AI Image Size
  #   Default width = 380, height = 704
  CroppedImageWidth = 380
  CroppedImageHeight = 704
  LogFilePath = D:\Storage\log.txt
  ```

- `helper/*`: Code used by other scripts for camera usage (camera.py), gripper information (gripper_status.py), robot status information (robot_status.py), robot control (robot.py) and assessment status (tool_assessment.py)
  - robot_status uses an rtde connection (using code from Universal robots in the ./rtde directory) to the robot, to gather it's status information. The data fields which is returned by the robot are specified in the file ./assets/record_configuration.xml. (The method used before, using data returned on Real-Time interface 30003, is deprecated and only returned data after a move command which did not work in a seperate thread with the ui).
  
  - `helper/movement_paths_structure.py`: Herein are the waypoints to pick up the tools, move them near the camera and to move them back to their home slots. 

  - `helper/scripts/movel_extractor.py`: Script to get the current waypoint of the robot as a movel code command.
- `ui/*`: Code for the ui.
- `vendor/`: Contains third party code:
  - rtde module from Universal Robots 
  - ur_robotiq_gripper (MIT License)
- `assets/`: Contains images for the UI, exported and edited URScripts for Gripper control and the record_configuration for the rtde lib.

## Maintenance Points in the Code
### Configuration

See the ```config.ini``` file.

### Recalibrating Photo Positioning after Mirror/Camera Changes

If the mirror is changed, the position in which photos are made has to be calibrated. See in ```robot.py``` the function ```find_sensor_and_move_to_photo_position```. 

```python
43 def find_sensor_and_move_to_photo_position(self):        
44        self.find_tool_sensor(z_step=0.001)
45        self.move_down(0.0065)
46        self.move_relative(x=0.0075, y=-0.03166) 
```

In line 44 the robot searches the tool sensor, to estimate the length of the tool. After finding it it moves down in line 45. In line 46 it moves relative in x and y to position the tool right under the mirror.
