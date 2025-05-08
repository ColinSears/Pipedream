from setuptools import setup, find_packages

setup(
    name="pipedream",
    version="1.0.0",
    description="Pipedream Satellite GUI and Controller",
    author="Colin Sears",
    author_email="colin.sears17@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "colorzero==2.0",
        "evdev==1.9.1",
        "gpiozero==2.0.1",
        "imutils==0.5.4",
        "numpy==2.2.4",
        "opencv-python==4.11.0.86",
        "pillow==11.2.1",
        "pyserial==3.5",
        "RPi.GPIO==0.7.1",
    ],
    entry_points={
        "console_scripts": [
            "pipedream=pipedream.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
