from setuptools import setup, find_packages

setup(
    name="pipedream",
    version="0.1.0",
    description="Pipedream Satellite GUI and Controller",
    author="Colin Sears",
    author_email="colin.sears17@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "Pillow",
        "evdev",         
        "pyserial",
    ],
    entry_points={
        "console_scripts": [
            "pipedream=cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
