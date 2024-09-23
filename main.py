import cv2
import datetime
import os
import shutil

from scanGUI import ScanGUI

# If set to True, will attempt to connect to localhost instead of external camera system
TEST = False
SAVE_FRAME_RATE = 4     # Frame rate to save animated frames for later viewing. Will not save if set to 0 or negative.


def makeVideo(file_name, image_folder, frame_rate):

    if not os.path.exists(image_folder):
        raise FileNotFoundError('Image folder \'' + image_folder + '\' does not exist')

    images = [img for img in sorted(os.listdir(image_folder)) if img.endswith('.jpg')]
    if len(images) < 1:
        shutil.rmtree(image_folder)
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(file_name + '.mp4', fourcc, frame_rate, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    video.release()


def main():
    run = True

    while run:
        # Get a unique name for the recording of the session
        session_name = 'animation_' + datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')

        actual_frame_rate = 0
        gui = ScanGUI(test=TEST, save_frame_rate=SAVE_FRAME_RATE, session_name=session_name)
        try:
            session_success = gui.run(connect_attempt_limit=10)
        except ConnectionRefusedError as e:
            print('Server not found, trying again...')
            continue

        except ConnectionResetError as e:
            print('Connection reset by server, closing application')

            gui.shutdown()

            run = False

        # Compile the recorded frames into a video
        # if session_success:
        #     print('Compiling video, please wait...')
        #     makeVideo(file_name=session_name, image_folder=session_name, frame_rate=gui.get_avg_frame_rate())
        # If the session failed to connect, delete the frames that were saved and the folder containing them
        # elif os.path.exists(session_name):
        #     shutil.rmtree(session_name)


if __name__ == '__main__':
    main()
