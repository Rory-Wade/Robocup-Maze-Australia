# Grayscale Binary Filter Example
#

import pyb, sensor, image, math, time
from pyb import LED

sensor.reset()
sensor.set_contrast(3)
sensor.set_gainceiling(2)
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking

LED(4).on()

GRAYSCALE_THRESHOLD = [(0, 40)]
high_threshold = (40, 255)

clock = time.clock()
while(True):
    clock.tick()

    img = sensor.snapshot()
    #img.midpoint(1, bias=0.1)
    img.binary([high_threshold])

    blobs = img.find_blobs(GRAYSCALE_THRESHOLD, merge=True)

    if blobs:

        # Find the index of the blob with the mosta pixels.
        most_pixels = 0
        largest_blob = 0

        for i in range(len(blobs)):
            #img.draw_rectangle(blobs[i].rect(), color = (10,10,10))
            if blobs[i].pixels() > most_pixels and blobs[i].pixels() < 2300 and blobs[i].h() < 90 and blobs[i].w() < 70 and blobs[i].h() > blobs[i].w():
                most_pixels = blobs[i].pixels()
                largest_blob = i


        if most_pixels > 250:
            # Main Points of interest
            MidX = blobs[largest_blob].x() + (blobs[largest_blob].w()//2)
            BotY = blobs[largest_blob].y() + blobs[largest_blob].h()
            TopY = blobs[largest_blob].y()

            White2Black = 0
            lastWhite = True

            for Y in range(TopY,BotY,1):

                if img.get_pixel(MidX, Y) == 0 and lastWhite:
                    White2Black += 1
                    lastWhite = False

                elif img.get_pixel(MidX, Y) != 0:
                    lastWhite = True

            img.draw_line((MidX,TopY,MidX,BotY),color = (150,150,150))
            img.draw_rectangle(blobs[largest_blob].rect(), color = (150,150,150))

            if White2Black == 3:
                img.draw_string(blobs[largest_blob].x(),blobs[largest_blob].y() - 10, "S",color = (150,150,150))
                print("SEEN: S")
            elif White2Black == 2:
                img.draw_string(blobs[largest_blob].x(),blobs[largest_blob].y() - 10, "C",color = (150,150,150))
                print("SEEN: C")
            elif White2Black == 1:
                img.draw_string(blobs[largest_blob].x(),blobs[largest_blob].y() - 10, "H",color = (150,150,150))
                print("SEEN: H")

    img.draw_string(0, 0, "FPS:%.2f"%(clock.fps()),color = (150,150,150))
