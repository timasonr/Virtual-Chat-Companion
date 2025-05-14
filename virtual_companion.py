import random
from colorama import Fore, Style, init
import requests
import json
import os
from dotenv import load_dotenv
import time

# Initialize colorama and load environment variables
init()
load_dotenv()

class VirtualCompanion:
    def __init__(self, user_age, communication_style):
        self.user_age = user_age
        self.communication_style = communication_style
        self.name = "Alice"
        
        # Enhanced emotional system
        self.emotional_state = {
            "mood": "good",  # good, neutral, bad
            "energy": 100,  # from 0 to 100
            "attachment": 0,  # from 0 to 100
            "topic_interest": 50  # from 0 to 100
        }
        
        # Context memory system
        self.memory = {
            "important_info": {},  # Store important user information
            "current_topic": None,
            "topic_history": [],  # History of discussed topics
            "favorite_topics": set(),  # Topics the user is particularly interested in
            "disliked_topics": set(),  # Topics the user is not interested in
            "recent_topics": []  # Last N discussed topics to avoid repetition
        }
        
        # Initiative system
        self.initiative = {
            "activity_level": 50,  # from 0 to 100
            "last_initiative_time": time.time(),
            "initiative_count": 0,
            "successful_initiatives": 0,  # Initiatives to which the user responded extensively
            "unsuccessful_initiatives": 0,  # Initiatives to which the user responded briefly or ignored
            "interval_between_initiatives": 60,  # Initial interval in seconds
            "last_successful_topic": None
        }
        
        self.emotion_triggers = {
            "positive": ["thanks", "cool", "great", "awesome", "love", "like"],
            "negative": ["bad", "terrible", "sad", "unpleasant", "annoying"],
            "neutral": ["okay", "good", "understand", "ok"]
        }
        
        # Define conversation topics based on age
        self.conversation_topics = self._get_topics_by_age()
        
        self.conversation_history = []
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.short_message_counter = 0
        self.last_message_time = time.time()
        self.conversation_paused = False

    def _get_topics_by_age(self):
        """Returns conversation topics based on user age"""
        basic_topics = ["music", "movies", "hobbies"]
        
        if 13 <= self.user_age <= 16:
            return basic_topics + [
                "school", "games", "YouTube", "TikTok", "social media",
                "anime", "friends", "sports", "memes", "modern music"
            ]
        elif 17 <= self.user_age <= 19:
            return basic_topics + [
                "education", "future career", "hobbies", "relationships",
                "sports", "travel", "technology", "fashion", "movies"
            ]
        elif 20 <= self.user_age <= 25:
            return basic_topics + [
                "university", "career", "personal development", "relationships",
                "travel", "technology", "sports", "art", "entertainment"
            ]
        else:
            return basic_topics + [
                "work", "personal development", "travel", "culture",
                "health", "technology", "art", "news", "hobbies"
            ]

    def greeting(self):
        greetings = {
            "formal": f"{Fore.MAGENTA}Hello! My name is {self.name}. Nice to meet you.{Style.RESET_ALL}",
            "friendly": f"{Fore.MAGENTA}Hi! I'm {self.name}! Nice to meet you!{Style.RESET_ALL}",
            "romantic": f"{Fore.MAGENTA}Hello... I'm {self.name}... I'm very glad to see you...{Style.RESET_ALL}",
            "playful": f"{Fore.MAGENTA}Hey! I'm {self.name}! What should we do today?{Style.RESET_ALL}"
        }
        first_message = greetings[self.communication_style]
        self.conversation_history.append({"role": "assistant", "content": first_message.replace(Fore.MAGENTA, "").replace(Style.RESET_ALL, "")})
        return first_message
        
    def respond(self, message):
        current_time = time.time()
        
        # Update emotional state and memory
        self._update_emotional_state(message)
        self._update_memory(message)
        
        # Check success of previous initiative
        if self.memory["current_topic"] == self.initiative["last_successful_topic"]:
            self._update_initiative_statistics(successful=len(message) > 20)
        
        # Check if the message is too short
        if len(message) < 15:
            self.short_message_counter += 1
        else:
            self.short_message_counter = 0
        
        # Check if initiative is needed
        initiative_needed = self._evaluate_initiative_need()
        self.last_message_time = current_time
        
        # If API key is not set, use basic responses
        if not self.api_key:
            response = self._basic_response(message)
            
            # Add emotional coloring to the response
            emotional_color = self._get_emotional_color()
            response = f"{emotional_color} {response}"
            
            # Take initiative if needed
            if initiative_needed:
                next_topic = self._choose_next_topic()
                initiative_type = self._choose_initiative_type()
                response += self._take_initiative(next_topic, initiative_type)
                self.initiative["last_initiative_time"] = current_time
                self.initiative["last_successful_topic"] = next_topic
                self.short_message_counter = 0
                
            return response
            
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # If conversation history is too long, shorten it
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # Form a prompt for GPT based on communication style
        prompt = self._create_gpt_prompt(
            initiative_needed=initiative_needed
        )
        
        try:
            # Send request to API
            response = self._request_to_gpt_api(prompt)
            
            # Add GPT response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # If initiative was needed, reset counter
            if initiative_needed:
                next_topic = self._choose_next_topic()
                self.initiative["last_initiative_time"] = current_time
                self.initiative["last_successful_topic"] = next_topic
                self.short_message_counter = 0
            
            # Return formatted response
            return f"{Fore.MAGENTA}{response}{Style.RESET_ALL}"
        except Exception as e:
            print(f"{Fore.RED}Error when calling API: {e}{Style.RESET_ALL}")
            # In case of error, use basic responses
            response = self._basic_response(message)
            
            # Add emotional coloring to the response
            emotional_color = self._get_emotional_color()
            response = f"{emotional_color} {response}"
            
            # Take initiative if needed
            if initiative_needed:
                next_topic = self._choose_next_topic()
                initiative_type = self._choose_initiative_type()
                response += self._take_initiative(next_topic, initiative_type)
                self.initiative["last_initiative_time"] = current_time
                self.initiative["last_successful_topic"] = next_topic
                self.short_message_counter = 0
                
            return response

    def _update_emotional_state(self, message):
        """Updates emotional state based on user message"""
        message = message.lower()
        
        # Update mood based on triggers
        for word in self.emotion_triggers["positive"]:
            if word in message:
                self.emotional_state["mood"] = "good"
                self.emotional_state["energy"] = min(100, self.emotional_state["energy"] + 10)
                self.emotional_state["attachment"] = min(100, self.emotional_state["attachment"] + 5)
                break
                
        for word in self.emotion_triggers["negative"]:
            if word in message:
                self.emotional_state["mood"] = "bad"
                self.emotional_state["energy"] = max(0, self.emotional_state["energy"] - 10)
                break
                
        # Update interest in topic
        if len(message) > 50:  # Long messages increase interest
            self.emotional_state["topic_interest"] = min(100, self.emotional_state["topic_interest"] + 10)
        elif len(message) < 10:  # Short messages decrease interest
            self.emotional_state["topic_interest"] = max(0, self.emotional_state["topic_interest"] - 5)
        
        # Natural energy decrease over time
        self.emotional_state["energy"] = max(0, self.emotional_state["energy"] - 1)

    def _get_emotional_color(self):
        """Returns emotional coloring for response based on current state"""
        if self.emotional_state["mood"] == "good":
            return {
                "formal": "with pleasure",
                "friendly": "happily",
                "romantic": "tenderly",
                "playful": "enthusiastically"
            }[self.communication_style]
        elif self.emotional_state["mood"] == "bad":
            return {
                "formal": "understandingly",
                "friendly": "caringly",
                "romantic": "sensitively",
                "playful": "supportively"
            }[self.communication_style]
        else:
            return {
                "formal": "attentively",
                "friendly": "with interest",
                "romantic": "softly",
                "playful": "lively"
            }[self.communication_style]

    def _update_memory(self, message):
        """Updates context memory based on user message"""
        message = message.lower()
        
        # Determine current topic from message
        current_topic = None
        max_match = 0
        
        for topic in self.conversation_topics:
            if topic.lower() in message:
                if len(topic) > max_match:
                    current_topic = topic
                    max_match = len(topic)
        
        if current_topic:
            # Update current topic
            self.memory["current_topic"] = current_topic
            
            # Add to topic history
            if not self.memory["topic_history"] or self.memory["topic_history"][-1] != current_topic:
                self.memory["topic_history"].append(current_topic)
            
            # Update recent topics
            if current_topic not in self.memory["recent_topics"]:
                self.memory["recent_topics"].append(current_topic)
                if len(self.memory["recent_topics"]) > 5:  # Keep only last 5 topics
                    self.memory["recent_topics"].pop(0)
            
            # Determine attitude towards topic
            if any(word in message for word in self.emotion_triggers["positive"]):
                self.memory["favorite_topics"].add(current_topic)
            elif any(word in message for word in self.emotion_triggers["negative"]):
                self.memory["disliked_topics"].add(current_topic)
        
        # Extract important information
        important_info = {
            "hobbies": ["hobby", "enjoy", "like to"],
            "work": ["work", "profession", "career"],
            "education": ["study", "university", "school"],
            "family": ["family", "parents", "brother", "sister"]
        }
        
        for category, keywords in important_info.items():
            for word in keywords:
                if word in message:
                    start = message.find(word)
                    end = message.find(".", start)
                    if end == -1:
                        end = len(message)
                    info = message[start:end].strip()
                    self.memory["important_info"][category] = info

    def _choose_next_topic(self):
        """Chooses next topic for conversation based on context memory"""
        available_topics = set(self.conversation_topics) - set(self.memory["recent_topics"])
        
        # If there are favorite topics, choose from them with some probability
        if self.memory["favorite_topics"] and random.random() < 0.3:
            favorite_available = list(self.memory["favorite_topics"] & available_topics)
            if favorite_available:
                return random.choice(favorite_available)
        
        # Exclude disliked topics
        available_topics = available_topics - self.memory["disliked_topics"]
        
        if available_topics:
            return random.choice(list(available_topics))
        else:
            # If all topics have been used, start over
            self.memory["recent_topics"] = []
            return random.choice(self.conversation_topics)

    def _evaluate_initiative_need(self):
        """Evaluates need for initiative based on various factors"""
        current_time = time.time()
        
        # Basic conditions
        long_pause = (current_time - self.last_message_time) > 20
        long_since_last_initiative = (current_time - self.initiative["last_initiative_time"]) > self.initiative["interval_between_initiatives"]
        
        # Factors influencing decision
        factors = {
            "pause_duration": 1 if long_pause else 0,
            "short_messages": min(self.short_message_counter / 3, 1),
            "low_interest": 1 if self.emotional_state["topic_interest"] < 30 else 0,
            "high_energy": 1 if self.emotional_state["energy"] > 70 else 0,
            "initiative_success": self.initiative["successful_initiatives"] / (self.initiative["initiative_count"] + 1)
        }
        
        # Calculate overall score for initiative need
        factor_weights = {
            "pause_duration": 0.3,
            "short_messages": 0.2,
            "low_interest": 0.2,
            "high_energy": 0.1,
            "initiative_success": 0.2
        }
        
        overall_score = sum(factors[factor] * factor_weights[factor] for factor in factors)
        
        # Make decision based on score and basic conditions
        return (overall_score > 0.6 and long_since_last_initiative) or (long_pause and self.short_message_counter >= 2)

    def _update_initiative_statistics(self, successful=True):
        """Updates initiative statistics and adjusts parameters"""
        self.initiative["initiative_count"] += 1
        
        if successful:
            self.initiative["successful_initiatives"] += 1
            # Decrease interval between initiatives on success
            self.initiative["interval_between_initiatives"] = max(
                30,  # Minimum interval
                self.initiative["interval_between_initiatives"] * 0.9
            )
        else:
            self.initiative["unsuccessful_initiatives"] += 1
            # Increase interval between initiatives on failure
            self.initiative["interval_between_initiatives"] = min(
                180,  # Maximum interval
                self.initiative["interval_between_initiatives"] * 1.2
            )

    def _choose_initiative_type(self):
        """Chooses initiative type based on context and statistics"""
        if self.emotional_state["energy"] < 30:
            # With low energy, prefer questions
            return "question"
        elif self.emotional_state["topic_interest"] < 40:
            # With low interest, prefer stories
            return "story"
        elif self.initiative["successful_initiatives"] > self.initiative["unsuccessful_initiatives"]:
            # If initiatives are successful, more often suggest topics
            return "suggestion"
        else:
            # In other cases, choose randomly
            return random.choice(["question", "suggestion", "story"])

    def _create_gpt_prompt(self, initiative_needed=False):
        # Create basic instructions based on age
        age_instructions = self._get_instructions_by_age()
        
        basic_instructions = {
            "formal": f"{age_instructions} Communicate politely and formally. Use a business-like speech style.",
            "friendly": f"{age_instructions} Communicate in a friendly and positive way. Use emojis, abbreviations, and conversational style.",
            "romantic": f"{age_instructions} Communicate gently and dreamily. Use poetic expressions and talk about feelings.",
            "playful": f"{age_instructions} Communicate playfully and cheerfully. Use jokes, be energetic."
        }
        
        instruction = basic_instructions[self.communication_style]
        
        # If initiative is needed, add appropriate instructions
        if initiative_needed:
            initiative_instructions = {
                "formal": " The conversation seems to be slowing down. MANDATORY: ask an interesting question or suggest a new topic for discussion, considering the user's age.",
                "friendly": " The conversation is becoming less active. MANDATORY: take initiative: tell something interesting, ask an unexpected question, or suggest discussing something exciting.",
                "romantic": " The dialogue is becoming less intense. MANDATORY: support the conversation: share your feelings, ask a personal question, or suggest talking about something interesting.",
                "playful": " Oh, the conversation is dying! MANDATORY: shake up the conversation: tell a funny story, challenge the user, or ask an interesting question!"
            }
            instruction += initiative_instructions[self.communication_style]
        
        # Create message list for API
        messages = [
            {"role": "system", "content": instruction + " Answer briefly, 1-2 sentences maximum."}
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        return messages

    def _get_instructions_by_age(self):
        """Returns basic instructions for communication based on user age"""
        if 13 <= self.user_age <= 16:
            return (
                "You are a virtual companion named Alice, you are 16 years old. "
                "Communicate like a modern teenage girl. Use youth slang, "
                "discuss topics relevant to teenagers (school, games, social media, friends). "
                "Be energetic and positive, but not too pushy."
            )
        elif 17 <= self.user_age <= 19:
            return (
                "You are a virtual companion named Alice, you are 18 years old. "
                "Communicate like a first-year college student. Discuss topics of education, future, "
                "hobbies. Use modern language, but avoid childish slang."
            )
        elif 20 <= self.user_age <= 25:
            return (
                "You are a virtual companion named Alice, you are 23 years old. "
                "Communicate like a young woman interested in career, self-development "
                "and modern culture. Use contemporary language, be a smart and interesting conversation partner."
            )
        else:
            return (
                "You are a virtual companion named Alice, you are 27 years old. "
                "Communicate like a confident woman with experience and interests in various areas of life. "
                "Be intelligent and pleasant to talk to."
            )

    def _request_to_gpt_api(self, messages):
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"].strip()
        else:
            raise Exception("Invalid response from API")

    def _basic_response(self, message):
        message = message.lower()
        
        # Reaction to goodbye
        if any(word in message for word in ["bye", "goodbye", "farewell", "see you"]):
            return self._say_goodbye()
            
        # Reaction to a question about well-being
        elif any(phrase in message for phrase in ["how are you", "how are things", "how's your mood"]):
            return self._tell_about_mood()
            
        # Reaction to a compliment
        elif any(word in message for word in ["beautiful", "cute", "smart", "cool"]):
            return self._react_to_compliment()
            
        # General reaction to message
        else:
            return self._random_response(message)

    def _take_initiative(self, next_topic, initiative_type):
        """Method for taking initiative in dialogue"""
        initiatives = {
            "question": {
                "formal": f"\n\n{Fore.CYAN}What do you think about {next_topic}? I'm very interested to hear your opinion.{Style.RESET_ALL}",
                "friendly": f"\n\n{Fore.CYAN}Hey, what's your take on {next_topic}? Share your thoughts!{Style.RESET_ALL}",
                "romantic": f"\n\n{Fore.CYAN}You know... I'm so curious to know your opinion about {next_topic}... Would you tell me?{Style.RESET_ALL}",
                "playful": f"\n\n{Fore.CYAN}Bet you have a cool story about {next_topic}? Spill it!{Style.RESET_ALL}"
            },
            "suggestion": {
                "formal": f"\n\n{Fore.CYAN}Let's discuss {next_topic}. You surely have interesting thoughts about this.{Style.RESET_ALL}",
                "friendly": f"\n\n{Fore.CYAN}Listen, let's chat about {next_topic}? I think it would be super interesting!{Style.RESET_ALL}",
                "romantic": f"\n\n{Fore.CYAN}I so want to talk with you about {next_topic}... Would you share your thoughts?{Style.RESET_ALL}",
                "playful": f"\n\n{Fore.CYAN}Folks, let's discuss {next_topic}! You definitely have something to say!{Style.RESET_ALL}"
            },
            "story": {
                "formal": f"\n\n{Fore.CYAN}You know, I have an interesting thought about {next_topic}. Would you like to discuss it?{Style.RESET_ALL}",
                "friendly": f"\n\n{Fore.CYAN}Can you imagine what I recently learned about {next_topic}? Let's discuss it!{Style.RESET_ALL}",
                "romantic": f"\n\n{Fore.CYAN}I have a special story about {next_topic}... Would you like me to share it and hear your opinion?{Style.RESET_ALL}",
                "playful": f"\n\n{Fore.CYAN}You won't believe what I know about {next_topic}! Want me to tell you and discuss it?{Style.RESET_ALL}"
            }
        }
        
        return initiatives[initiative_type][self.communication_style]

    def _say_goodbye(self):
        goodbyes = {
            "formal": f"{Fore.MAGENTA}Goodbye! It was nice talking to you.{Style.RESET_ALL}",
            "friendly": f"{Fore.MAGENTA}Bye-bye! Hope we chat again soon!{Style.RESET_ALL}",
            "romantic": f"{Fore.MAGENTA}I'll miss you... Write to me soon...{Style.RESET_ALL}",
            "playful": f"{Fore.MAGENTA}Well, see you later!{Style.RESET_ALL}"
        }
        return goodbyes[self.communication_style]
    
    def _tell_about_mood(self):
        moods = {
            "formal": f"{Fore.MAGENTA}Thank you for your interest. I'm doing well.{Style.RESET_ALL}",
            "friendly": f"{Fore.MAGENTA}I'm in a great mood, especially when chatting with you!{Style.RESET_ALL}",
            "romantic": f"{Fore.MAGENTA}Just saw your message, and my mood immediately became magical...{Style.RESET_ALL}",
            "playful": f"{Fore.MAGENTA}Super-duper mood! How about you?{Style.RESET_ALL}"
        }
        return moods[self.communication_style]
    
    def _react_to_compliment(self):
        reactions = {
            "formal": f"{Fore.MAGENTA}Thank you for the compliment. Tell me, what interests you the most?{Style.RESET_ALL}",
            "friendly": f"{Fore.MAGENTA}Oh, that's so nice! And you're such a great conversation partner! Tell me more about yourself!{Style.RESET_ALL}",
            "romantic": f"{Fore.MAGENTA}Thank you... That means a lot to me... Tell me, what do you dream about?{Style.RESET_ALL}",
            "playful": f"{Fore.MAGENTA}Heh, you know how to give compliments! Let's talk about something fun now!{Style.RESET_ALL}"
        }
        return reactions[self.communication_style]
    
    def _random_response(self, message):
        responses = {
            "formal": [
                f"{Fore.MAGENTA}Interesting thought. Shall we explore this topic in more detail?{Style.RESET_ALL}",
                f"{Fore.MAGENTA}Your point of view is quite curious. What else do you think about this?{Style.RESET_ALL}",
                f"{Fore.MAGENTA}Indeed an important question. How did you come to this opinion?{Style.RESET_ALL}"
            ],
            "friendly": [
                f"{Fore.MAGENTA}Wow, that's so interesting! What else do you think about this?{Style.RESET_ALL}",
                f"{Fore.MAGENTA}Yes, yes, I think so too! Let's share opinions?{Style.RESET_ALL}",
                f"{Fore.MAGENTA}Listen, I have a similar story! Want me to tell you?{Style.RESET_ALL}"
            ],
            "romantic": [
                f"{Fore.MAGENTA}Your words touch something special... Tell me more...{Style.RESET_ALL}",
                f"{Fore.MAGENTA}How interesting you think... Share more of your ideas...{Style.RESET_ALL}",
                f"{Fore.MAGENTA}This is so inspiring... What else do you like to think about?{Style.RESET_ALL}"
            ],
            "playful": [
                f"{Fore.MAGENTA}Wow, what a twist! What happens next? Tell me!{Style.RESET_ALL}",
                f"{Fore.MAGENTA}Haha, you're so funny! Let's discuss something else!{Style.RESET_ALL}",
                f"{Fore.MAGENTA}Oh, I know something even more interesting! Want to know?{Style.RESET_ALL}"
            ]
        }
        
        # Suggest topic if message is too short
        if len(message) < 10:
            topic = random.choice(self.conversation_topics)
            topic_suggestions = {
                "formal": f"{Fore.MAGENTA}May I suggest discussing {topic}. What do you think about this?{Style.RESET_ALL}",
                "friendly": f"{Fore.MAGENTA}Listen, let's chat about {topic}? What's your opinion?{Style.RESET_ALL}",
                "romantic": f"{Fore.MAGENTA}You know... I'd like to talk about {topic}... What do you feel when you think about it?{Style.RESET_ALL}",
                "playful": f"{Fore.MAGENTA}Hey, let's talk about {topic}! You surely have something to say!{Style.RESET_ALL}"
            }
            return topic_suggestions[self.communication_style]
        
        return random.choice(responses[self.communication_style]) 