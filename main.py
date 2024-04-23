from scanGUI import ScanGUI
import datetime, cv2, os


# If set to True, will attempt to connect to localhost instead of external camera system
TEST = True
SAVE_FRAME_RATE = 4     # Frame rate to save animated frames for later viewing. Will not save if set to 0 or negative.


def makeVideo(name, image_folder):

    images = [img for img in sorted(os.listdir(image_folder)) if img.endswith('.jpg')]
    if len(images) < 1:
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(name + '.mp4', fourcc, SAVE_FRAME_RATE, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    video.release()


def main():
    # Get a unique name for the recording of the session
    session_name = 'animation_' + datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')

    gui = ScanGUI(test=TEST, save_frame_rate=SAVE_FRAME_RATE, session_name=session_name)
    try:
        gui.run()
    except ConnectionRefusedError as e:
        print('Server not found, trying again...')
        return True
    except ConnectionResetError as e:
        print('Connection reset by server')

        gui.shutdown()

    print('Compiling video, please wait...')
    makeVideo(name=session_name, image_folder=session_name)



if __name__ == '__main__':
    run = True

    while run:
        run = main()
