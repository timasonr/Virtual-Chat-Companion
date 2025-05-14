from virtual_companion import VirtualCompanion
from colorama import Fore, Style, init
import time
import os

# Initialize colorama
init()

def main_menu():
    print(f"{Fore.CYAN}=== VIRTUAL COMPANION CHAT ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Welcome! Let's get to know each other.{Style.RESET_ALL}")
    
    # Check for API key
    if not os.getenv("enter_your_openai_api_key"):
        print(f"{Fore.YELLOW}Note: OpenAI API key not found. Only basic responses will be used.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}For AI responses, create a .env file with OPENAI_API_KEY=your_api_key{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}OpenAI API key detected. GPT mode will be used for more interesting conversations.{Style.RESET_ALL}")
    
    # Get user age
    while True:
        try:
            age = int(input(f"{Fore.YELLOW}How old are you? {Style.RESET_ALL}"))
            if 13 <= age <= 100:
                break
            else:
                print(f"{Fore.RED}Please enter a valid age (between 13 and 100).{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
    
    # Choose communication style
    print(f"\n{Fore.CYAN}Choose your communication style:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1. Formal {Style.RESET_ALL}- polite and reserved communication")
    print(f"{Fore.YELLOW}2. Friendly {Style.RESET_ALL}- open and positive communication")
    print(f"{Fore.YELLOW}3. Romantic {Style.RESET_ALL}- tender and dreamy communication")
    print(f"{Fore.YELLOW}4. Playful {Style.RESET_ALL}- humorous and flirtatious communication")
    
    while True:
        try:
            choice = int(input(f"\n{Fore.YELLOW}Your choice (1-4): {Style.RESET_ALL}"))
            if 1 <= choice <= 4:
                styles = ["formal", "friendly", "romantic", "playful"]
                communication_style = styles[choice - 1]
                break
            else:
                print(f"{Fore.RED}Please choose a number from 1 to 4.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
    
    return age, communication_style


def start_conversation(companion):
    print(f"\n{Fore.CYAN}Starting conversation...{Style.RESET_ALL}")
    print(companion.greeting())
    
    last_response_time = time.time()
    
    while True:
        # Check if there's a pause in the conversation
        current_time = time.time()
        conversation_pause = (current_time - last_response_time) > 40  # 40 seconds
        
        # If there's a pause and the conversation is not already paused, the companion takes initiative
        if conversation_pause and not companion.conversation_paused:
            initiative = companion._take_initiative(companion._choose_next_topic(), companion._choose_initiative_type())
            print(initiative)
            companion.conversation_paused = True
            last_response_time = time.time()
        
        # Get message from user
        message = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        
        # Reset pause flag
        companion.conversation_paused = False
        
        if message.lower() in ["exit", "quit"]:
            print(f"\n{Fore.CYAN}Ending program. Goodbye!{Style.RESET_ALL}")
            break
            
        response = companion.respond(message)
        print(response)
        
        # Update last response time
        last_response_time = time.time()


if __name__ == "__main__":
    age, communication_style = main_menu()
    companion = VirtualCompanion(age, communication_style)
    start_conversation(companion) 