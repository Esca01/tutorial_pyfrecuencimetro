#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Proyecto: Monitor de frecuencia fundamental  ---> aplicado como afinador (tuner) de instrumentos o voz (Vocal pitch monitor)  

Asumimos que sabemos numeros midis de cuerdas de Guitara (Afinacion MI)
   MIDI  frec
E4 64   1ra cuerda (abajo)
B3 59
G3 55
D3 50
A2 45
E2 40   6ta cuerda (arriba)

Para voz
C4 60
..+12 semitonos
C3 48
"""


#usaremos su funcion GetFdato()  que nos brindara la frecuencia (Hz)

"""
#nuesta version: https://github.com/educarte_pro/afinador.git
#basado en:      https://github.com/michniewicz/python-tuner 
Mas informacion:
MIDI numeros:
http://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
https://newt.phys.unsw.edu.au/jw/notes.html (teoria)    (indicamos en la pagweb de github y youtube)
http://musiki.org.ar/Escala_logar%C3%ADtmica_de_frecuencia   (Escala logarítmica de frecuencia - base 2)
PEND:    (FFT)
"""

"""
C1: colocamos las librerias y  
"""
 #archivo afinador2.py   usaremos su funcion GetFdato()  que nos brindara la frecuencia (Hz)

import numpy as np
import pyaudio
from time import time    #T0: para calcular tiempo de cada iteracion

# Definimos las notas minimas donde trabajeremos: en este caso como queremos afinar una guitarra 
#Numero MIDI (abreviatura de Musical Instrument Digital Interface)
NOTE_MIN = 40       # E2  6ta cuerda entre E2 y E4 hay 24 semitonos  PEND: hacer video sobre eso
NOTE_MAX = 64       # E4  1
FSAMP = 22050       # Sampling frequency in Hz  -- T=0,000045351
FRAME_SIZE = 2048   # samples per frame         -- T=0,000488281
FRAMES_PER_FFT = 16  # FFT takes average across how many frames?   -- cantidad de frames analizads por la FFT (transformada rapida de fourier)

#variables globales para compartir con otros files.py
varPub = 10
numeroMIDI, frecHz, notaProxima, distNotaProxima = 0, 0, 0, 0
#ResMidi, ResFrec, ResNota, ResDist = 1 , 2 , 3 , 4

######################################################################
# Derived quantities from constants above. Note that as
# SAMPLES_PER_FFT goes up, the frequency step size decreases (sof
# resolution increases); however, it will incur more delay to process
# new sounds.

SAMPLES_PER_FFT = FRAME_SIZE * FRAMES_PER_FFT
FREQ_STEP = float(FSAMP) / SAMPLES_PER_FFT

######################################################################
# For printing out notes

#NOTE_NAMES = 'E F F# G G# A A# B C C# D D#'.split()
NOTE_NAMES = 'Mi Fa Fa# Sol Sol# La La# Si Do Do# Re Re#'.split()

######################################################################
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html

def freq_to_number(f): return 64 + 12 * np.log2(f / 329.63)


def number_to_freq(n): return 329.63 * 2.0**((n - 64) / 12.0)


def note_name(n):
    return NOTE_NAMES[n % NOTE_MIN % len(NOTE_NAMES)] + str(int(n / 12 - 1))

######################################################################
# Ok, ready to go now.

# Get min/max index within FFT of notes we care about.
# See docs for numpy.rfftfreq()


def note_to_fftbin(n): return number_to_freq(n) / FREQ_STEP


imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN - 1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX + 1))))

# Allocate space to run an FFT.
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

# Initialize audio
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)  #PEND: este de la frecuencia de transmision??????

stream.start_stream()

# Create Hanning window function
window = 0.5 * (1 - np.cos(np.linspace(0, 2 * np.pi, SAMPLES_PER_FFT, False)))

# Print initial text
print('sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')
print()


def PublicaNota():	
    while stream.is_active():   #T0: ojo: Hemos calculado que el tiempo de cada iteracion es 0.1431541443 seg  osea 6.98 Hz de frec 
          
        start_time = time()    #T0: para calcular tiempo de cada iteracion

	    # Shift the buffer down and new data in
        buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
        buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)

	    # Run the FFT on the windowed buffer
        fft = np.fft.rfft(buf * window)

	    # Get frequency of maximum response in range
        freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

	    # Get note number and nearest note  //NOTA REAL
        n = freq_to_number(freq)
        n0 = int(round(n))

	    # Console output once we have a full buffer
        global num_frames  #declara  a num_frames como variable global para poder utilizarla fuera del while() y de la funcion "PublicaNota()"
        num_frames += 1

	#Resultado
        global numeroMIDI, frecHz, notaProxima, distNotaProxima
        numeroMIDI, frecHz, notaProxima, distNotaProxima =  n, freq, note_name(n0), (n-n0)
        #global ResMidi, ResFrec, ResNota, ResDist
        #ResMidi, ResFrec, ResNota, ResDist =  n, freq, note_name(n0), (n-n0)
	
        if num_frames >= FRAMES_PER_FFT:    #   Despues de 16 frames analizados por FFT se mostrara la nota
            print('Num MIDI {:7.2f} Frec: {:7.2f} Hz     Nota prox: {:>3s} {:+.2f}'.format( numeroMIDI, frecHz, notaProxima, distNotaProxima ))
	
        global varPub #variable enviada
        varPub = numeroMIDI
        #print("Varible publicada: %s" % str(varPub) )

        #return numeroMIDI, frecHz, notaProxima, distNotaProxima  #PEND: No avanza el programa si se activa RETURN por eso debemos trabajar con variable sglobales commo "varPub"

        elapsed_time = time() - start_time                     #T0: para calcular tiempo de cada iteracion
        print("Elapsed time: %0.10f seconds." % elapsed_time)  #T0: para calcular tiempo de cada iteracion:  media  0.1431541443 seg  osea 6.98 Hz de frec

if __name__ == '__main__':   #se ejecuta solo se llama desde este file
        PublicaNota()

