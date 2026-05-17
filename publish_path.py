"""
Publishes the text-to-path strokes as a ROS topic.
Teammate's ROS node subscribes to /drawing/path and executes.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time
from text_to_path import text_to_waypoints, strokes_to_3d

TEXT = "hello"
HEIGHT_MM = 30
TOPIC_NAME = "/drawing/path"  # CHANGE if teammate wants different name

class PathPublisher(Node):
    def __init__(self):
        super().__init__('path_publisher')
        self.pub = self.create_publisher(String, TOPIC_NAME, 10)
        self.timer = self.create_timer(1.0, self.publish_once)
        self.published = False
        self.get_logger().info(f'Will publish to {TOPIC_NAME}')
    
    def publish_once(self):
        if self.published:
            return
        strokes = text_to_waypoints(TEXT, height_mm=HEIGHT_MM)
        waypoints = strokes_to_3d(strokes)
        payload = {
            "text": TEXT,
            "height_mm": HEIGHT_MM,
            "n_strokes": len(strokes),
            "waypoints": [[float(x), float(y), float(z)] for x, y, z in waypoints]
        }
        msg = String()
        msg.data = json.dumps(payload)
        self.pub.publish(msg)
        self.get_logger().info(
            f'Published "{TEXT}" — {len(strokes)} strokes, {len(waypoints)} 3D waypoints'
        )
        self.published = True

def main():
    rclpy.init()
    node = PathPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()