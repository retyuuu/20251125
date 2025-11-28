from openai import OpenAI
from configparser import ConfigParser
import requests
import json

# Load configuration from config.ini
config = ConfigParser()
config.read("config.ini")

client = OpenAI(
    api_key=config.get("AzureOpenAI", "API_KEY"),
    base_url=config.get("AzureOpenAI", "END_POINT"),
    default_query={"api-version": "preview"},
)
def add(a: int, b: int) -> int:
    return a + b


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    Args:
        city (str): The name of the city for which to retrieve the weather report.
        the city name should be in English 
    Returns:
        dict: status and result or error msg.
    """
    api_key = config.get("OpenWeatherMap", "API_KEY")
    if not api_key:
        return {
            "status": "error",
            "error_message": "API key for OpenWeatherMap is not set.",
        }
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        print(data)
        if data["cod"] != 200:
            return {
                "status": "error",
                "error_message": f"Weather information for '{city}' is not available.",
            }
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        report = (
            f"The weather in {city} is {weather_description} with a temperature of "
            f"{temperature} degrees Celsius."
        )
        return {"status": "success", "report": report}
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while fetching the weather data: {str(e)}",
        }


question = "現在舊金山溫度幾度？"
# question = "你好"

response = client.responses.create(
    model=config.get("AzureOpenAI", "DEPLOYMENT_NAME_GPT4o_Mini"),
    input=question,
    max_output_tokens=1000,
    tools=[
        {
            "type": "function",
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                },
                "required": ["location"],
            },
        }
    ],
)

print(response.model_dump_json(indent=2))
# print(f"Q: {question}")
# print(f"A: {response.output_text}")

# To provide output to tools, add a response for each tool call to an array passed
# to the next response as `input`
input = []
for output in response.output:
    if output.type == "function_call":
        match output.name:
            case "get_weather":
                input.append(
                    {
                        "type": "function_call_output",
                        "call_id": output.call_id,
                        "output": str(get_weather(
                            json.loads(response.output[0].arguments)["location"]
                        )),
                    }
                )
            case _:
                raise ValueError(f"Unknown function call: {output.name}")

        second_response = client.responses.create(
            model=config.get("AzureOpenAI", "DEPLOYMENT_NAME_GPT4o_Mini"), 
            previous_response_id=response.id, 
            input=input
        )

        # print(second_response.model_dump_json(indent=2))
        print(f"Q: {question}")
        print(f"A: {second_response.output_text}")
    else:
        print(f"Q: {question}")
        print(f"A: {response.output_text}")