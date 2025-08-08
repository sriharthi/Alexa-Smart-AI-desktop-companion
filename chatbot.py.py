import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
import pyttsx3
import datetime
from tkinter import simpledialog
from googletrans import Translator
import os
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from playsound import playsound
import time
import random
import subprocess
import webbrowser
import wikipedia
import requests
import speedtest
import pyautogui
import threading
import random
import cv2
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image,ImageTk,ImageOps
#00040f

class SoumyaAI:
    def __init__(self, root):
        self.user_score = 0
        self.computer_score = 0
        self.tie_score = 0
        self.root = root
        self.root.title("Soumya-Your Smart Companion")
        # Make window fullscreen but still show window controls (not borderless)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.state("zoomed")
        self.delete_icon = ImageTk.PhotoImage(Image.open("delete.png").resize((45, 45), Image.Resampling.LANCZOS))
        # self.root.resizable(False, False)

        # Initialize speech engine
        self.machine = pyttsx3.init()
        self.machine.setProperty("rate", 180)
        voices = self.machine.getProperty("voices")
        self.machine.setProperty("voice", voices[1].id)

        # API configurations (Replace with your own keys)
        self.weather_api_key = "71db80c13eb83dc1532f63b77332527e"
        self.news_api_key = "eaf72ab068114ce08dba33fa9c9c071a"
        self.GEMINI_API_KEY="AIzaSyCySojJTnBFlD0KbWckzjh1I1YSaqA40Xc"
        # Applications mapping
        self.applications = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "camera": "start microsoft.windows.camera:",
            "command prompt": "cmd.exe",
            "paint": "mspaint.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "spotify": "spotify.exe"
        }

        # Jokes database (fallback when API fails)
        self.jokes = [
            ("Why don't scientists trust atoms?", "Because they make up everything!"),
            ("Did you hear about the mathematician who's afraid of negative numbers?",
             "He'll stop at nothing to avoid them."),
            ("Why don't skeletons fight each other?", "They don't have the guts."),
            ("I invented a new word today!", "Plagiarism."),
            ("Why did the scarecrow win an award?", "Because he was outstanding in his field!")
        ]

        self.setup_gui()
        self.talk(f"{self.greet()} I'm Soumya, your AI assistant. How can I help you today?")

    def setup_gui(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Load background image
        self.bg_image = Image.open("i5.jpg")
        self.bg_image = self.bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a Canvas and set background image on it
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height,
                                highlightthickness=0)
        self.canvas.place(x=0, y=0)

        # Place image on canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # Now add the floating text on the same canvas
        self.canvas.create_text(screen_width // 2, 30,
                        text="Soumya – Your Smart Companion",
                        fill="#00ADB5", font=("Arial", 22, "bold"))
        # --- Chat Area (Top Right) ---
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 12),
                                                   bg="#00040f", fg="white")
        self.chat_area.place(relx=0.6, rely=0.09, relwidth=0.35, relheight=0.65)
        self.chat_area.config(state=tk.DISABLED)

        # --- Entry Field (under chat area) ---
        self.entry_var = tk.StringVar()
        self.entry_box = tk.Entry(self.root, textvariable=self.entry_var, font=("Arial", 14),
                                  bg="#00040f", fg="white", insertbackground="white")
        self.entry_box.place(relx=0.6, rely=0.76, relwidth=0.35, relheight=0.05)
        self.entry_box.bind("<Return>", lambda event: self.submit_text())

        # --- Load Button Images ---
        self.send_icon = ImageTk.PhotoImage(Image.open("send.jpeg").resize((50, 50), Image.Resampling.LANCZOS))
        self.speak_icon = ImageTk.PhotoImage(Image.open("v.jpg").resize((50, 50), Image.Resampling.LANCZOS))

        # --- Submit Button (under entry) ---
        submit_btn = tk.Button(self.root, image=self.send_icon, command=self.submit_text,
                               bd=0, bg="#00040f", activebackground="#1e1e1e")
        submit_btn.place(relx=0.70, rely=0.82)

        # --- Speak Button (next to submit) ---
        speak_btn = tk.Button(self.root, image=self.speak_icon, command=self.voice_input_threaded,
                              bd=0, bg="#00040f", activebackground="#1e1e1e")
        speak_btn.place(relx=0.78, rely=0.82)
        #delete button
        tk.Button(self.root, image=self.delete_icon, command=self.clear_chat,
          bd=0, bg="#00040f", activebackground="#00040f").place(relx=0.63, rely=0.82)
        # Quick Command Buttons
        # --- Load Command Icons ---
        # Load icons
        self.icons = {
            "time": ImageTk.PhotoImage(Image.open("time.png").resize((50, 50), Image.Resampling.LANCZOS)),
            "date": ImageTk.PhotoImage(Image.open("date.png").resize((50, 50), Image.Resampling.LANCZOS)),
            "news": ImageTk.PhotoImage(Image.open("news.png").resize((50, 50), Image.Resampling.LANCZOS)),
            "joke": ImageTk.PhotoImage(Image.open("joke.png").resize((50, 50), Image.Resampling.LANCZOS)),
            "weather": ImageTk.PhotoImage(Image.open("weather.png").resize((50, 50), Image.Resampling.LANCZOS)),
            "screenshot": ImageTk.PhotoImage(Image.open("screenshot.png").resize((50, 50), Image.Resampling.LANCZOS)),
        }

        # Position them in 2 rows, bottom-left corner
        positions = {
            "time":       (0.05, 0.75),
            "date":       (0.20, 0.75),
            "news":       (0.35, 0.75),
            "joke":       (0.05, 0.87),
            "weather":    (0.20, 0.87),
            "screenshot": (0.35, 0.87),
        }

        # Place buttons with custom background
        for cmd, (x, y) in positions.items():
            tk.Button(self.root, image=self.icons[cmd], command=lambda c=cmd: self.execute_command(c),
                    bd=0, bg="#00040f", activebackground="#00040f").place(relx=x, rely=y)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        # Small label to the right of Speak button
        status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 14),
                                bg="#00040f", fg="#EEEEEE")

        # Place next to speak button (speak button is at relx=0.76)
        status_label.place(relx=0.6, rely=0.92)

    def get_rps_score_text(self):
        return (
            f"Scores:\nYou: {self.user_score}   Soumya: {self.computer_score}   Ties: {self.tie_score}"
        )

    def launch_rps_game(self):
        """Launch Rock Paper Scissors GUI game."""
        self.user_score = 0
        self.computer_score = 0
        self.tie_score = 0

        self.rps_window = tk.Toplevel(self.root)
        self.rps_window.title("Rock Paper Scissors")
        self.rps_window.geometry("300x300")
        self.rps_window.config(bg="#393E46")

        tk.Label(self.rps_window, text="Choose your move:", font=("Arial", 14), bg="#393E46", fg="white").pack(pady=10)

        button_frame = tk.Frame(self.rps_window, bg="#393E46")
        button_frame.pack(pady=10)

        for move in ["rock", "paper", "scissors"]:
            tk.Button(button_frame, text=move.capitalize(), width=10, font=("Arial", 12),
                      bg="#00ADB5", fg="white", command=lambda m=move: self.rps_user_choice(m)).pack(side=tk.LEFT,
                                                                                                     padx=5)

        self.rps_result_label = tk.Label(self.rps_window, text="", font=("Arial", 12), bg="#393E46", fg="white")
        self.rps_result_label.pack(pady=10)

        self.score_label = tk.Label(self.rps_window, text=self.get_rps_score_text(), font=("Arial", 12), bg="#393E46",
                                    fg="white")
        self.score_label.pack(pady=10)

    def rps_user_choice(self, user_choice):
        options = ["rock", "paper", "scissors"]
        computer_choice = random.choice(options)

        if user_choice == computer_choice:
            result = "It's a draw!"
            self.tie_score += 1
        elif (user_choice == "rock" and computer_choice == "scissors") or \
                (user_choice == "scissors" and computer_choice == "paper") or \
                (user_choice == "paper" and computer_choice == "rock"):
            result = "You win!"
            self.user_score += 1
        else:
            result = "I win!"
            self.computer_score += 1

        self.talk(f"You chose {user_choice}, I chose {computer_choice}. {result}")
        self.rps_result_label.config(text=f"You: {user_choice}\nSoumya: {computer_choice}\n{result}")
        self.score_label.config(text=self.get_rps_score_text())

    def get_rps_score_text(self):
        return f"Scores - You: {self.user_score} | Soumya: {self.computer_score} | Ties: {self.tie_score}"

    def talk(self, text):
        """Convert text to speech and display response in GUI."""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"Soumya: {text}\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

        self.status_var.set(f"Speaking: {text[:30]}..." if len(text) > 30 else f"Speaking: {text}")
        self.root.update_idletasks()  # ⬅️ Force GUI update before speaking

        self.machine.say(text)
        self.machine.runAndWait()

        self.status_var.set("Ready")

    def voice_input_threaded(self):
        """Run voice input in a separate thread to prevent GUI freezing."""
        threading.Thread(target=self.voice_input, daemon=True).start()
    def clear_chat(self):
        """Clear all chat messages from the chat area."""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
    def voice_input(self):
        """Get user command using speech."""
        try:
            with sr.Microphone() as source:
                self.status_var.set("Listening...")
                self.root.update()
                self.listener = sr.Recognizer()
                self.listener.adjust_for_ambient_noise(source, duration=0.5)
                speech = self.listener.listen(source, timeout=5, phrase_time_limit=7)
                instruction = self.listener.recognize_google(speech).lower()
                self.update_chat(f"You: {instruction}\n")
                self.entry_var.set(instruction)
                self.execute_command(instruction)
        except sr.WaitTimeoutError:
            self.status_var.set("Listening timed out")
            self.talk("I didn't hear anything.")
        except sr.UnknownValueError:
            self.status_var.set("Could not understand audio")
            self.talk("Sorry, I couldn't understand what you said.")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            self.talk("Sorry, there was an error processing your request.")

    def update_chat(self, text):
        """Update chat area with new text."""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)

    def greet(self):
        """Return appropriate greeting based on time of day."""
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning!"
        elif 12 <= hour < 17:
            return "Good afternoon!"
        elif 17 <= hour < 21:
            return "Good evening!"
        else:
            return "Hello!"

    def submit_text(self):
        """Handle text input from entry box."""
        instruction = self.entry_var.get().strip().lower()
        if instruction:
            self.update_chat(f"You: {instruction}\n")
            self.execute_command(instruction)
            self.entry_var.set("")
            self.entry_box.focus_set()

    def translate_text(self, text):
        """Translate text to a user-specified language and speak it using talk()."""
        try:
            self.talk("Which language do you want to translate to? Please type the language code.")
            self.update_chat("Languages: en (English), hi (Hindi), fr (French), es (Spanish), de (German), etc.\n")

            # Ask user to type the destination language code
            lang_win = tk.Toplevel(self.root)
            lang_win.title("Select Language")
            lang_win.geometry("300x100")
            lang_win.configure(bg="#222831")

            tk.Label(lang_win, text="Enter language code:", bg="#222831", fg="white").pack(pady=5)
            lang_var = tk.StringVar()
            tk.Entry(lang_win, textvariable=lang_var).pack(pady=5)

            def on_submit():
                target_lang = lang_var.get().strip()
                lang_win.destroy()

                if not target_lang:
                    self.talk("You didn't enter a language code.")
                    return

                from googletrans import Translator
                translator = Translator()
                translated = translator.translate(text, dest=target_lang)
                translated_text = translated.text
                self.talk(f"The translation is: {translated_text}")

            tk.Button(lang_win, text="Translate", command=on_submit, bg="#00ADB5", fg="white").pack(pady=5)

        except Exception as e:
            self.talk("Sorry, there was an error with translation.")
            print("Translation error:", str(e))

    def execute_command(self, instruction):
        """Process user command and respond."""
        if not instruction:
            self.talk("Please enter a command.")
            return

        try:
            # Basic Commands
            if instruction == "hi":
                self.talk(f"{self.greet()} How can I assist you?")

            elif "lock window" in instruction or "lock computer" in instruction:
                self.talk("Locking your computer.")
                pyautogui.hotkey('win', 'l')

            elif "rock paper scissors" in instruction or "game" in instruction:
                self.launch_rps_game()

            elif "play" in instruction:
                song = instruction.replace("play", "").strip()
                self.talk(f"Playing {song} on YouTube...")
                webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

            elif "time" in instruction:
                current_time = datetime.datetime.now().strftime('%I:%M %p')
                self.talk(f"The current time is {current_time}")

            elif "date" in instruction:
                current_date = datetime.datetime.now().strftime('%A, %B %d, %Y')
                self.talk(f"Today is {current_date}")

            elif "how are you" in instruction:
                self.talk("I'm doing great! How about you?")

            elif "your name" in instruction:
                self.talk("I am Sowmya, your personal AI assistant.")

            elif "explain" in instruction:
                topic = instruction.replace("explain", "").strip()
                self.talk(f"Searching Wikipedia for {topic}...")
                try:
                    info = wikipedia.summary(topic, sentences=1)
                    self.talk(info)
                except wikipedia.exceptions.DisambiguationError:
                    self.talk("There are multiple results. Please be more specific.")
                except wikipedia.exceptions.PageError:
                    self.talk("Sorry, I couldn't find anything on that topic.")
            elif "click my photo" in instruction or "take my photo" in instruction:
                self.talk("Clicking your picture")
                self.click_photo()
            elif "wikipedia" in instruction:
                query = instruction.replace("wikipedia", "").strip()
                self.search_wikipedia(query)
            elif "whatsapp" in instruction:
                self.talk("Opening WhatsApp Web.")
                webbrowser.open("https://web.whatsapp.com")
            elif "search" in instruction:
                query = instruction.replace("search", "").strip()
                self.talk(f"Searching Google for {query}...")
                webbrowser.open(f"https://www.google.com/search?q={query}")

            elif "open" in instruction:
                self.open_application(instruction)

            # Additional Features
            elif "weather" in instruction:
                location = instruction.replace("weather", "").replace("in", "").replace("for", "").strip()
                if location:
                    self.get_weather(location)
                else:
                    self.talk("Please specify a location (e.g., 'weather in London')")

            elif "joke" in instruction or "funny" in instruction:
                self.tell_joke()
            elif "internet speed" in instruction or "speed test" in instruction:
                self.check_internet_speed()

            elif "news" in instruction:
                self.get_news()

            elif "calculate" in instruction or (
                    "what is" in instruction and any(op in instruction for op in ["+", "-", "*", "/"])):
                self.calculate(instruction)

            elif "screenshot" in instruction:
                self.take_screenshot()

            elif "shutdown" in instruction:
                if messagebox.askyesno("Confirm", "Are you sure you want to shutdown your computer?"):
                    self.talk("Shutting down the system in 30 seconds.")
                    os.system("shutdown /s /t 30")
                else:
                    self.talk("Shutdown cancelled.")

            elif "restart" in instruction:
                if messagebox.askyesno("Confirm", "Are you sure you want to restart your computer?"):
                    self.talk("Restarting the system in 30 seconds.")
                    os.system("shutdown /r /t 30")
                else:
                    self.talk("Restart cancelled.")

            elif "exit" in instruction or "bye" in instruction or "goodbye" in instruction:
                self.talk("Goodbye! Have a great day!")
                self.root.after(2000, self.root.destroy)

            # elif "translate" in instruction:
            #     phrase = instruction.replace("translate", "").strip()
            #     if phrase:
            #         self.translate_text(phrase)
            #     else:
            #         self.talk("Please tell me what to translate.")
            elif "." in instruction:
                gemini_query = instruction
                # self.talk("Connecting to Gemini...")
                self.interact_with_gemini(gemini_query)
            else:
                self.talk("Sorry I could'nt understand")
        except Exception as e:
            self.talk("Sorry, there was an error processing your command.")
            print(f"Error: {str(e)}")

    def open_application(self, instruction):
        """Handle application opening commands."""
        app_name = instruction.replace("open", "").strip()

        if "." in app_name:  # Website URL
            if not app_name.startswith(("http://", "https://")):
                app_name = "https://" + app_name
            self.talk(f"Opening {app_name}...")
            webbrowser.open(app_name)

        elif app_name in self.applications:  # Local application
            self.talk(f"Opening {app_name}...")
            try:
                if app_name == "camera":
                    os.system(self.applications[app_name])
                else:
                    subprocess.Popen(self.applications[app_name])
            except Exception as e:
                self.talk(f"Sorry, I couldn't open {app_name}.")
                print(f"Error opening {app_name}: {str(e)}")
        else:
            self.talk(f"Sorry, I don't know how to open {app_name}.")

    def search_wikipedia(self, query):
        """Search Wikipedia for information."""
        if not query:
            self.talk("Please specify what you want me to look up.")
            return

        self.talk(f"Searching for information about {query}...")
        try:
            result = wikipedia.summary(query, sentences=2)
            self.talk(f"Here's what I found about {query}: {result}")
        except wikipedia.exceptions.DisambiguationError as e:
            self.talk(f"There are multiple results for {query}. Please be more specific.")
        except wikipedia.exceptions.PageError:
            self.talk(f"Sorry, I couldn't find any information about {query}.")
        except Exception as e:
            self.talk("Sorry, there was an error searching Wikipedia.")
            print(f"Wikipedia error: {str(e)}")

    def check_internet_speed(self):
        """Check and report internet speed."""
        try:
            self.talk("Checking your internet speed. This may take a moment...")
            st = speedtest.Speedtest()
            st.get_best_server()

            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000
            ping = st.results.ping

            speed_info = (
                f"Internet Speed Results:\n"
                f"Download: {download_speed:.2f} Mbps\n"
                f"Upload: {upload_speed:.2f} Mbps\n"
                f"Ping: {ping:.2f} ms"
            )
            self.talk(speed_info)
        except Exception as e:
            self.talk("Sorry, I couldn't check your internet speed.")
            print(f"Speed test error: {str(e)}")

    def take_screenshot(self):
        """Take and save a screenshot."""
        try:
            screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            self.talk(f"Screenshot saved to device")
        except Exception as e:
            self.talk("Sorry, I couldn't take a screenshot.")
            print(f"Screenshot error: {str(e)}")

    # ===== ADDITIONAL FEATURES =====

    def get_weather(self, location):
        """Get weather information using OpenWeatherMap API."""
        try:
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            complete_url = f"{base_url}appid={self.weather_api_key}&q={location}&units=metric"

            response = requests.get(complete_url)
            data = response.json()

            if data["cod"] != "404":
                main = data["main"]
                weather = data["weather"][0]

                weather_info = (
                    f"Weather in {location}:\n"
                    f"Temperature: {main['temp']}°C (Feels like {main['feels_like']}°C)\n"
                    f"Conditions: {weather['description'].capitalize()}\n"
                    f"Humidity: {main['humidity']}%\n"
                    f"Wind Speed: {data['wind']['speed']} m/s"
                )
                self.talk(weather_info)
            else:
                self.talk(f"Sorry, couldn't find weather for {location}.")
        except Exception as e:
            self.talk("Sorry, I couldn't fetch weather information.")
            print(f"Weather API error: {str(e)}")

    import cv2  # Make sure it's at the top of your file

    def click_photo(self):
        """Open webcam and click a photo."""
        try:
            self.talk("Opening camera. Get ready for the photo.")
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                self.talk("Sorry, I couldn't access your camera.")
                return

            self.talk("Press space to take the photo or ESC to cancel.")
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.talk("Failed to capture image.")
                    break

                cv2.imshow("Press SPACE to capture", frame)
                key = cv2.waitKey(1)

                if key == 27:  # ESC to exit
                    self.talk("Cancelled photo capture.")
                    break
                elif key == 32:  # SPACE to capture
                    photo_dir = os.path.join(os.path.expanduser("~"), "Pictures", "SoumyaPhotos")
                    os.makedirs(photo_dir, exist_ok=True)
                    filename = os.path.join(photo_dir, f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    cv2.imwrite(filename, frame)
                    self.talk(f"Photo captured and saved as {filename}")
                    break

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            self.talk("Something went wrong while taking the photo.")
            print(f"Camera error: {e}")

    def tell_joke(self):
        """Tell a random joke."""
        try:
            url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
            response = requests.get(url)
            joke_data = response.json()

            if joke_data["type"] == "single":
                self.talk(joke_data["joke"])
            else:
                self.talk(joke_data["setup"])
                self.root.after(2000, lambda: self.talk(joke_data["delivery"]))
        except Exception as e:
            # Fallback to local jokes if API fails
            setup, punchline = random.choice(self.jokes)
            self.talk(setup)
            self.root.after(2000, lambda: self.talk(punchline))
            print(f"Joke API error: {str(e)}")

    def get_news(self):
        """Fetch top news headlines using NewsAPI."""
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.news_api_key}"
            response = requests.get(url)
            news_data = response.json()

            if news_data["status"] == "ok" and news_data["totalResults"] > 0:
                self.talk("Here are the top news headlines:")
                for i, article in enumerate(news_data["articles"][:5], 1):
                    self.talk(f"{i}. {article['title']}")
                    if i < 5:  # Pause between headlines
                        self.root.after(1500 * i)
            else:
                self.talk("Sorry, couldn't fetch news at the moment.")
        except Exception as e:
            self.talk("Sorry, I couldn't get the latest news.")
            print(f"News API error: {str(e)}")

    def calculate(self, instruction):
        """Perform basic calculations."""
        try:
            # Extract the mathematical expression
            if "calculate" in instruction:
                expr = instruction.replace("calculate", "").strip()
            elif "what is" in instruction:
                expr = instruction.replace("what is", "").strip()

            # Safety check - only allow basic math operations
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expr):
                raise ValueError("Invalid characters in expression")

            result = eval(expr)
            self.talk(f"The result is: {result}")
        except Exception as e:
            self.talk("Sorry, I couldn't perform that calculation.")
            print(f"Calculation error: {str(e)}")

    from tkinter import simpledialog
    from googletrans import Translator


    def translate_text(self, text):
        try:
            self.talk("Please enter the language code to translate to. For example, 'hi' for Hindi or 'fr' for French.")
            lang_code = simpledialog.askstring("Translate",
                                               "Enter language code (e.g., 'hi' for Hindi, 'fr' for French):",
                                               parent=self.root)

            if lang_code:
                translator = Translator()
                result = translator.translate(text, dest=lang_code)
                self.talk(f"The translation is: {result.text}")
            else:
                self.talk("You did not enter a language code.")
        except Exception as e:
            self.talk("Something went wrong during translation.")
            print("Translation error:", e)
    

    def play_rock_paper_scissors(self):
        self.talk("Let's play Rock Paper Scissors! We'll play five rounds.")
        options = ["rock", "paper", "scissors"]
        user_score = 0
        computer_score = 0

        for i in range(5):
            self.talk(f"Round {i + 1}. Your turn.")
            self.status_var.set("Listening for your move...")
            self.root.update()

            # Get user input via voice
            try:
                with sr.Microphone() as source:
                    self.listener.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.listener.listen(source, timeout=5, phrase_time_limit=4)
                    user_choice = self.listener.recognize_google(audio).lower()
            except:
                self.talk("Sorry, I didn't catch that.")
                continue

            if user_choice not in options:
                self.talk("That's not a valid choice. Please say rock, paper, or scissors.")
                continue

            computer_choice = random.choice(options)
            self.talk(f"I chose {computer_choice}.")

            # Determine winner
            if user_choice == computer_choice:
                self.talk("It's a draw.")
            elif (user_choice == "rock" and computer_choice == "scissors") or \
                    (user_choice == "scissors" and computer_choice == "paper") or \
                    (user_choice == "paper" and computer_choice == "rock"):
                user_score += 1
                self.talk("You win this round.")
            else:
                computer_score += 1
                self.talk("I win this round.")

            self.update_chat(f"Score after round {i + 1} - You: {user_score}, Soumya: {computer_score}\n")

        # Final result
        if user_score > computer_score:
            self.talk("You win the game! Well played.")
        elif user_score < computer_score:
            self.talk("I win the game! Better luck next time.")
        else:
            self.talk("It's a tie overall!")
    def interact_with_gemini(self, query):
        """Handles interaction with the Gemini language model."""
        try:
            genai.configure(api_key=self.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(query)
            gemini_response = response.text
            self.update_chat(f"Soumya: {gemini_response}\n")
            # self.talk(gemini_response)
        except Exception as e:
            error_message = "Sorry, there was an error communicating with Gemini."
            self.update_chat(f"Gemini: {error_message} (Error: {e})\n")
            self.talk(error_message)
            print(f"Gemini Interaction Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    assistant = SoumyaAI(root)
    root.mainloop()