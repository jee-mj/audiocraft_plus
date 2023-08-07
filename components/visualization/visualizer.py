from os import path
from audio2numpy import open_audio
import numpy as np

channel = "avarage"
framerate = 30
duration = framerate/1000
bins = 64
xlog = 0
ylog = 0

def load_audio(audio_file):
    if not path.exists(audio_file):
        raise FileNotFoundError("Audio file does not exist")
    else:
        waveform, sample_rate = open_audio(audio_file)
        return waveform, sample_rate

def calculate_frameData(fileData, samplerate):
    channels = []
    channel = "avarage"

    if len(fileData.shape) > 1:
        if channel == "avarage":
            channels.append(np.mean(fileData, axis=1))
        elif channel == "left":
            channels.append(fileData[:,0])
        elif channel == "right":
            channels.append(fileData[:,1])
        else:
            for i in range(fileData.shape[1]):
                channels.append(fileData[:,i])
    else:
        channels.append(fileData)
    
    frameData = []
    for channel in channels:

        channelData = channel

        channelFrameData = []
        stepSize = samplerate/framerate
        for i in range(int(np.ceil(len(channelData)/stepSize))):
            frameDataMidpoint = stepSize*i + (stepSize/2)
            frameDataStart = int(frameDataMidpoint - (duration/1000/2)*samplerate)
            frameDataEnd = int(frameDataMidpoint + (duration/1000/2)*samplerate)

            if frameDataStart < 0:
                emptyFrame = np.zeros(int(duration/1000 * samplerate))
                currentFrameData = channelData[0:frameDataEnd]
                emptyFrame[0:len(currentFrameData)] = currentFrameData
                currentFrameData = emptyFrame
            elif frameDataEnd > len(channelData):
                emptyFrame = np.zeros(int(duration/1000 * samplerate))
                currentFrameData = channelData[frameDataStart:]
                emptyFrame[0:len(currentFrameData)] = currentFrameData
                currentFrameData = emptyFrame
            else:
                currentFrameData = channelData[int(frameDataStart):int(frameDataEnd)]

            frameDataAmplitudes = abs(np.fft.rfft(currentFrameData))

            frameDataAmplitudes = frameDataAmplitudes[int(0/(samplerate/2)*len(frameDataAmplitudes)):int((samplerate/2)/(samplerate/2)*len(frameDataAmplitudes))]

            channelFrameData.append(frameDataAmplitudes)

        frameData.append(channelFrameData)

    return frameData

def create_bins(frameData):
    bins = []
    for channel in frameData:
        channelBins = []
        for data in channel:
            frameBins = []
            for i in range(bins):
                if xlog == 0:
                    dataStart = int(i * len(data) / bins)
                    dataEnd = int((i + 1) * len(data) / bins)
                else:
                    dataStart = int((i/bins)**xlog * len(data))
                    dataEnd = int(((i+1)/bins)**xlog * len(data))
                if dataStart == dataEnd:
                    dataEnd += 1
                frameBins.append(np.mean(data[dataStart:dataEnd]))
            channelBins.append(frameBins)
        
        bins.append(channelBins)

    return bins