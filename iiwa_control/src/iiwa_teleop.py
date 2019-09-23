#!/usr/bin/env python

import rospy
import sys, select, termios, tty

from std_msgs.msg import String, Header, Float64
from rospy import init_node, get_param, loginfo, Publisher
from geometry_msgs.msg import PoseStamped
from low_level_logics.compact_utilities import CompactTransform
from numpy import pi

def getKey():
  tty.setraw(sys.stdin.fileno())
  select.select([sys.stdin], [], [], 0)
  key = sys.stdin.read(1)
  termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
  return key

def printCmd(cmd):
  print('X{:.2f} Y{:.2f} Z{:.2f} A{:.2f} B{:.2f} C{:.2f} R{:.2f}'.format(
    cmd['X'], cmd['Y'], cmd['Z'], cmd['A'], cmd['B'], cmd['C'], cmd['R']))

if __name__=="__main__":
  settings = termios.tcgetattr(sys.stdin)

  init_node('keyboard')
  pose_pub = Publisher('command/CartesianPose', PoseStamped, queue_size = 1)
  redundancy_pub = Publisher('command/redundancy', Float64, queue_size = 1)
  robot_name = get_param('~robot_name', 'iiwa')

  cmd = {'X': 0.5, 'Y': 0.0, 'Z': 0.4, 'A': 0.0, 'B': pi, 'C': 0.0, 'R': 0.0}

  key_map = {
      'w': ('X', 0.01),
      's': ('X', -0.01),
      'e': ('Y', 0.01),
      'd': ('Y', -0.01),
      'r': ('Z', 0.01),
      'f': ('Z', -0.01),
      'u': ('A', 0.1),
      'j': ('A', -0.1),
      'i': ('B', 0.1),
      'k': ('B', -0.1),
      'o': ('C', 0.1),
      'l': ('C', -0.1),
      'p': ('R', 0.1),
      ';': ('R', -0.1),
      }

  try:
    while(1):
      key = getKey()

      if key == '\x03':
        break
      elif key in key_map:
        cmd[key_map[key][0]] += key_map[key][1]

        printCmd(cmd)

        redundancy_pub.publish(Float64(cmd['R']))
        pose_pub.publish(
            PoseStamped(
              header = Header(
                frame_id = '{}_link_0_horizontal'.format(robot_name)),
              pose = CompactTransform.fromXYZRPY(
                cmd['X'], cmd['Y'], cmd['Z'], cmd['C'], cmd['B'], cmd['A']).toPose()))
      else:
        printCmd(cmd)

  except Exception as e:
    print(e)

  finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
