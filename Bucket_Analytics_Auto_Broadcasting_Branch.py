"""
File: Bucket_Analytics_Auto_Broadcasting_Branch
Author: Yu-Ju Fang
"""
import cv2
from collections import defaultdict


def read_text(file_name):
    """
    :param file_name: Read the file we get from using yolo model to find each players' position in each frame
    :return: all the player positions in each frame
    """

    player_positions = defaultdict(list)
    with open(file_name) as f:
        contents = f.readlines()

    for i in range(len(contents)):
        lst = contents[i].split()
        player_positions[int(lst[0])].append(lst[2:6])

    return player_positions


def find_max_x(project_lst):
    """
    Find the position on x-axis that indicates most players are by using a sliding window with 300 pixel width
    :return : the position that we want to zoom in
    """
    sum_project_lst = [0] * int(WIDTH)
    for i in range(200, len(project_lst) - 200):
        sum_project_lst[i] = sum(project_lst[i - 150: i + 150])

    max_val = max(sum_project_lst)
    return sum_project_lst.index(max_val)


def zoom(max_x_position, frame1):
    """
    Zoom in the frame
    :param max_x_position: the position we are going to zoom in
    :param frame1: the current frame
    :return: the Zoomed frame
    """
    center_x, center_y = int(HEIGHT / 2), int(max_x_position)
    # radius_x and radius_y determine the scale we zoom in
    radius_x, radius_y = 240, 320  # 240, 320 suits the best for 720 * 1280 video

    min_x, max_x = center_x - radius_x, center_x + radius_x
    min_y, max_y = center_y - radius_y, center_y + radius_y

    cropped = frame1[min_x:max_x, min_y:max_y]
    resized_cropped = cv2.resize(cropped, (int(WIDTH), int(HEIGHT)))

    return resized_cropped


cap = cv2.VideoCapture('test3.mp4')  # Read the video
frame_dict = read_text('test3.txt')  # Read the txt file which stores the position of each player in each frame


WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
UPPER_COURT_BOUNDARY = 300  # upper boundary of the basketball court
LOWER_COURT_BOUNDARY = 450  # lower boundary of the basketball court
LEFT_COURT_BOUNDARY = 550
RIGHT_COURT_BOUNDARY = 700
FIXED_POSITION_LEFT_COURT = 400
FIXED_POSITION_RIGHT_COURT = 850

def main():
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    project_lst = [0] * int(WIDTH)
    first = True
    frame_number = 3

    while cap.isOpened():

        # Use yolo to capture player position and project to the x-axis
        for people in frame_dict[frame_number]:
            for pos in range(int(people[0]), int(people[0]) + int(people[2])):

                # Only players on the court should be include to determine max_x_position
                if int(people[1]) + int(people[3]) / 2 > UPPER_COURT_BOUNDARY and \
                        int(people[1]) + int(people[3]) < LOWER_COURT_BOUNDARY:
                    project_lst[pos] += int(people[3])

        # Find the start point
        max_x_position = find_max_x(project_lst)

        if first:
            prev_max_position = max_x_position
            first = False

        if WIDTH - 100 > max_x_position > 100:  # Valid Max Position

            # Decide how fast the frame should move due to the max_x_position
            if FIXED_POSITION_RIGHT_COURT > max_x_position > FIXED_POSITION_LEFT_COURT:  # 900, 400 are customized boundary
                speed = 8  # Speed is customized
            else:  # left court or right court speed
                speed = 3  # Speed is customized
            # Only move when max_x_position moves 100 pixel large than previous max position

            # Decide the position to zoom in based on the max_x_position - pre_max_position
            if max_x_position - prev_max_position > 50:
                max_x_position = prev_max_position + speed
                prev_max_position = max_x_position
            elif max_x_position - prev_max_position < -50:
                max_x_position = prev_max_position - speed
                prev_max_position = max_x_position
            else:
                if max_x_position - prev_max_position >= 0:
                    max_x_position = prev_max_position + 2
                else:
                    max_x_position = prev_max_position - 2
                prev_max_position = max_x_position

            # If max position is less than LEFT_COURT_BOUNDARY we fix the position at FIXED_POSITION_LEFT_COURT
            # which means all the players are at the left court
            if max_x_position < LEFT_COURT_BOUNDARY:
                if max_x_position > FIXED_POSITION_LEFT_COURT:
                    max_x_position -= 10
                else:
                    max_x_position = FIXED_POSITION_LEFT_COURT
            # If max position is greater than RIGHT_COURT_BOUNDARY we fix the position at FIXED_POSITION_RIGHT_COURT
            # since all the players are at the right court
            if max_x_position > RIGHT_COURT_BOUNDARY:
                if max_x_position < FIXED_POSITION_RIGHT_COURT:
                    max_x_position += 10
                else:
                    max_x_position = FIXED_POSITION_RIGHT_COURT

            # Zoom in to the max_x_position
            frame1 = zoom(max_x_position, frame1)

        else:  # invalid Max Position
            frame1 = zoom(prev_max_position, frame1)

        project_lst = [0] * int(WIDTH)  # Initialize project_lst
        cv2.imshow('Basketball Action Detection', frame1)

        frame1 = frame2
        ret, frame2 = cap.read()
        frame_number += 1
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    cap.release()


if __name__ == '__main__':
    main()