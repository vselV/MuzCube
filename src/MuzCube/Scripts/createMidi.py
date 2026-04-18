from src.MuzCube.FirstVersion import toMidiMeth, toMidGa
from src.MuzCube.Scripts import allMidiFrom
import src.MuzCube.FirstVersion.toMidiMeth, src.MuzCube.FirstVersion.toMidGa
from midiutil import MIDIFile
def create(mypath):
    files= allMidiFrom.allMidi(mypath)
    MyMIDI = MIDIFile(len(files),False,False,False,1)
    for i in range (len(files)):
        toMidiMeth.toMidi(mypath+"/"+files[i],i,MyMIDI)
    with open(mypath+"/midi/" +"general.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)
def fullPack(mypath):
    create(mypath)
    #play(mypath)
    #AudioPlayer(mypath+"/wav/general.wav").play(block=True,loop=False)
    toMidGa.start(mypath+"/midi/general.mid")