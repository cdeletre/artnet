# artnet
Artnet stuffs (ws2812, led matrix, dmx512)

    ./artnetsend.py -h
    usage: arnetplay [-h] [-v] [-d DESTINATION] [-p PORT] [-f FPS] [-r REPEAT] [-l LOOP] [-s] [-b] filepath [filepath ...]

    Send raw images using Artnet protocol

    positional arguments:
    filepath              Raw image (rgb24) filepath

    options:
    -h, --help            show this help message and exit
    -v, --verbose         Verbose level
    -d DESTINATION, --destination DESTINATION
                            IP destination address
    -p PORT, --port PORT  UDP destination port
    -f FPS, --fps FPS     Frame Per Second
    -r REPEAT, --repeat REPEAT
                            UDP packet repeat
    -l LOOP, --loop LOOP  Number of loop to play
    -s, --show            Show frames
    -b, --box             Use boxes instead of dots when showing frames

    Made with ♥ in Python
