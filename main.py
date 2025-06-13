import customtkinter as ctk
import tkinter as tk
from tkinter import Toplevel
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" 
import pyttsx3
import datetime
import threading
import pygame
from PIL import Image, ImageTk, ImageSequence
import speech_recognition as sr
import pywhatkit
import wikipedia
import pyautogui
import random
import google.generativeai as genai
import webbrowser

# Set appearance mode and theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# Initialize pygame mixer for playing music
pygame.mixer.init()

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 200)


def speak(audio):
    """Speak text using pyttsx3 in a separate thread."""
    def run_speech():
        engine.say(audio)
        engine.runAndWait()

    threading.Thread(target=run_speech, daemon=True).start()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak(f"Good Morning! I am Friday How can I assist you today?")
    elif 12 <= hour < 18:
        speak(f"Good Afternoon! I am Friday. How can I assist you today?")
    else:
        speak(f"Good Evening! I am Friday. How can I assist you today?")
    


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio, language='en-in')
        return query
    except Exception:
        return "None"

def randomJoke():
    jokes = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐞",
    "Why was the JavaScript developer sad? Because they didn’t know how to null their feelings. 😢",
    "Why do Python developers prefer snakes over cats? Because they love working with a Py-thon! 🐍",
    "How do programmers like their sandwiches? Open source! 🥪",
    "Why did the programmer quit their job? They didn’t get arrays. 🤷‍♂️",
    "How do you comfort a JavaScript bug? You console it. 😂",
    "Why was the developer always calm? Because they always handled exceptions! 😌",
    "Why don’t programmers like nature? Too many bugs. 🌳🐜",
    "Why was the computer cold? It left its Windows open! 🥶",
    "What’s a programmer’s favorite hangout place? The Foo Bar! 🍻"]
    random_joke = random.choice(jokes)
    speak(random_joke)

class AnimatedBackground(ctk.CTkCanvas):
    def __init__(self, master, gif_path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Load GIF frames
        self.frames = []
        with Image.open(gif_path) as gif:
            for frame in ImageSequence.Iterator(gif):
                frame = frame.resize((800, 600))  # Resize GIF to fit the window (800x600)
                self.frames.append(ImageTk.PhotoImage(frame))

        self.current_frame = 0
        self.configure(width=800, height=600, highlightthickness=0, bg="black")
        self.pack(fill="both", expand=True)

        # Start animation
        self.animation_running = True
        self.update_animation()

    def update_animation(self):
        if self.animation_running and self.frames:
            self.delete("all")  # Clear the canvas
            self.create_image(0, 0, anchor="nw", image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(50, self.update_animation)  # Adjust frame rate for smoothness

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed = False 
        self.geometry("800x600")  # Set the window resolution to 800x600
        self.title("Friday - Personal AI Assistant")
        self.iconbitmap("icon.ico")

        # Disable window resizing
        self.resizable(False, False)

        self.play_music()

        # States
        self.is_awake = True
        self.is_mic_on = False  # Initially mic is off

        # Fonts
        self.title_font = ctk.CTkFont(family="Cascadia Code", size=45, weight="bold", slant="italic")
        self.button_font = ctk.CTkFont(family="Verdana", size=15, weight="bold")

        # Animated Background
        self.background = AnimatedBackground(self, "visual.gif")

        # Title
        self.title_label = ctk.CTkLabel(self, text="Friday", font=self.title_font, bg_color='white')
        self.title_label.place(relx=0.5, rely=0.15, anchor="center")

        # Load Images for Buttons
        self.img_mic_on = Image.open("mic_on.png").resize((30, 30))
        self.img_mic_off = Image.open("mic_off.png").resize((30, 30))
        self.img_mic_on_tk = ImageTk.PhotoImage(self.img_mic_on)
        self.img_mic_off_tk = ImageTk.PhotoImage(self.img_mic_off)

        # Wake Button
        self.btn_wake = ctk.CTkButton(
            self, width=155, height=45, text="Go to sleep", font=self.button_font,
            command=self.go_to_sleep, corner_radius=0
        )
        self.btn_wake.place(relx=0.15, rely=0.9, anchor="center")

        # Mic Button
        self.btn_test = ctk.CTkButton(
            self, width=75, height=75, image=self.img_mic_off_tk,
            command=self.toggle_mic, text="", corner_radius=0
        )
        self.btn_test.place(relx=0.5, rely=0.9, anchor="center")
        self.btn_test.image = self.img_mic_off_tk

        # Start listening for the wake word
        threading.Thread(target=self.handle_voice_command, daemon=True).start()

    def play_music(self):
        """Play the startup sound and speak about the weather."""
        pygame.mixer.music.load("startup.mp3")  # Replace with your music file path
        pygame.mixer.music.play(loops=0, start=0.0)

        # Wait for the music to finish playing
        while pygame.mixer.music.get_busy():
            continue

        # After music finishes, greet the user and provide weather info
        wishMe()  # Greeting based on time



    def go_to_sleep(self):
        if not self.is_awake:
            return
        self.is_awake = False
        self.btn_wake.configure(text="Wake up", command=self.wake_up)
        self.is_mic_on = False
        self.btn_test.configure(image=self.img_mic_off_tk)
        speak("I am now asleep. Wake me up if needed.")

    def wake_up(self):
        if self.is_awake:
            return
        self.is_awake = True
        self.btn_wake.configure(text="Go to sleep", command=self.go_to_sleep)
        self.is_mic_on = True
        self.btn_test.configure(image=self.img_mic_on_tk)

    def toggle_mic(self):
        if self.is_awake:
            if self.is_mic_on:
                self.is_mic_on = False
                self.btn_test.configure(image=self.img_mic_off_tk)
                speak("Microphone is off.")
            else:
                self.is_mic_on = True
                self.btn_test.configure(image=self.img_mic_on_tk)
                speak("Microphone is on.")
                threading.Thread(target=self.handle_commands, daemon=True).start()
        else:
            speak("I am asleep. Please wake me up first.")


    def handle_voice_command(self):
        while True:
            query = takeCommand().lower()

            current_voice = engine.getProperty('voice')
            if current_voice == voices[0].id:
                voiceID = 'jarvis'
            elif current_voice == voices[1].id:
                voiceID = 'friday'

            if voiceID in query:  # Check for wake word 'Friday' or 'Jarvis'
                speak("Yes, how can I help you?")
                self.is_mic_on = True
                self.btn_test.configure(image=self.img_mic_on_tk)
                self.handle_commands()

    def handle_commands(self):
        while self.is_mic_on:
            query = takeCommand().lower()

            if query == "stop listening":
                speak("Stopping listening.")
                self.is_mic_on = False
                self.btn_test.configure(image=self.img_mic_off_tk)
                break  # Exit the loop immediately

            if query != "none":

                # Handle math-related queries
                if 'calculate' in query or 'solve' in query or 'math' in query:
                    try:
                        # Extract the math expression from the query
                        math_expression = query.replace('calculate', '').replace('solve', '').replace('math', '').strip()
                        if math_expression:
                            result = eval(math_expression)  # Evaluate the math expression
                            speak(f"The result is {result}")
                        else:
                            speak("Please specify the calculation.")
                    except Exception as e:
                        pywhatkit.search(f"{math_expression}")
        
                # Handle YouTube playback
                elif 'play' in query:
                    ytvid = query.partition('play')[2].strip()
                    speak(f"Playing {ytvid} on YouTube.")
                    threading.Thread(target=self.play_on_youtube, args=(ytvid,), daemon=True).start()

                # Handle Wikipedia search for general queries
                elif 'what is' in query or 'who is' in query:
                    try:
                        gsearch = query.partition('what is')[2].strip() or query.partition('who is')[2].strip()
                        if gsearch:
                            threading.Thread(target=self.search_wikipedia, args=(gsearch,), daemon=True).start()
                        else:
                            speak("Please specify what or who you want to search for.")
                    except:
                        summary = wikipedia.summary(query, sentences=1)
                        speak(summary)
                
                elif 'volume' in query or 'mute' in query:
                    if 'volume' in query and 'increase' in query:
                        pyautogui.press("volumeup", 10)

                    elif 'volume' in query and 'decrease' in query:
                        pyautogui.press("volumedown", 10)

                    elif 'volume' in query and ('full' in query or 'max' in query):
                        pyautogui.press("volumeup", 50)
                    
                    elif 'change' in query or 'set' in query:
                        volNum = query.partition('to')
                        volPi = (100 - int(volNum[2])) // 2
                        pyautogui.press("volumeup", 50)
                        pyautogui.press("volumedown", volPi)

                    elif 'mute' in query:
                        pyautogui.press("volumedown", 50)
                
                elif 'screenshot' in query:
                    screenshot = pyautogui.screenshot()
                    screenshot.save("screenshot.png")
                    speak('Screenshot captured successfully')

                elif 'who are you' in query or 'hu r u' in query:
                    current_voice = engine.getProperty('voice')
                    if current_voice == voices[0].id:
                        voiceID = 'JARVIS'
                    elif current_voice == voices[1].id:
                        voiceID = 'FRIDAY'
                    speak(f'I am a masterpiece exclusively created by my master Harshal Sharma. Behold, as you are talking to none other than {voiceID}.')

                elif 'how are you' in query or 'how r you' in query or 'how r u' in query:
                    speak("I'm doing great, thanks for asking! 😊 How about you?")

                elif 'am fine' in query or 'm fine' in query:
                    speak("I'm glad to here that. So, how can I help you? Wanna play some music ? or hear some jokes.")
                
                elif 'joke' in query:
                    randomJoke()
                
                elif 'full screen' in query:
                    pyautogui.press("f")
                
                elif 'time' in query:
                    time = datetime.datetime.now().strftime("%I:%M %p")
                    speak(f"The current time is {time}")
                
                elif 'voice' in query and ('male' in query or 'jarvis' in query):
                    engine.setProperty('voice', voices[0].id)
                    engine.setProperty('rate', 200)
                    speak('Voice is now set to JARVIS!')
                    self.title("J.A.R.V.I.S. - Personal AI Assistant")
                    self.title_label.configure(text='J.A.R.V.I.S.')
                    self.title_label.cget("font").configure(family="Verdana")

                elif 'voice' in query and ('female' in query or 'friday' in query):
                    engine.setProperty('voice', voices[1].id)
                    engine.setProperty('rate', 200)
                    speak('Voice is now set to FRIDAY!')
                    self.title("Friday - Personal AI Assistant")
                    self.title_label.configure(text='Friday')
                    self.title_label.cget("font").configure(family="Cascadia Code")
                
                elif 'open' in query:
                    programs = {'google': 'https://www.google.com/', 'youtube': 'https://www.youtube.com/', 'facebook': 'https://www.facebook.com/', 'github': 'https://github.com/', 'cobalt': 'https://cobalt.tools/'}
                    for program in programs:
                        if program in query:
                            webbrowser.open(programs[program])
                            speak(f'Opening {program}')
                        elif program not in query and not self.executed:
                            pyautogui.press('win')
                            openQuery = query.replace('open ', '')  
                            speak(f'Opening {openQuery}')
                            for x in openQuery:
                                pyautogui.press(x)
                            self.executed = True
                            pyautogui.press('enter')
                    self.executed = False

                elif 'generate' in query or 'write' in query or 'make' in query or 'create' in query:
                    genai.configure(api_key="AIzaSyAVk9WIM1NS-mXqMmMxsi0rGCbSSodtNmM")
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(query)
                    if response:
                        self.display_response_in_window(response.text)
                        speak('here it is.')
                    else:
                        speak("Sorry, I didn't quite get that.")

                elif 'search for' in query or 'search' in query:
                    frisearch = None  # Initialize variable to avoid UnboundLocalError
                    
                    if 'search for' in query:
                        frisearch = query.partition('search for')[2].strip()
                    elif 'search' in query:
                        frisearch = query.partition('search')[2].strip()
                    
                    if frisearch:  # Ensure frisearch is not empty
                        threading.Thread(target=pywhatkit.search, args=(frisearch,), daemon=True).start()
                    else:
                        speak("Please specify what you want to search for.")
                elif query:
                    speak('I didnt understood. Say that again please...')

    def display_response_in_window(self, response_text):
        """Display the Generative AI response in a Toplevel window with scrollbars."""
        response_window = Toplevel(self)
        response_window.geometry("600x400")
        response_window.title("AI Generated Response")

        # Create a frame to contain the textbox and scrollbars
        frame = ctk.CTkFrame(response_window)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a Textbox for displaying response
        response_textbox = ctk.CTkTextbox(
            frame,
            wrap="none",  # Prevents auto-wrapping, allowing horizontal scrolling
            font=ctk.CTkFont(family="Arial", size=14)
        )
        response_textbox.pack(side="left", fill="both", expand=True)

        # Create Vertical Scrollbar
        v_scrollbar = tk.Scrollbar(frame, orient="vertical", command=response_textbox.yview)
        v_scrollbar.pack(side="right", fill="y")
        response_textbox.configure(yscrollcommand=v_scrollbar.set)

        # Create Horizontal Scrollbar
        h_scrollbar = tk.Scrollbar(response_window, orient="horizontal", command=response_textbox.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        response_textbox.configure(xscrollcommand=h_scrollbar.set)

        # Insert the text into the textbox
        response_textbox.insert("1.0", response_text)

        # Disable editing (acts like a label)
        response_textbox.configure(state="disabled")

        # Add a close button
        close_button = ctk.CTkButton(response_window, text="Close", command=response_window.destroy)
        close_button.pack(pady=10)

    def play_on_youtube(self, video_title):
        """Handle YouTube playback in a separate thread."""
        try:
            pywhatkit.playonyt(video_title)
        except Exception as e:
            speak("There was an error playing the video on YouTube.")

    def search_wikipedia(self, query):
        """Search Wikipedia in a separate thread."""
        try:
            summary = wikipedia.summary(query, sentences=1)
            speak(summary)
        except wikipedia.exceptions.DisambiguationError:
            speak("There are multiple results. Please be more specific.")
        except wikipedia.exceptions.PageError:
            speak("I couldn't find any information on that.")
        except Exception as e:
            speak("Sorry, something went wrong while fetching the information.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
