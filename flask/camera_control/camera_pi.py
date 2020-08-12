''''
Line 28 - 96 are adapted from https://github.com/miguelgrinberg/flask-video-streaming

The MIT License (MIT)

Copyright (c) 2014 Miguel Grinberg lines

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import io
import threading
import time
import os
import picamera


def gen(camer):
    while True:
        frame = camer.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# camera.resolution=(1280, 720)
class Camera(object):
    global camera
    camera = picamera.PiCamera()
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    # camera = picamera.PiCamera()
    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        global camera
        # with picamera.PiCamera() as camera:
        # camera setup
        # camera.resolution = (320, 240)
        # camera.hflip = True
        # camera.vflip = True

        # let camera warm up
        camera.start_preview()
        time.sleep(2)

        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream,
                                             'jpeg',
                                             use_video_port=True):

            # camera.capture_continuous(stream, 'jpeg', use_video_port=True)# store frame
            stream.seek(0)
            cls.frame = stream.read()

            # reset stream for next frame
            stream.seek(0)
            stream.truncate()

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds stop the thread
            if time.time() - cls.last_access > 10:
                break
        cls.thread = None

    def rec(time, path_to_file):
        global camera
        print(path_to_file)
        dirpath = path_to_file.split('/')[:-1]
        dirpath = '/'.join(dirpath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        camera.start_recording(path_to_file)
        camera.wait_recording(time)
        camera.stop_recording()
        return
