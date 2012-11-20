#!/usr/bin/env python
# Written by Yu-Jie Lin
# Public Domain
#
# Deps: PyAudio, NumPy, and Matplotlib
# Blog: http://blog.yjl.im/2012/11/frequency-spectrum-of-sound-using.html

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import wave


TITLE = ''
FPS = 25.0

nFFT = 512
BUF_SIZE = 4 * nFFT
SAMPLE_SIZE = 2
CHANNELS = 2
RATE = 44100

def animate(i, line, wf, MAX_y):

  N = (int((i + 1) * RATE / FPS) - wf.tell()) / nFFT
  if not N:
    return line,
  N *= nFFT
  data = wf.readframes(N)
  print '{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
    100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes())

  # Unpack data, LRLRLR...
  y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / MAX_y
  y_L = y[::2]
  y_R = y[1::2]

  Y_L = np.fft.fft(y_L, nFFT)
  Y_R = np.fft.fft(y_R, nFFT)

  # Sewing FFT of two channels together, DC part uses right channel's
  Y = abs(np.hstack((Y_L[-nFFT/2:-1], Y_R[:nFFT/2])))

  line.set_ydata(Y)
  return line,


def init(line):

  # This data is a clear frame for animation
  line.set_ydata(np.zeros(nFFT - 1))
  return line,


def main():
  
  fig = plt.figure()

  # Frequency range
  x_f = 1.0 * np.arange(-nFFT / 2 + 1, nFFT / 2) / nFFT * RATE
  ax = fig.add_subplot(111, title=TITLE, xlim=(x_f[0], x_f[-1]),
                       ylim=(0, 2 * np.pi * nFFT**2 / RATE))
  ax.set_yscale('symlog', linthreshy=nFFT**0.5)

  line, = ax.plot(x_f, np.zeros(nFFT - 1))

  # Change x tick labels for left channel
  def change_xlabel(evt):
    labels = [label.get_text().replace(u'\u2212', '')
              for label in ax.get_xticklabels()]
    ax.set_xticklabels(labels)
    fig.canvas.mpl_disconnect(drawid)
  drawid = fig.canvas.mpl_connect('draw_event', change_xlabel)

  MAX_y = 2.0**(SAMPLE_SIZE * 8 - 1)
  wf = wave.open('temp.wav', 'rb')
  assert wf.getnchannels() == CHANNELS
  assert wf.getsampwidth() == SAMPLE_SIZE
  assert wf.getframerate() == RATE
  frames = wf.getnframes()

  ani = animation.FuncAnimation(fig, animate, int(frames / RATE * FPS),
      init_func=lambda: init(line), fargs=(line, wf, MAX_y),
      interval=1000.0/FPS, blit=True)
  ani.save('temp.mp4', fps=FPS)

  wf.close()


if __name__ == '__main__':
  main()
