import nav_algo.coordinates as coord
import nav_algo.boat as boat
import math


def newSailingAngle(boat, target):
    """TODO Determines the best angle to sail at.

        The sailboat follows a locally optimal path (maximize vmg while minimizing
        directional changes) until the global optimum is "better" (based on the
        hysterisis factor).

        Returns:
            float: The best angle to sail (in the global coordinate system).

    """

    beating = 10.0  # TODO

    boat_to_target = target.vectorSubtract(boat.getPosition())

    right_angle_max, right_vmg_max = optAngle(boat_to_target, boat, True)
    left_angle_max, left_vmg_max = optAngle(boat_to_target, boat, False)

    boat_heading = boat.sensors.velocity.angle()
    hysterisis = 1.0 + (beating / boat_to_target.magnitude())
    sailing_angle = right_angle_max
    if (abs(right_angle_max - boat_heading) <
            abs(left_angle_max - boat_heading) and right_vmg_max * hysterisis <
            left_vmg_max) or (abs(right_angle_max - boat_heading) >=
                              abs(left_angle_max - boat_heading)
                              and left_vmg_max * hysterisis >= right_vmg_max):
        sailing_angle = left_angle_max

    return sailing_angle


def optAngle(boat_to_target, boat, right):
    """TODO Determines the best angle to sail on either side of the wind.

        The "best angle" maximizes the velocity made good toward the target.

        Args:
            right (bool): True if evaluating the right side of the wind, False for left.

        Returns:
            float: The best angle to sail (in the global coordinate system).
            float: The velocity made good at the best angle.

    """
    delta_alpha = 1.0  # TODO is this ok?
    alpha = 0.0
    best_vmg = 0.0
    wind_angle = boat.sensors.wind_direction
    best_angle = wind_angle

    while alpha < 180:
        vel = polar(alpha if right else -1.0 * alpha, boat)
        vmg = vel.dot(boat_to_target.toUnitVector())

        if vmg > best_vmg:
            best_vmg = vmg
            best_angle = wind_angle + alpha if right else wind_angle - alpha

        alpha = alpha + delta_alpha

    return coord.rangeAngle(best_angle), best_vmg


def polar(angle, boat):
    """Evaluates the polar diagram for a given angle relative to the wind.

        Args:
            angle (float): A potential boat heading relative to the absolute wind direction.
            boat (BoatController): The BoatController (either sim or real)

        Returns:
            Vector: A unit boat velocity vector in the global coordinate system.

      """
    # TODO might want to use a less simplistic polar diagram
    angle = coord.rangeAngle(angle)
    if (angle > 20 and angle < 160) or (angle > 200 and angle < 340):
        # put back into global coords
        return coord.Vector(angle=angle + boat.sensors.wind_direction)
    return coord.Vector.zeroVector()


def endurance():
    pass


def stationKeeping(waypoints, circle_radius, state, opt_angle=45):
    if state == "ENTRY":
        stationKeepingWaypoints = []  # Necessary waypoints
        # entry point to the square
        square_entries = [waypoints[0].midpoint(waypoints[1]),
                        waypoints[1].midpoint(waypoints[2]),
                        waypoints[2].midpoint(waypoints[3]),
                        waypoints[3].midpoint(waypoints[0])]
        curr_pos = boat.getPosition()
        shortest_dist = min((curr_pos.xyDist(square_entries[0]), square_entries[0]),
                            (curr_pos.xyDist(
                                square_entries[1]), square_entries[1]),
                            (curr_pos.xyDist(
                                square_entries[2]), square_entries[2]),
                            (curr_pos.xyDist(
                                square_entries[3]), square_entries[3]),
                            key=lambda x: x[0])
        stationKeepingWaypoints.append(shortest_dist[1])

        # center of the sqaure
        center = waypoints[0].midpoint(waypoints[2])
        stationKeepingWaypoints.append(center)
        waypoints = stationKeepingWaypoints
        return
    elif state == "KEEP":
        # downwind=wind-yaw=0=clockwise,
        keep_waypoints = []
        # radian_angle = math.radians(opt_angle)
        x_coord = boat.getPosition().x
        y_coord = boat.getPosition().y
        boat_direction = boat.sensors.yaw
        #get wind direction relative to boat
        relative_wind=boat.sensors.wind_direction-boat_direction
        if relative_wind<0:
            relative_wind+=360
        if relative_wind >= 180:
            # move ccw
            loop_direction = 1
        else:
            # move cw
            loop_direction = -1
        # compute angle of first waypoint
        first_angle = boat_direction + opt_angle * loop_direction
        if (first_angle < 0):
            first_angle += 360
        # convert to radians for computation of other waypoints using trig
        first_angle_rad = math.radians(first_angle)

        for i in range(4):
            # place 4 waypoints each 90 deg apart; when angle>2pi, trig functions know to shift input to be in range
            input_angle = first_angle_rad + \
                loop_direction * i * math.radian(90)
            keep_waypoints.append((x_coord+circle_radius*math.cos(input_angle)), (y_coord+circle_radius*math.sin(input_angle))

        waypoints=keep_waypoints
        return keep_waypoints

    elif state == "EXIT":
        # corner waypoint order: NW, NE, SE, SW
        # TODO: ask Courtney about the units of x-y coord
        units_away=10
        # north exit
        north_exit=waypoints[0].midpoint(waypoints[1])
        north_exit.y += units_away
        # east exit
        east_exit=waypoints[1].midpoint(waypoints[2])
        east_exit.x += units_away
        # south exit
        south_exit=waypoints[2].midpoint(waypoints[3])
        south_exit.y -= units_away
        # west exit
        west_exit=waypoints[0].midpoint(waypoints[3])
        west_exit.x -= units_away
        # exit waypoint order in list: N, E, S, W
        curr_pos=boat.getPosition()
        shortest_dist=min((curr_pos.xyDist(north_exit), north_exit),
                            (curr_pos.xyDist(east_exit), east_exit),
                            (curr_pos.xyDist(south_exit), south_exit),
                            (curr_pos.xyDist(west_exit), west_exit),
                            key=lambda x: x[0])
        waypoints=[shortest_dist[1]]
        return

def find_inner_outer_points(start_point, end_point, dist, flag):
    #1 is in, -1 is out, 0 is on the line
    slope = (start_point.y - end_point.y) / (start_point.x - end_point.x)
    if flag != 0:
        slope = -1/slope
        x = flag * (start_point.x + math.sqrt(dist/(1+slope**2)))
        y = flag * (start_point.y + slope * math.sqrt(dist/(1+slope**2)))
    else:
        x = start_point.x + math.sqrt(dist/(1+slope**2))
        y = start_point.y + slope * math.sqrt(dist/(1+slope**2))
        return (x, y)

def buoy_offset(start_point, buoy, dist):
    slope = (start_point.y - end_point.y) / (start_point.x - end_point.x)
    x = buoy.x + math.sqrt(dist/(1+slope**2))
    y = buoy.y + slope * math.sqrt(dist/(1+slope**2))
    return (x, y)
    
def precisionNavigation(waypoints, offset=5.0, side_length=50.0):
    #waypoints:[topleft_buoy, topright_buoy, botleft_buoy, botright_buoy]
    topleft_buoy=waypoints[0]
    topright_buoy=waypoints[1]
    botleft_buoy=waypoints[2]
    botright_buoy=waypoints[3]
    
    x_coord = boat.getPosition().x
    y_coord = boat.getPosition().y
    boat_direction = boat.sensors.yaw
    relative_wind=boat.sensors.wind_direction-boat_direction    
    if relative_wind<0:
        relative_wind+=360 
    if relative_wind >= 180:
        # move ccw
        sail_direction = 1
    else:
        # move cw
        sail_direction = -1
                
    start_pos = topleft_buoy.midpoint(topright_buoy)
    # find inner and outer waypoints on first side of triangle
    start_point = start_pos
    end_point = botleft_buoy
    dist = (start_point.xyDist(end_point))/3
    point_line = find_inner_outer_points(start_point, end_point, dist, 0)
    first_waypoint = find_inner_outer_points(point_line, end_point, dist, 1)    
    dist_out = 2 * dist
    point_line_2 = find_inner_outer_points(start_point, end_point, dist_out, 0)
    second_waypoint = find_inner_outer_points(point_line_2, end_point, dist_out,-1)
    # first offset from buoy
    dist_buoy = (start_point.xyDist(end_point))/10
    third_waypoint = buoy_offset(start_point, end_point, dist_buoy)
    
    # find inner and outer waypoints on second side of triangle
    start_point = end_point
    end_point = botright_buoy

    dist = (start_point.xyDist(end_point))/3
    point_line = find_inner_outer_points(start_point, end_point, dist, 0)
    fourth_waypoint = find_inner_outer_points(point_line, end_point, dist, 1)    
    dist_out = 2 * dist
    point_line_2 = find_inner_outer_points(start_point, end_point, dist_out, 0)
    fifth_waypoint = find_inner_outer_points(point_line_2, end_point, dist_out,-1)    
    # second offset from buoy
    dist_buoy = (start_point.xyDist(end_point))/10
    sixth_waypoint = buoy_offset(start_point, end_point, dist_buoy)

    # find inner and outer waypoints on third side of triangle
    start_point = end_point
    end_point = start_point
    dist = (start_point.xyDist(end_point))/3
    point_line = find_inner_outer_points(start_point, end_point, dist, 0)
    seventh_waypoint = find_inner_outer_points(point_line, end_point, dist, -1)    
    dist_out = 2 * dist
    point_line_2 = find_inner_outer_points(start_point, end_point, dist_out, 0)
    eighth_waypoint = find_inner_outer_points(point_line_2, end_point, dist_out,1)    
    # final waypoint is start_point
    ninth_waypoint = start_pos

    waypoints = [first_waypoint, second_waypoint, third_waypoint, 
                fourth_waypoint, fifth_waypoint, sixth_waypoint, 
                seventh_waypoint, eighth_waypoint, ninth_waypoint]
    return
    
def collisionAvoidance():
    pass


def search():
    pass
