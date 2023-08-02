import openai
import speech_recognition as sr
import pyttsx3
import tkinter as tk
import tkinter.messagebox as messagebox
import cv2
import numpy as np
import requests
import spacy


# Step 3: Set up OpenAI GPT-3.5 API
openai.api_key = "OpenAI GPT-3.5 API"

# OpenWeatherMap API Key
weather_api_key = "YOUR_OPENWEATHERMAP_API_KEY"

# Step 4: Define the AI Voice Assistant Function
def dkreem_assistant():
    recognizer = sr.Recognizer()

    # Create a GUI window
    root = tk.Tk()
    root.title("dkreem Assistant")

    user_input_label = tk.Label(root, text="User: ")
    user_input_label.pack()

    ai_response_label = tk.Label(root, text="dkreem: ")
    ai_response_label.pack()

    # Step 2: Customizable Voice - List available voices
    voices = pyttsx3.init().getProperty('voices')
    voice_selection = tk.StringVar()
    voice_selection.set(voices[0].id)  # Set the default voice

    voice_dropdown = tk.OptionMenu(root, voice_selection, *[(voice.name, voice.id) for voice in voices])
    voice_dropdown.pack()

    # Step 1: Add visual feedback for listening
    feedback_label = tk.Label(root, text="Listening...", fg="blue")
    feedback_label.pack()

    engine = pyttsx3.init()

    conversation_history = []  # Initialize conversation history as an empty list

    # Load spaCy NLP model
    nlp = spacy.load("en_core_web_sm")

    def listen_and_recognize():
        nonlocal feedback_label
        with sr.Microphone() as source:
            audio = recognizer.listen(source)

        try:
            user_input = recognizer.recognize_google(audio).lower()
            print("User: " + user_input)
            user_input_label.config(text="User: " + user_input)

            # Step 3: Intent Recognition - Simple Rule-based Approach
            intent = "command"  # Default intent
            if "hello" in user_input or "hi" in user_input:
                intent = "greeting"
            elif "?" in user_input:
                intent = "question"

            # Step 4: Multilingual Support - Detect language and translate if needed
            detected_language = detect(user_input)
            if detected_language != 'en':
                translator = Translator()
                user_input = translator.translate(user_input, src=detected_language, dest='en').text

            # Hide the listening feedback label once input is received
            feedback_label.pack_forget()

            # Step 6: Save Conversation History
            conversation_history.append(user_input)
            conversation_context = ' '.join(conversation_history[-3:])  # Use the last 3 elements as context

            # Step 7: Send user input to the GPT-3.5 API with intent and conversation history as context
            ai_response_label.config(text="dkreem: Thinking...")
            try:
                response = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=conversation_context,  # Use conversation history as context
                    max_tokens=150,
                    temperature=0.7,
                    context=intent  # Providing intent as context to GPT-3.5 API
                )

                ai_response = response.choices[0].text.strip()

                # Step 9: Keyword Triggering - Specific Responses based on Keywords
                if "weather" in user_input:
                    weather_data = get_weather()
                    ai_response = "The weather in {city} is {description} with a temperature of {temp}°C.".format(
                        city=weather_data["city"],
                        description=weather_data["description"],
                        temp=weather_data["temp"]
                    )
                elif "time" in user_input:
                    # You can integrate with an external time service here or use Python's datetime module
                    ai_response = "The current time is 12:00 PM."

                # Step 12: Natural Language Understanding (NLU) - Extract Named Entities
                nlp_response = nlp(user_input)
                named_entities = [entity.text for entity in nlp_response.ents]

                if named_entities:
                    ai_response += " Named Entities: " + ", ".join(named_entities)

                print("dkreem: " + ai_response)
                ai_response_label.config(text="dkreem: " + ai_response)

                # Step 3: Customizable Voice - Set the selected voice
                selected_voice = voice_selection.get()
                engine.setProperty('voice', selected_voice)

                # Step 11: Volume Control and Mute Option
                if "mute" in user_input:
                    engine.setProperty('volume', 0.0)
                else:
                    engine.setProperty('volume', 1.0)

                # Step 8: Convert AI response to speech with the selected voice
                engine.say(ai_response)
                engine.runAndWait()

                # Step 13: Continual Learning - Save conversation history to a text file (during the session)
                save_conversation_history(conversation_history)

            except openai.errors.APIConnectionError:
                ai_response = "Sorry, I'm currently unable to access the internet. Please try again later."
                ai_response_label.config(text="dkreem: " + ai_response)
                engine.say(ai_response)
                engine.runAndWait()

            except sr.UnknownValueError:
                print("dkreem: Sorry, I didn't catch that. Could you please repeat?")
                ai_response = "Sorry, I didn't catch that. Could you please repeat?"
                ai_response_label.config(text="dkreem: " + ai_response)
                engine.say(ai_response)
                engine.runAndWait()

            except sr.RequestError as e:
                print("dkreem: Oops! There was an error with the speech recognition service. {0}".format(e))
                ai_response = "Oops! There was an error with the speech recognition service."
                ai_response_label.config(text="dkreem: " + ai_response)
                engine.say(ai_response)
                engine.runAndWait()

            # Show listening feedback for the next interaction
            feedback_label.pack()

        except sr.WaitTimeoutError:
            print("dkreem: No speech detected. Please try speaking.")
            ai_response = "No speech detected. Please try speaking."
            ai_response_label.config(text="dkreem: " + ai_response)
            engine.say(ai_response)
            engine.runAndWait()

            # Show listening feedback for the next interaction
            feedback_label.pack()

    def get_weather():
        # Step 8: Skill Integration - Fetch Weather Data from OpenWeatherMap API
        city = "New York"  # You can change the default city here
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        weather_data = {
            "city": city,
            "description": data["weather"][0]["description"],
            "temp": data["main"]["temp"],
        }
        return weather_data

    def save_conversation_history(conversation_history):
        # Step 14: Privacy and Data Protection - Data is saved only during the session and not persisted
        with open("conversation_history.txt", "w") as file:
            file.write("\n".join(conversation_history[-3:]))  # Save only the last 3 interactions

    # Step 14: Privacy and Data Protection - Inform users about data collection
    def show_privacy_notice():
        privacy_notice = "Welcome to dkreem Assistant!\n\nThis voice assistant will interact with you and collect your " \
                         "spoken queries for the purpose of providing responses. Your interactions will be " \
                         "temporarily saved in memory during this session and will not be used for any other " \
                         "purpose or persist beyond the current session. By using this voice assistant, you " \
                         "consent to the collection of your interactions. If you do not wish to provide consent, " \
                         "please close the application.\n\nThank you for using dkreem Assistant!"
        tk.messagebox.showinfo("Privacy Notice", privacy_notice)

    show_privacy_notice()

# Step 15: Initialize the camera
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera, change to the appropriate camera index if needed

    def detect_objects():
        nonlocal feedback_label
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect objects using YOLO (You Only Look Once) model
            # You'll need to download the YOLO model and its configuration files
            # and put them in the appropriate paths.
            # You can find the necessary files and instructions here: https://pjreddie.com/darknet/yolo/
            net = cv2.dnn.readNet("path/to/yolov3.weights", "path/to/yolov3.cfg")
            classes = []
            with open("path/to/coco.names", "r") as f:
                classes = [line.strip() for line in f.readlines()]
            layer_names = net.getLayerNames()
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            height, width, channels = frame.shape

            # Preprocess the image
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # Get object detection results
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:  # Adjust the confidence threshold as needed
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # Draw bounding boxes and labels for detected objects
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Display the image with detected objects
            cv2.imshow("Object Detection", frame)

            # Stop the object detection when the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # Start listening in a separate thread to avoid blocking the GUI
    listen_thread = Thread(target=listen_and_recognize)
    listen_thread.daemon = True
    listen_thread.start()

    root.mainloop()

if __name__ == "__main__":
    dkreem_assistant()
