from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import DatabaseManager
from agents import ItineraryAgent, WeatherAgent, OptimizationAgent, MemoryAgent, UserInteractionAgent
from llm import LLMManager
from config import OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, WEATHER_API_KEY

# Initialize app and database
app = FastAPI()
db_manager = DatabaseManager(uri=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)

# Initialize agents
llm = LLMManager(mode="openai", api_key=OPENAI_API_KEY)
itinerary_agent = ItineraryAgent(llm=llm.query)
weather_agent = WeatherAgent(api_key=WEATHER_API_KEY)
memory_agent = MemoryAgent(database_manager=db_manager)
optimization_agent = OptimizationAgent()


# Request models
class Preferences(BaseModel):
    user_id: str
    city: str
    budget: float
    interests: str
    start_time: str
    end_time: str


class ItineraryUpdate(BaseModel):
    user_id: str
    additional_constraints: dict


user_agent = UserInteractionAgent(llm=llm.query)

# Handles dynamic user interaction to collect preferences.
@app.post("/interact/")
def interact(user_message: dict):
    try:
        message = user_message["message"]
        response, collected_data = user_agent.interact(message)
        return {"response": response, "collected_data": collected_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/")
def get_weather(city: str):
    """
    Fetches the weather information for the given city.
    """
    try:
        weather = weather_agent.fetch_weather(city)
        return {"city": city, "weather": weather}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize/")
def optimize_itinerary(update: ItineraryUpdate):
    """
    Optimizes the itinerary based on additional constraints.
    """
    try:
        user_id = update.user_id
        preferences = memory_agent.retrieve_preferences(user_id)
        itinerary = itinerary_agent.generate_itinerary(preferences)
        optimized_itinerary = optimization_agent.optimize_itinerary(itinerary, update.additional_constraints.get("budget"), update.additional_constraints.get("time"))
        return {"message": "Itinerary optimized.", "optimized_itinerary": optimized_itinerary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """
    Root endpoint for testing.
    """
    return {"message": "Welcome to the One-Day Tour Planning Assistant!"}


@app.on_event("shutdown")
def shutdown_event():
    """
    Cleanup resources on shutdown.
    """
    db_manager.close()
