# Pipe Dream

**Aerospace Engineering Senior Design Project**  
**Iowa State University, 2025**

**Pipe Dream** is an **Senior Design Project**, focusing on the development of a **Design Test Unit (DTU)**—a neutral buoyancy craft that simulates a small-scale satellite. The DTU is capable of:
- **Undocking & Redocking** using a custom four arm pin and slider mechanism
- **Maneuvering** using compressed air solenoids as thrusters
- **Capturing an image** via an onboard camera

### Graphical User Interface (GUI)

The accompanying software provides a **modular GUI** to assist the pilot with real-time operations. Key modules include:
- **Video Camera Feed** for live monitoring
- **Last Captured Image Display** for reviewing obtained visuals
- **Command Table** to show current input
- **Gyroscope Readings** for orientation awareness

### Future Improvements

Future improvements include making the controller joystick inputs more reliable, improving the gyroscope portion of the GUI by using quaternion data to create a 3D model of the craft's orientation, and adding autonomous stability.

---

## Author

This codebase was developed by **Colin Sears**.

## Team Collaboration

This project was made possible by the full Pipe Dream team. The design, hardware integration, and testing were led by the rest of the team. Special thanks to the following team members:

- Alicia Minkel, *Team Lead & Project Coordinator*
- Bryce Moore, *Structural Design*
- Oakley Oxley, *Mechanical Systems*
- Patrick Kinn, *Electronics*
- Andrew Boelter, *Propulsion Systems*

Special thanks to faculty and mentors who supported the project.

---

## Setup & Installation

### Dependencies
Before running the software, ensure the following dependencies are installed:

- **Python** (>=3.7)
- **colorzero** (`colorzero==2.0`)
- **evdev** (`evdev==1.9.1`)
- **gpiozero** (`gpiozero==2.0.1`)
- **imutils** (`imutils==0.5.4`)
- **NumPy** (`numpy==2.2.4`)
- **OpenCV** (`opencv-python==4.11.0.86`)
- **Pillow** (`pillow==11.2.1`)
- **pyserial** (`pyserial==3.5`)
- **RPi.GPIO** (`RPi.GPIO==0.7.1`)

### Installation
To install the software and set up the environment:

1. Clone the repository
2. Navigate to the project directory
3. Install the required dependencies package using setuptools: python setup.py install

### Running
Once installed, you can launch the software using one of the following methods
- ```python pipedream.cli```
- ```pipedream``` if installed using setup.py

The GUI interface is initalized with the camera, gyroscope, and controller modules enabled as default. These can be changed in the cli.py file. The GUI interface can be quit via a button on the controller, keyboard interrupt, or closing the GUI.
