# Maivin EdgeFirst Service Subscriber

This project demonstrates subscribing to a Maivin EdgeFirst Service from Python and reading messages from the published topics.  The services on Maivin follow a ROS2-like pattern though without using ROS2 itself.  Instead messages are communicated using the [Zenoh](https://zenoh.io) messaging framework with message contents encoded using [CDR](https://en.wikipedia.org/wiki/Common_Data_Representation) according to the [Maivin EdgeFirst Schemas](https://github.com/MaivinAI/schemas).  We prioritize using the published ROS2 schemas from the [ROS2 Common Interfaces](https://github.com/ros2/common_interfaces/tree/humble) when possible.  Where the ROS2 Common Interface schemas are insuffient custom schemas are defined and published.

Refer to [Maivin EdgeFirst Schemas](https://github.com/MaivinAI/schemas) for an overview of the services and their schemas used by this example project.

# Examples

The following examples are provided which are all based on topics which can be easily viewed and interpreted with text output.

- topics.py
  - Subscribes to all topics and lists newly discovered ones on the console

- schema.py
  - Subscribes to a topic and prints the schema name for each message on the console
  - Explains how to identify the correct schema for a message using the encoding

- detect.py
  - Prints the object detection and tracking information currently observed by the Maivin

- camerainfo.py
  - Prints the camera configuration information

- imu.py
  - Prints the pose (yaw, pitch, roll) of the camera using the IMU

- navsat.py
  - Prints the global lattitude/longitude coordinates of the camera using the GPS

# Camera

A dedicated repository, [camerasub-py](https://github.com/MaivinAI/camerasub-py), is provided to demonstrate using the Maivin camera service which requires additional specialized processing to work with camera frames.

# License

This project is licensed under the AGPL-3.0 or under the terms of the DeepView AI Middleware Commercial License.

# Support

Commercial Support is provided by Au-Zone Technologies through the [DeepView Support](https://support.deepviewml.com) site.
