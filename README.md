Bebop Follow QR Code
====================

## Dependencies
ROS Indigo (if needed, feel free to post de PR or ask me to create versioned branches)

catkin-tools (see https://catkin-tools.readthedocs.io/en/latest/installing.html)

## Install
```bash
git clone --recursive git@github.com:Amoki/bebop-follow-qr-code.git
cd bebop-follow-qr-code
catkin build -DCMAKE_BUILD_TYPE=RelWithDebInfo
```

## Start
```bash
source devel/setup.bash
roslaunch bebop_tracker bebop.launch
```


The drone take off when it sees a QR code and automatically lands if there is no recognized QR Code for 10 seconds

