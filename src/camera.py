import cv2
import time

class Camera:
    """API for Camera interface on Nvidia Jetson TX2 using OpenCV"""

    def __init__(self, height, width, fps=30):
        self.height = height
        self.width = width
        self.cap = None
        self.fps = fps

    def open_cam_rtsp(self, uri, latency):
        gst_str = ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
                   "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
                   "videoconvert ! appsink").format(uri, latency, self.width, self.height)
        self.cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            raise Exception("Could not open RSTP camera!")

        return True

    def open_cam_usb(self, dev):
        # We want to set width and height here, otherwise we could just do:
        #     return cv2.VideoCapture(dev)
        gst_str = ("v4l2src device=/dev/video{} ! "
                   "video/x-raw, width=(int){}, height=(int){}, format=(string)RGB ! "
                   "videorate !"
                   "video/x-raw,framerate={}/1 !"
                   "videoconvert ! appsink").format(dev, self.width, self.height, self.fps)
        self.cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)\

      # if not self.cap.isOpened():
      #      raise Exception("Could not open USB camera!")

        return True

    def open_window(self, windowName, title="Camera Demo for Jetson TX2/TX1"):
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowName, self.width, self.height)
        cv2.moveWindow(windowName, 0, 0)
        cv2.setWindowTitle(windowName, title)

    def capture_image(self, fileName=False, showImage=False, windowName="Nvidia Jetson Tx2"):
        capture_time = time.time()
        ret, frame = self.cap.read()
        print "Capture Time: ", time.time() - capture_time
        if showImage:
            show_image(frame, windowName)
        write_time = time.time()
        if fileName:
            cv2.imwrite(fileName, frame) 
        print "Write Time: ", time.time() - write_time
        return frame

    def show_image(self, frame, windowName):
        showHelp = True
        showFullScreen = False
        helpText = "'Esc' to Quit, 'H' to Toggle Help, 'F' to Toggle Fullscreen"
        font = cv2.FONT_HERSHEY_PLAIN
        start_time = time.time()
        while (time.time() - start_time < 1):
            if cv2.getWindowProperty(windowName, 0) < 0: # Check to see if the user closed the window
                break                                     # This will fail if the user closed the window; Nasties get printed to the console
            if showHelp == True:
                cv2.putText(frame, helpText, (11,20), font, 1.0, (32,32,32), 4, cv2.LINE_AA)
                cv2.putText(frame, helpText, (10,20), font, 1.0, (240,240,240), 1, cv2.LINE_AA)
            cv2.imshow(windowName, frame)
            key = cv2.waitKey(10)
            if key == 27: # ESC key: quit program
                break
            elif key == ord('H') or key == ord('h'): # toggle help message
                showHelp = not showHelp
            elif key == ord('F') or key == ord('f'): # toggle fullscreen
                showFullScreen = not showFullScreen
                
            if showFullScreen:
                cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
               cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)


    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

        cv2.destroyAllWindows()


    def __del__(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

        cv2.destroyAllWindows()
