import speech_recognition as sr
import pyttsx3
from datetime import datetime
import requests
import pytz
from pytz import country_timezones, timezone
from iso3166 import countries_by_name
import re

recognizer = sr.Recognizer()
engine = pyttsx3.init()

notes = []

def recognize_speech() -> str:
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            sayy("Listening timed out while waiting for phrase to start")
            print("Listening timed out while waiting for phrase to start")
        except sr.UnknownValueError:
            sayy("Sorry, I did not understand that.")
            print("Sorry, I did not understand that.")
        except sr.RequestError:
            sayy("Could not request results; check your network connection.")
            print("Could not request results; check your network connection.")
        return ""

def sayy(text: str):
    engine.say(text)
    engine.runAndWait()

def get_time_in_country(country_name: str) -> str:
    try:
        country_code = countries_by_name[country_name.upper()].alpha2
        country_timezones_list = country_timezones(country_code)
        if country_timezones_list:
            tz = timezone(country_timezones_list[0])
            country_time = datetime.now(tz).strftime('%H:%M')
            return f"The current time in {country_name.title()} is {country_time}"
        else:
            return "Sorry, I couldn't find the timezone for the specified country."
    except KeyError:
        return f"Error: country {country_name.title()} not found."
    except Exception as e:
        return f"Error getting time for country {country_name.title()}: {e}"

def fetch_from_api(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request error: {e}")
        return {}

def get_joke() -> str:
    joke_data = fetch_from_api("https://official-joke-api.appspot.com/jokes/random")
    if joke_data:
        return f"{joke_data['setup']} ... {joke_data['punchline']}"
    return "I couldn't fetch a joke at the moment."

def get_riddle() -> tuple:
    riddle_data = fetch_from_api("https://riddles-api.vercel.app/random")
    if riddle_data:
        return riddle_data['riddle'], riddle_data['answer']
    return "I couldn't fetch a riddle at the moment.", ""

def get_definition(word: str) -> str:
    definition_data = fetch_from_api(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    if definition_data:
        return f"The definition of {word} is: {definition_data[0]['meanings'][0]['definitions'][0]['definition']}"
    return f"I couldn't find the definition for {word}."

def get_fun_fact() -> str:
    fact_data = fetch_from_api("https://uselessfacts.jsph.pl/random.json?language=en")
    if fact_data:
        return fact_data['text']
    return "I couldn't fetch a fun fact at the moment."

def get_quote() -> str:
    quote_data = fetch_from_api("https://api.quotable.io/random")
    if quote_data:
        return f"{quote_data['content']} - {quote_data['author']}"
    return "I couldn't fetch a quote at the moment."

def get_local_time() -> str:
    local_time = datetime.now().strftime('%H:%M')
    return f"The current local time is {local_time}"

def save_notes_to_file(note: str) -> str:
    filename = "notes.txt"
    with open(filename, 'a') as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp}: {note}\n")
    return "Note saved."

def extract_word_for_definition(command: str) -> str:
    patterns = [
        r"define (.+)",
        r"what is the definition of (.+)",
        r"what is the meaning of (.+)",
        r"what does (.+) mean"
    ]
    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1).strip()
    return ""

def extract_country_from_command(command: str) -> str:
    match = re.search(r'time in\s+([\w\s]+)', command)
    if match:
        return match.group(1).strip()
    return ""

def handle_command(command: str) -> bool:
    global notes
    if "hello" in command:
        sayy("Hello! How can I help you?")
    elif "time in" in command:
        country = extract_country_from_command(command)
        if country:
            country_time = get_time_in_country(country)
            sayy(country_time)
        else:
            sayy("Please specify a country name.")
    elif "time" in command or "what is the time" in command:
        local_time = get_local_time()
        sayy(local_time)
    elif "joke" in command:
        joke = get_joke()
        sayy(joke)
    elif any(phrase in command for phrase in ["define", "what is the definition of", "what is the meaning of", "what does"]):
        word = extract_word_for_definition(command)
        if word:
            definition = get_definition(word)
            sayy(definition)
        else:
            sayy("Please provide a word to define.")
    elif "fun fact" in command:
        fun_fact = get_fun_fact()
        sayy(fun_fact)
    elif "quote" in command:
        quote = get_quote()
        sayy(quote)
    elif "note" in command:
        note = command.replace("note", "").strip()
        if note:
            save_notes_to_file(note)
            sayy("Note taken.")
        else:
            sayy("Please provide a note to save.")
    elif "riddle" in command:
        riddle, answer = get_riddle()
        sayy(riddle)
        user_answer = recognize_speech()
        if user_answer and answer.lower() in user_answer.lower():
            sayy("Correct!")
        else:
            sayy(f"Sorry, the correct answer is {answer}.")
    elif "exit" in command or "quit" in command:
        sayy("See you next time")
        return False
    else:
        sayy("Sorry, I can only respond to specific commands.")
    return True



if __name__ == "__main__":
    sayy("How can I assist you today?")
    while True:
        command = recognize_speech()
        if command:
            if not handle_command(command):
                sayy("Goodbye!")
                break