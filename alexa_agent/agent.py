from alexa_client import AlexaClient
from simple_tts import tts
import os
import subprocess
import shlex


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
AUDIO_DIR = BASE_DIR + '/audio'


class AlexaAgent(object):
    def __init__(self):
        print "Hello" + AUDIO_DIR
	self.audio_dir = AUDIO_DIR        
    
    def wakeup(self):
        print self.audio_dir
	self.play_mp3("{}/wakeup.mp3".format(self.audio_dir))

    def say(self, input):
        """Alexa will say the text.
        
        @param: input: Text you want Alexa to say.
        @type: input: str or list of str
        """
        if isinstance(input, list):
            self.send_to_alexa(
                text="Simon says, {}".format(input[0]),
                addl_text_list=["Simon says, {}".format(t) for t in input[1:]]
            )
        else:
            self.send_to_alexa(text=input)

    def ask(self, user_id, input):
        """Ask Alexa to do something(s).
        
        @param: input: Text command you want to send to Alexa.
        @type: input: str or list of str
        """
        if isinstance(input, list):
            self.send_to_alexa(user_id,
                text=input[0],
                addl_text_list=input[1:]
            )
        else:
            self.send_to_alexa(user_id, text=input)
    
    def send_to_alexa(self, user_id, text, addl_text_list=[], no_play=False):
        """Send text to Alexa. If addl_text_list is provided, all the text
        commands will be sent concurrently and responses played back in order.

        @param: text: Text command to send to Alexa.
        @type: text: str

        @param: addl_text_list: List of additional text commands to send.
        @type: addl_text_list: list
        """
        alexa = AlexaClient()
        text_list = [text] + addl_text_list
        input_list = [tts(t) for t in text_list]
        output_list = alexa.ask(user_id, input_list[0])

        if no_play:
            return output_list
        if len(output_list) > 1:
            self.speech_to_text(output_list)
        else:
            self.speech_to_text(output_list)
        alexa.clean()

    def speech_to_text(self, filename):
	import speech_recognition as sr

	# obtain path to "english.wav" in the same folder as this script
	from os import path

	print("STT: " + filename)
	wav_file = filename + ".wav"
	from pydub import AudioSegment
	AudioSegment.from_mp3(filename).export(wav_file, format="wav")
	
	# use the audio file as the audio source
	r = sr.Recognizer()
	with sr.AudioFile(wav_file) as source:
    	    audio = r.record(source) # read the entire audio file

	WIT_AI_KEY = "3S4FE6EQEVKKQT2GLEJV3XFYHKUW2FYX" # Wit.ai keys are 32-character uppercase alphanumeric strings
	try:
    	    print("Wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
	except sr.UnknownValueError:
    	    print("Wit.ai could not understand audio")
	except sr.RequestError as e:
    	    print("Could not request results from Wit.ai service; {0}".format(e))
	

    def play_mp3(self, filename, addl_filenames=[], pause=True):
        """Plays MP3 file(s).
        
        @param: filename: The file path of the MP3 file to play.
        @type: filename: str
        
        @param: addl_filenames: List of paths to additional MP3 files to play.
        @type: addl_filenames: list

        @param: pause: Whether to insert a 1 second pause between files.
        @type: pause: bool
        """
        cmd_args = ["mpg123", "-q"]
        input_list = [filename] + addl_filenames

        for f in input_list:
            cmd_args.append(f)
            if pause:
                cmd_args.append('{}/1sec.mp3'.format(self.audio_dir))

        # Join the args into a string and use shlex to parse it for subprocess
        cmd_str = " ".join(cmd_args)
        cmd = shlex.split(cmd_str)

        # Popen and communicate() to make sure all the audio finishes playing
        p = subprocess.Popen(cmd)
        p.communicate()
