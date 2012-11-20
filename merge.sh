#!/bin/bash

ffmpeg -i temp.mp4 -i temp.wav -vcodec copy -acodec libmp3lame sound-spectrum.mp4
