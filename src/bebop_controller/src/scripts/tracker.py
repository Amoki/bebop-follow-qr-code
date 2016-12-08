#!/usr/bin/env python
# coding: utf-8
import rospy
import datetime
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Int8
from std_msgs.msg import Empty


TARGET_DISTANCE_MIN = 0.30
TARGET_DISTANCE_MAX = 0.50


class Controller():
    def __init__(self):
        self.pub_take_off = rospy.Publisher('bebop/takeoff', Empty, queue_size=10)
        self.pub_land = rospy.Publisher('bebop/land', Empty, queue_size=10)
        self.pub = rospy.Publisher('bebop/cmd_vel', Twist, queue_size=10)
        self.target_locked = False
        self.started = False
        self.last_target_locked = datetime.datetime.now()
        self.takeoff_date = datetime.datetime.now()
        rospy.Subscriber("/visp_auto_tracker/object_position", PoseStamped, self.callback_position)
        rospy.Subscriber("/visp_auto_tracker/status", Int8, self.callback_locked)

    def callback_position(self, data):
        if self.target_locked and (datetime.datetime.now() - self.takeoff_date).total_seconds() > 3:
            self.compute_move(data)
        else:
            self.pub.publish(Twist(linear=Vector3(x=0, y=0, z=0), angular=Vector3(x=0, y=0, z=0)))

    def callback_locked(self, data):
        if data.data == 3:
            self.target_locked = True
            self.last_target_locked = datetime.datetime.now()
            if not self.started:
                self.started = True
                self.takeoff_date = datetime.datetime.now()
                self.pub_take_off.publish()
        else:
            self.target_locked = False
            if self.started and (datetime.datetime.now() - self.last_target_locked).total_seconds() > 10:
                self.started = False
                self.pub_land.publish()

    def compute_move(self, data):
        '''
        x -0.30 (left) to +0.30 (right)
        y -0.13 (trop haut) to +0.13 (trop bas)
                           z    w
        robot à gauche : 0.30 0.30  x et y positifs
        robot à droite : 0.15 0.15  x et y négatifs
        face   : 0    0

        '''
        position = data.pose.position
        orientation = data.pose.orientation

        # Pivot
        angular_z = - 3.3 * position.x

        # Move forward / backward
        if TARGET_DISTANCE_MIN < position.z and position.z < TARGET_DISTANCE_MAX:
            linear_x = 0
        elif position.z < TARGET_DISTANCE_MIN:
            linear_x = (position.z - TARGET_DISTANCE_MIN) / 1.5
        else:  # position.z > TARGET_DISTANCE_MAX
            linear_x = (position.z - TARGET_DISTANCE_MAX) / 3.5

        # translate right of left
        linear_y = 0.0
        if orientation.x > 0:
            direction = -1.0
        else:
            direction = 1.0

        linear_y = orientation.z * direction / 3.5

        # height
        linear_z = - 2 * position.y

        linear = Vector3(
            x=linear_x,  # pitch (angle)
            y=linear_y,  # roll (angle) - => droite AND + => gauche
            z=linear_z   # vertical velocity
        )
        angular = Vector3(
            x=0,
            y=0,
            z=angular_z  # only Z is useful (rotate axis : + = counter-clockwise, - = clockwise) -1 to 1
        )

        message = Twist(linear=linear, angular=angular)
        print("%f\t%f\t%f\t%f" % (position.z, orientation.y, 0.0, position.x))
        print("%f\t%f\t%f\t%f" % (linear_x, linear_y, 0.0, angular_z))

        self.pub.publish(message)


def run():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('bebop_controller', anonymous=True)

    Controller()

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    run()
