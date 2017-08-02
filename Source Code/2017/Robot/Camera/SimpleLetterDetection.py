# Grayscale Binary Filter Example
import pyb, sensor, image, math, time

sensor.reset()
sensor.set_contrast(3)
sensor.set_gainceiling(2)
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking

GRAYSCALE_THRESHOLD = [(0, 40)]
high_threshold = (70, 255)

while(True):

    img = sensor.snapshot()
    #img.midpoint(1, bias=0.5)
    img.binary([high_threshold])

    blobs = img.find_blobs(GRAYSCALE_THRESHOLD, merge=True)

    if blobs:

        # Find the index of the blob with the mosta pixels.
        most_middle = 100000
        best_match = 0
        match_found = False

        img.draw_cross(170,120, color=(20,20,20))

        for i in range(len(blobs)):

            #img.draw_rectangle(blobs[i].rect(), color = (200,200,200))
            #img.draw_string(blobs[i].x() + 20,blobs[i].y() - 10,"ID: %i"%(i), color = (100,100,100))
            #img.draw_cross(blobs[i].cx(),blobs[i].cy(), color=(20,20,20))

            #print(math.floor(math.sqrt( math.pow(2, (blobs[i].cx() - 160) ) + math.pow(2 , (blobs[i].cy() - 120)))))
            distance = math.floor( math.sqrt( math.pow((blobs[i].cx() - 160),2 ) + math.pow((blobs[i].cy() - 120),2)))

            #print("ID: %i DistanceFrom: %i x: %i y: %i"%(i,distance,blobs[i].cx(),blobs[i].cy() ))

            if distance < most_middle: #and blobs[i].pixels() < 2300 and blobs[i].h() > blobs[i].w():
                most_middle = distance
                best_match = i
                match_found = True

        if blobs[best_match].pixels() > 150 and match_found:

            # Main Points of interest
            MidX = blobs[best_match].cx()
            BotY = blobs[best_match].y() + blobs[best_match].h()
            TopY = blobs[best_match].y()

            White2Black = 0
            BlackCount = 0
            lastWhite = True

            for Y in range(TopY,BotY,1):

                if img.get_pixel(MidX, Y) == 0 and lastWhite:
                    White2Black += 1
                    lastWhite = False

                elif img.get_pixel(MidX, Y) == 0:
                    BlackCount += 1

                elif img.get_pixel(MidX, Y) != 0:
                    lastWhite = True

            lastWhite = True


            if BlackCount > blobs[best_match].h()//2:
                White2Black = 10
                print("ERROR")

            img.draw_line((MidX,TopY,MidX,BotY),color = (150,150,150))
            img.draw_rectangle(blobs[best_match].rect(), color = (150,150,150))

            if White2Black == 3:
                img.draw_string(blobs[best_match].x(),blobs[best_match].y() - 10, "S",color = (150,150,150))
                print("SEEN: S")
            elif White2Black == 2:
                img.draw_string(blobs[best_match].x(),blobs[best_match].y() - 10, "U",color = (150,150,150))
                print("SEEN: U")
            elif White2Black == 1:
                img.draw_string(blobs[best_match].x(),blobs[best_match].y() - 10, "H",color = (150,150,150))
                print("SEEN: H")
            elif White2Black == 1:
                img.draw_string(blobs[best_match].x(),blobs[best_match].y() - 10, "INVALID",color = (150,150,150))
                print("SEEN: H")
            else:
                print("White To Black: %i"%(White2Black))


