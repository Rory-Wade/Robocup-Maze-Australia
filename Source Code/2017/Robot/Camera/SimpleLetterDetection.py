# Smart Letter Detection Version 2
import sensor, image, time, math

from pyb import LED,UART,Pin,Servo

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QCIF)
sensor.skip_frames(30)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

ImageX = 80
ImageY = 70

sensor.set_windowing((80, 30, ImageX, ImageY))

high_threshold = (0, 60)
thresholds = (0, 120)

centX = ImageX // 2
centY = ImageY // 2

uart = UART(3, 19200, timeout_char=10)

Servo(2).pulse_width(1800)

global best_match

while(True):
    img = sensor.snapshot()

    img.binary([high_threshold])
    img.dilate(2)
    img.binary([high_threshold])

    most_middle = 10000
    match_found = False
    White2Black = 0

    for blob in img.find_blobs([thresholds], pixels_threshold=50, area_threshold=10, merge=False):

        # touch side break
        if blob.x() == 0 or blob.y() == 0 or blob.y() + blob.h() >= ImageY - 1 or blob.x() + blob.w() >= ImageX - 1:
            continue

        distance = math.floor( math.sqrt( math.pow((blob.cx() - centX),2 ) + math.pow((blob.cy() - centY),2)))

        if distance < most_middle and blob.pixels() < 3000 and blob.pixels() > 10:
            most_middle = distance
            best_match = blob
            match_found = True

    if match_found:

        MidY = best_match.cy()
        BotX = best_match.x() + best_match.w()
        TopX = best_match.x()

        BlackCount = 0
        lastWhite = True

        for X in range(TopX,BotX,1):

            if img.get_pixel(X, MidY) == 0 and lastWhite:
                White2Black += 1
                lastWhite = False

            elif img.get_pixel(X, MidY) == 0:
                BlackCount += 1

            elif img.get_pixel(X, MidY) != 0:
                lastWhite = True

        if(img.get_pixel(TopX + 1, MidY) == 0 and White2Black == 1):
            White2Black += 1
            print(BlackCount)

        img.draw_line( (TopX,MidY,BotX,MidY),color = (150,150,150))
        lastWhite = True

    LED(1).off()
    LED(2).off()
    LED(3).off()

    print(White2Black)

    if White2Black == 3:
        uart.write("C:S\n")
        LED(1).on()

    elif White2Black == 2:
        uart.write("C:U\n")
        LED(2).on()

    elif White2Black == 1:
        uart.write("C:H\n")
        LED(3).on()

    if uart.any() > 0:
        line = uart.readline()
        print(line)
        if b"D1" in line:
            Servo(2).pulse_width(1200)
            time.sleep(500)
            Servo(2).pulse_width(1800)
            uart.write("C:OK2")

    match_found = False
