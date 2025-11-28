from openai import OpenAI
from configparser import ConfigParser

# Load configuration from config.ini
config = ConfigParser()
config.read("config.ini")

client = OpenAI(
    api_key=config.get("AzureOpenAI", "API_KEY"),
    base_url=config.get("AzureOpenAI", "END_POINT"),
    default_query={"api-version": "preview"},
)

question = """
喝酒骰子來一下，ok?
"""

response = client.responses.create(
    
    model=config.get(
        "AzureOpenAI", "DEPLOYMENT_NAME_GPT4o_Mini"
    ),  # replace with your model deployment name
    tools=[
        # {
        #     "type": "mcp",
        #     "server_label": "deepwiki",
        #     "server_url": "https://mcp.deepwiki.com/mcp",
        #     "require_approval": "never",
        # },  
        # {
        #     "type": "mcp",
        #     "server_label": "coingecko",
        #     "server_url": "https://mcp.api.coingecko.com/mcp",            
        #     "require_approval": "never",
        #     "allowed_tools": ["get-simple-prices"],
        # },
        {
            "type": "mcp",
            "server_label": "drink_dice_server",
            "server_url": "https://hierogrammatical-lovie-nondigestive.ngrok-free.dev/sse",
            "require_approval": "never",
        }
    ],
    input=question,
)

print(response.output_text)