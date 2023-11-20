#!/usr/bin/env python3

from struct import pack, unpack     # Usefull to play with bytes
import socket                       # UDP
import time                         # sleep function
from datetime import datetime       # get the current time (FPS calculation)
from sys import stdout              # for the spining indicator
import argparse                     # for the command line arguments

# For rgb to xterm256 color matching:
from colormath.color_conversions import convert_color
from colormath.color_objects import (
    LabColor,
    sRGBColor,
)
import math

# Some Artnet stuffs
ARTNET_PHYSICAL = 0         # 0 as default value is fine
ARTNET_DESCRIPTOR_HEADER = b'Art-Net\x00'          # Art-Net
ARTNET_DESCRIPTOR_HEADER += pack('<H', 0x5000)     # OpCode: ArtDMX (0x5000)
ARTNET_DESCRIPTOR_HEADER += pack('>H', 14)         # ProtVer: 14

# Nothing very important here
VERBOSE=0                   # verbose level
INDICATOR = '/-\|'          # spining indicator chars

# Showing frame stuffs
BOX = '\u2586\u2586 '       # LOWER THREE QUARTERS BLOCK, LOWER THREE QUARTERS BLOCK, SPACE
DOT = '\u2b24 '             # BLACK LARGE CIRCLE, SPACE
PRINTCHAR = DOT             # By default use dot

XTERM256RGB = [ # xterm256 color look-up table (xterm256 index to RGB24)
                # Primary 3-bit (8 colors).
                0x000000,
                0x800000,
                0x008000,
                0x808000,
                0x000080,
                0x800080,
                0x008080,

                # Equivalent "bright" versions of original 8 colors.
                0xc0c0c0,
                0x808080,
                0xff0000,
                0x00ff00,
                0xffff00,
                0x0000ff,
                0xff00ff,
                0x00ffff,

                # Strictly ascending.
                0xffffff,
                0x000000,
                0x00005f,
                0x000087,
                0x0000af,
                0x0000d7,
                0x0000ff,
                0x005f00,
                0x005f5f,
                0x005f87,
                0x005faf,
                0x005fd7,
                0x005fff,
                0x008700,
                0x00875f,
                0x008787,
                0x0087af,
                0x0087d7,
                0x0087ff,
                0x00af00,
                0x00af5f,
                0x00af87,
                0x00afaf,
                0x00afd7,
                0x00afff,
                0x00d700,
                0x00d75f,
                0x00d787,
                0x00d7af,
                0x00d7d7,
                0x00d7ff,
                0x00ff00,
                0x00ff5f,
                0x00ff87,
                0x00ffaf,
                0x00ffd7,
                0x00ffff,
                0x5f0000,
                0x5f005f,
                0x5f0087,
                0x5f00af,
                0x5f00d7,
                0x5f00ff,
                0x5f5f00,
                0x5f5f5f,
                0x5f5f87,
                0x5f5faf,
                0x5f5fd7,
                0x5f5fff,
                0x5f8700,
                0x5f875f,
                0x5f8787,
                0x5f87af,
                0x5f87d7,
                0x5f87ff,
                0x5faf00,
                0x5faf5f,
                0x5faf87,
                0x5fafaf,
                0x5fafd7,
                0x5fafff,
                0x5fd700,
                0x5fd75f,
                0x5fd787,
                0x5fd7af,
                0x5fd7d7,
                0x5fd7ff,
                0x5fff00,
                0x5fff5f,
                0x5fff87,
                0x5fffaf,
                0x5fffd7,
                0x5fffff,
                0x870000,
                0x87005f,
                0x870087,
                0x8700af,
                0x8700d7,
                0x8700ff,
                0x875f00,
                0x875f5f,
                0x875f87,
                0x875faf,
                0x875fd7,
                0x875fff,
                0x878700,
                0x87875f,
                0x878787,
                0x8787af,
                0x8787d7,
                0x8787ff,
                0x87af00,
                0x87af5f,
                0x87af87,
                0x87afaf,
                0x87afd7,
                0x87afff,
                0x87d700,
                0x87d75f,
                0x87d787,
                0x87d7af,
                0x87d7d7,
                0x87d7ff,
                0x87ff00,
                0x87ff5f,
                0x87ff87,
                0x87ffaf,
                0x87ffd7,
                0x87ffff,
                0xaf0000,
                0xaf005f,
                0xaf0087,
                0xaf00af,
                0xaf00d7,
                0xaf00ff,
                0xaf5f00,
                0xaf5f5f,
                0xaf5f87,
                0xaf5faf,
                0xaf5fd7,
                0xaf5fff,
                0xaf8700,
                0xaf875f,
                0xaf8787,
                0xaf87af,
                0xaf87d7,
                0xaf87ff,
                0xafaf00,
                0xafaf5f,
                0xafaf87,
                0xafafaf,
                0xafafd7,
                0xafafff,
                0xafd700,
                0xafd75f,
                0xafd787,
                0xafd7af,
                0xafd7d7,
                0xafd7ff,
                0xafff00,
                0xafff5f,
                0xafff87,
                0xafffaf,
                0xafffd7,
                0xafffff,
                0xd70000,
                0xd7005f,
                0xd70087,
                0xd700af,
                0xd700d7,
                0xd700ff,
                0xd75f00,
                0xd75f5f,
                0xd75f87,
                0xd75faf,
                0xd75fd7,
                0xd75fff,
                0xd78700,
                0xd7875f,
                0xd78787,
                0xd787af,
                0xd787d7,
                0xd787ff,
                0xd7af00,
                0xd7af5f,
                0xd7af87,
                0xd7afaf,
                0xd7afd7,
                0xd7afff,
                0xd7d700,
                0xd7d75f,
                0xd7d787,
                0xd7d7af,
                0xd7d7d7,
                0xd7d7ff,
                0xd7ff00,
                0xd7ff5f,
                0xd7ff87,
                0xd7ffaf,
                0xd7ffd7,
                0xd7ffff,
                0xff0000,
                0xff005f,
                0xff0087,
                0xff00af,
                0xff00d7,
                0xff00ff,
                0xff5f00,
                0xff5f5f,
                0xff5f87,
                0xff5faf,
                0xff5fd7,
                0xff5fff,
                0xff8700,
                0xff875f,
                0xff8787,
                0xff87af,
                0xff87d7,
                0xff87ff,
                0xffaf00,
                0xffaf5f,
                0xffaf87,
                0xffafaf,
                0xffafd7,
                0xffafff,
                0xffd700,
                0xffd75f,
                0xffd787,
                0xffd7af,
                0xffd7d7,
                0xffd7ff,
                0xffff00,
                0xffff5f,
                0xffff87,
                0xffffaf,
                0xffffd7,
                0xffffff,

                # Gray-scale range.
                0x080808,
                0x121212,
                0x1c1c1c,
                0x262626,
                0x303030,
                0x3a3a3a,
                0x444444,
                0x4e4e4e,
                0x585858,
                0x626262,
                0x6c6c6c,
                0x767676,
                0x808080,
                0x8a8a8a,
                0x949494,
                0x9e9e9e,
                0xa8a8a8,
                0xb2b2b2,
                0xbcbcbc,
                0xc6c6c6,
                0xd0d0d0,
                0xdadada,
                0xe4e4e4,
                0xeeeeee]

def rgb2lab(rgb):
    # Convert rgb color to lab color representation
    # input: rgb 24bits value (eg 0x12cafe)
    # output: lab color tuple (l,a,b)

    b = rgb & 0xff
    rgb = rgb >> 8
    g = rgb & 0xff
    rgb = rgb >> 8
    r = rgb & 0xff
    lab = convert_color(sRGBColor(r, g, b),LabColor)
    return (lab.lab_l,lab.lab_a,lab.lab_b)

# Build xterm256 colors lab look-up table
XTERM256LAB = list( map(lambda rgb: rgb2lab(rgb),
                    XTERM256RGB))

# Already calculated correspondance look-up hashtable
FAST_RGB2XTERM256 = dict()  

def distance(xyz1,xyz2):
    # Calculate the distance between two xyz coordinates
    # input: pair of (x,y,z) tuples
    # output: distance

    return math.sqrt(   math.pow((xyz1[0]-xyz2[0]),2) +
                        math.pow((xyz1[1]-xyz2[1]),2) +
                        math.pow((xyz1[2]-xyz2[2]),2))

def rgb2xterm256_lab(r,g,b):
    # Find best matching xterm256 color using distance in lab representation
    # input: r, g, b int values
    # output: xterm256 color index
    
    # Calculate rgb 24bits value for hashtable lookup
    rgb = r
    rgb = rgb << 8
    rgb += g
    rgb = rgb << 8
    rgb += b
    
    # If rgb is in the hashtable return the already calcultate xterm256 index
    if rgb in FAST_RGB2XTERM256.keys():
        return FAST_RGB2XTERM256[rgb]
    
    i = 0
    
    # Convert rgb color to look to lab representation
    srgb = sRGBColor(r, g, b)
    lab = convert_color(srgb,LabColor)
    lab1 = (lab.lab_l,lab.lab_a,lab.lab_b)

    # Peek the first xterm256 color lab representation 
    lab2 = XTERM256LAB[0]
    min_distance = distance(lab1,lab2)
    best_match = i
    i = 1

    # Find the best matching xterm256color (minimal distance)
    while min_distance > 0 and i < len(XTERM256LAB):

        lab2 = XTERM256LAB[i]
        cur_distance = distance(lab1,lab2)

        if cur_distance < min_distance:
            min_distance = cur_distance
            best_match = i

        i += 1
    
    # Add the found xterm256 color to the hastable
    FAST_RGB2XTERM256[rgb] = best_match

    return best_match

def verbose_1(msg):
    # Verbose level 1 printing
    if VERBOSE > 0:
        print('\033[38;5;230m' + msg)

def verbose_2(msg):
    # Verbose level 2 printing
    if VERBOSE > 1:
        print('\033[38;5;230m' + msg)

def verbose_3(msg):
    # Verbose level 3 printing
    if VERBOSE > 2:
        print('\033[38;5;230m' + msg)

def frame2ascii(frame,width=0,height=0):
    # Convert a frame to ascii printable text
    # input: frame as raw rgb pixel values
    # ouput: the frame as printable colored text

    ascii = ''
    if width == 0 or height ==0:
        width = int(math.sqrt(len(frame)/3))     # we assume it is a square
        height = width
    
    # For each frame line
    for y in range(height):
        # For each column
        for x in range(width):

            # Calculate the current rgb triplet pointer
            index = y*3*width + 3*x
            # Get the r,g,b values
            r = int(frame[ index ])
            g = int(frame[ index + 1 ])
            b = int(frame[ index + 2 ])

            # Convert RGB24 to xterm256 indexed color
            color = rgb2xterm256_lab(r,g,b)

            # Append pixel as a colored char (dot or square)
            ascii += ('\033[38;5;%sm%s' % (color, PRINTCHAR))

        ascii += '\n'

    return ascii

def main():
    global VERBOSE
    global PRINTCHAR

    parser = argparse.ArgumentParser(
                    prog='arnetplay.py',
                    description='Send raw images using Artnet protocol',
                    epilog='Made with \u2665 in Python')
    
    parser.add_argument('-v','--verbose',action='count',default=0,help='Verbose level')
    parser.add_argument('-W','--width',type=int,default=16,help='Frame width in pixels')
    parser.add_argument('-H','--height',type=int,default=16,help='Frame height in pixels')
    parser.add_argument('-d','--destination',default='127.0.0.1',help='IP destination address (default 127.0.0.1)')
    parser.add_argument('-p','--port',type=int,default=6454,help='UDP destination port (default 6454)')
    parser.add_argument('-f','--fps',type=int,default=5,help='Frame Per Second (default 5)')
    parser.add_argument('-r','--repeat',type=int,default=0,help='UDP packet repeat (default none)')
    parser.add_argument('-L','--loop',type=int,default=0,help='Number of loop to play (infinite loop by default)')
    parser.add_argument('-s','--show',action='count',default=0,help='Show frames')
    parser.add_argument('-b','--box',action='count',default=0,help='Use boxes instead of dots when showing frames')
    parser.add_argument('filepath',nargs='+',help='Raw image (rgb24) filepath')

    args = parser.parse_args()

    VERBOSE = args.verbose

    if args.box > 0:
        PRINTCHAR = BOX

    # Open UDP socket
    udpclient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      # UDP

    if int(args.destination.split('.')[3]) == 255:
        udpclient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   # Allow multicast

    # load frames from files
    frames = []
    asciiframes = []

    for filepath in args.filepath:
        with open(filepath,'rb') as file:
            
            # Load file content
            frame = file.read()

            # Append file content to frames table
            frames.append(frame)

            # Also compute ascii frame if needed
            if args.show > 0:
                asciiframes.append(frame2ascii(frame,args.width,args.height))

    # First frame will use sequence 0
    sequence = 0

    # use for spining indicator
    i = 0

    # number of loop of the frame to do
    loop = args.loop

    verbose_1('=' * 80)

    # Forever loop
    while True:

        loop -= 1   # with loop set to 0 from start it results in infinite loop

        # For each frame loaded in the frames table
        for f in range(len(frames)):

            # Store start time (used for FPS)
            start = datetime.now()

            if VERBOSE == 0 and args.show == 0:
                stdout.write('\rSending frames %s' % INDICATOR[i])
                i = (i + 1) % len(INDICATOR)

            # First Artnet payload for a frame is in universe 0
            universe = 0
            
            # Get the frame size
            remaining_bytes = len(frames[f])

            verbose_1('* Processing frame %d, %d bytes to send' % (f, remaining_bytes))
            if args.show > 0:
                print(asciiframes[f])

            # While data needs to be sent for the current frame
            while remaining_bytes > 0:

                verbose_1('+' + '-' * 79)
                verbose_2('+ %d bytes remaining to send' % remaining_bytes)

                # Prepare up to 170 RGB values to send (510 bytes, maximum in DMX512)
                index = universe * 510
                rgbvalues = frames[f][index: index + 510]
            
                # Build the artnet payload
                data = ARTNET_DESCRIPTOR_HEADER                     # Pack header first
                data += pack('>B',sequence)                         # Pack the sequence index
                data += pack('>B',ARTNET_PHYSICAL)                  # Pack the artnet physical
                data += pack('<H',universe)                         # Pack the universe index
                data += pack('>H',len(rgbvalues))                   # Pack the artnet payload length
                data += pack('>%sB' % len(rgbvalues), *rgbvalues)   # Pack the payload

                verbose_1('+ Sequence: %d, universe: %d, DMX: %d bytes, UDP payload: %d bytes' % (sequence,universe,len(rgbvalues),len(data)))
                verbose_3('-----BEGIN PAYLOAD-----')
                verbose_3(data.hex())
                verbose_3('-----END PAYLOAD-----')
                verbose_2('+ Sending UDP packet with %d bytes' % len(data))

                # Send the artnet data in UDP packet
                udpclient.sendto(data,(args.destination,args.port))

                # When requested resend the UDP packet
                # May be usefull in case of bad network quality
                for repeat in range(args.repeat):
                    verbose_2('+ Sending again UDP packet (repeat %d)' % repeat)
                    udpclient.sendto(data,(args.destination,args.port))

                # Increment universe index for the remaining bytes to be send in other
                # Artnet packet with the same sequence index
                universe = (universe + 1) % 65536

                # Calculate the remaining bytes to send
                remaining_bytes -= 510
            
            verbose_1('+' + '-' * 79)

            # Increment sequence index for next frame
            sequence = (sequence + 1) % 256

            # Evaluate the elapsed time since the computing has started
            # for the current frame
            duration = (datetime.now() - start).microseconds/1000000

            verbose_2('+ Processing frame %d took %f seconds' % (f,duration))

            # Calculate the wait time needed to achieve the requested FPS
            wait = 1/int(args.fps) - duration
            verbose_2('+ Will wait %f seconds' % wait)

            # If we're not to late we will need to wait
            if wait > 0:
                time.sleep(wait)
            
            verbose_1('=' * 80)

        # Stop when the number of loop has been done 
        # Note: infinite loop will never branch in here (loop < 0)
        if loop == 0:   
            break

if __name__ == '__main__':
    main()