import os
import time
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown

console = Console()
# Sets an explicit 30-second timeout to prevent indefinite socket hangs
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
        # Customized prompt label
        user_input = input("Prompt ❯ ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # Send input with a visual status spinner
        with console.status("[bold yellow]Thinking & Reasoning...[/bold yellow]"):
            response = chat.send_message(user_input)
            
        # Display the AI's reasoning/thought process if available
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if candidate.finish_reason:
                # Check for thoughts or reasoning blocks if supported by the stream/response
                pass

        # Print the main response text
        console.print(Markdown(response.text))
        
        # Extract Token Usage and Calculate Estimated Cost
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage = response.usage_metadata
            prompt_tokens = getattr(usage, 'prompt_token_count', 0)
            completion_tokens = getattr(usage, 'candidates_token_count', 0)
            total_tokens = getattr(usage, 'total_token_count', 0)
            
            # Gemini 3.8 Flash pricing approximation: $0.075 / 1M input, $0.30 / 1M output
            est_cost = (prompt_tokens * 0.000000075) + (completion_tokens * 0.00000030)
            
            console.print(
                f"\n[dim]📊 Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total | "
                f"Est. Cost: ${est_cost:.6f}[/dim]"
            )
        
    except Exception as e:
        console.print(f"\n[bold red]API Error / Timeout:[/bold red] {e}")
        console.print("[dim]If the server timed out or was busy, try your prompt again in a moment.[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[dim]Session terminated.[/dim]")
        break