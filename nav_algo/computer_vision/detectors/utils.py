import cv2
import math

# Constants (could maybe double-check these)
SENSOR_HEIGHT = 2.74
FOCAL_LENGTH = 3.60  # focal length of raspberry pi cam 1


def find_distances(contours_output, img_height, img_width, obstacle_width):
    """Calculates distances from each contour and creates list of obstacle distances from camera.
    Args:
      img_height (int): height of image passed in, in pixels
    Returns:
      list: A list where each element represents an obstacle distance in meters.
    """
    distances = []
    x_displacements = []

    for contour in contours_output:
        center, size, angle = cv2.minAreaRect(contour)
        width, height = size
        distances.append((obstacle_width * FOCAL_LENGTH * img_height /
                          (height * SENSOR_HEIGHT)) / 1000)
        x_displacements.append(center[0] - img_width / 2)

    return distances, x_displacements


def find_distance_largest_contour(contours_output, img_height, img_width,
                                  obstacle_width):
    """Calculates distances from each contour and creates list of obstacle distances from camera.
    Args:
      img_height (int): height of image passed in, in pixels
    Returns:
      list: A list where each element represents an obstacle distance in meters.
    """
    try:
      c = max(contours_output, key=cv2.contourArea)
      center, size, angle = cv2.minAreaRect(c)
      width, height = size
      distance = (obstacle_width * FOCAL_LENGTH * img_height /
                  (height * SENSOR_HEIGHT)) / 1000
      x_displacement = center[0] - img_width / 2
      return distance, x_displacement
    except:
      pass


def get_coords(distance, x_displacement, direction, curr_x, curr_y):
    """
    get_coord(distance, x_displacement, direction, curr_x, curr_y) returns the
    x and y coordinates of the center of an obstacle given a calculated [distance] in front
    of the boat at coordinates [curr_x], [curr_y] facing [direction]

    Returns:
      float: The x coordinate of the obstacle center.
      float: The y coordinate of the obstacle center.
    """
    # TODO: Convert based on x displacement

    buoy_x = curr_x + distance * math.cos(direction)
    buoy_y = curr_y + distance * math.sin(direction)

    # camera facing same direction as boat
    return buoy_x, buoy_y  # returns one buoy's coordinates in our coordinate system
