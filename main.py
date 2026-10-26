import os
import time
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown

console = Console()
# The client automatically looks for the GEMINI_API_KEY environment variable 
# and sets an explicit 30-second timeout to prevent indefinite socket hangs
client = genai.Client(http_options={'timeout': 30_000}) 

# 1. Define a tool (Gemini decides when to execute this based on the prompt)
def read_agents_rulebook() -> str:
    """Reads the AGENTS.md rulebook from the local directory."""
    try:
        with open("AGENTS.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No specific rules found in this directory."

# 2. Configure the Agent
chat = client.chats.create(
    model="gemini-3.8-flash", 
    config=types.GenerateContentConfig(
        system_instruction="You are an elite terminal coding assistant. Check the AGENTS.md rulebook for project guidelines.",
        temperature=0.2,
        tools=[read_agents_rulebook],
    )
)

# 3. The Interactive Loop
console.print("[bold cyan]Agent initialized. Ready for input.[/bold cyan]")

while True:
    try:
        user_input = input("❯ ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # Send input with a visual status spinner and safeguard against server hiccups
        with console.status("[bold yellow]Thinking...[/bold yellow]"):
            response = chat.send_message(user_input)
            
        console.print(Markdown(response.text))
        
    except Exception as e:
        # Gracefully catches timeouts, 503 server overloads, or connection glitches
        console.print(f"\n[bold red]API Error / Timeout:[/bold red] {e}")
        console.print("[dim]If the server timed out or was busy, try your prompt again in a moment.[/dim]")
        
    except KeyboardInterrupt:
        # Allows a clean exit directly from your keyboard
        console.print("\n[dim]Session terminated.[/dim]")
        break