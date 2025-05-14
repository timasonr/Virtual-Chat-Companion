# Virtual Chat Companion

A Python console application that simulates chatting with a virtual female companion using GPT technology.

## Features

- Four different communication styles (formal, friendly, romantic, playful)
- Uses OpenAI API for generating natural and lively responses
- **Active initiative taking** when the conversation stagnates or pauses
- Emotional system that adapts to user messages
- Context memory that remembers important information about the user
- Age-appropriate conversation topics and style
- Colored text output for better readability
- Smart topic suggestions for short messages
- Dialog history support for coherent conversations

## Requirements

- Python 3.6 or higher
- Libraries: colorama, requests, python-dotenv
- Optional: OpenAI API key for enhanced responses

## Installation

1. Clone this repository or download the files
2. Install dependencies using pip:

```bash
pip install -r requirements.txt
```

3. For GPT functionality (recommended):
   - Create a `.env` file and add the line `OPENAI_API_KEY=your_openai_api_key`
   - Replace `your_openai_api_key` with your actual OpenAI API key

## Running the Application

```bash
python main.py
```

## Usage

1. When starting the program, you'll need to enter your age (from 13 to 100)
2. Choose your preferred communication style (1-4)
3. Start chatting with the virtual companion
4. To exit, type "exit" or "quit"

## Operation Modes

The program can operate in two modes:

1. **GPT Mode** (if OpenAI API key is configured) - uses artificial intelligence to generate natural and diverse responses that maintain context.

2. **Basic Mode** (if API key is not configured) - uses pre-made response templates for various situations.

## Initiative Taking

The program automatically detects when the conversation is dying down, based on:
- Too short user responses in succession
- Long pauses between messages
- General conversation inactivity

In these cases, the virtual companion takes initiative:
- Suggests a new topic for discussion
- Asks an interesting question
- Tells a story or shares thoughts
- Initiates activity according to the chosen communication style

## Context Memory

The companion remembers:
- Topics the user likes or dislikes
- Important personal information shared during conversation
- Previous topics to avoid repetition
- The emotional state of the conversation

## Emotional System

The companion has an emotional system that includes:
- Mood (good, neutral, bad)
- Energy level
- Attachment to the user
- Interest in the current topic

These emotional states are affected by the conversation and influence the companion's responses.

## Example Interactions

- Ask "How are you?" or "How's your mood?"
- Give a compliment: "You're so smart" or "You're nice"
- Send a short message to get a suggestion to discuss a random topic
- Stay silent for 40 seconds to see how the companion takes initiative

## Customizing Styles

You can customize the different communication styles by changing the GPT instructions in the `_создать_промпт_для_gpt()` method or the basic responses in the corresponding methods of the `ВиртуальнаяДевушка` class. 
