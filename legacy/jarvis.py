import speech_recognition as sr
import pyttsx3
import pywhatkit as pwk
import datetime
import wikipedia

listener = sr.Recognizer()
engine = pyttsx3.init()
engine.say('Hello I am Jarvis, an intelligent AI created by Tony Stark. What can I do to help you?')
engine.runAndWait()


def talk(text):
    engine.say(text)
    engine.runAndWait()


def take_command():
    command = ""
    try:
        with sr.Microphone() as source:
            print("listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'jarvis' in command:
                command = command.replace('jarvis', '')
                print(command)
    except:
        pass
    return command


def jarvis():
    command = take_command()
    if 'play' in command:
        song = command.replace('play', '')
        talk("playing" + song)
        pwk.playonyt(song)

    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk(' Current Time is ' + time)

    elif 'date' in command:
        date = datetime.date.today()
        talk(date)

    elif any(keyword in command for keyword in ['search', 'what', 'who', 'define', 'how', 'where', 'why', 'when']):
        for i in range(3):
            q1 = command.replace('search', '')
            q2 = q1.replace('what', '')
            q3 = q2.replace('who', '')
            q4 = q3.replace('define', '')
            q5 = q4.replace('how', '')
            q6 = q5.replace('where', '')
            q7 = q6.replace('why', '')
            q8 = q7.replace('when', '')
            question = q8.replace('define', '')
        talk(' Searching for ' + question)
        results = wikipedia.summary(question, 1)
        talk(results)

while True:
    jarvis()