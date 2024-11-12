from gtts import gTTS
import os
import playsound

# the voiceline when open, close, turn off
OPEN = "The curtain is opened"
CLOSE = "The curtain is closed"
OFF = "The curtain is turning off"
# add more voicelines here...

# language 
LANG = "en"

# enabling of the TTS system
ENA = False

# a cloud based TTS function
def speak(phrase):
    # Create gTTS object
    tts = gTTS(text=phrase, lang=LANG, slow=False)
    
    # Save the speech to a temporary file
    temp_file = 'temp_audio.mp3'
    tts.save(temp_file)
    
    # Play the saved audio file
    playsound.playsound(temp_file)
    
    # Optionally, remove the temporary file after playback
    os.remove(temp_file)

if __name__ == "__main__":
    speak(input())
