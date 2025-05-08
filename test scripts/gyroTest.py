from witmotion import IMU

#https://witmotion.readthedocs.io/en/latest/quickstart.html

def callback(msg):
    print(msg)

imu = IMU()
#imu.subscribe(callback)
imu.get_quaternion()