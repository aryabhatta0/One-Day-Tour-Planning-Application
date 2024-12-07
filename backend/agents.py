import requests

# An LLM-based agent to interact with the user and dynamically collect preference
class UserInteractionAgent:
    def __init__(self, llm):
        self.llm = llm
        self.required_fields = ["city", "budget", "interests", "start_time", "end_time"]
        self.user_data = {field: None for field in self.required_fields}

    def interact(self, user_message):
        # Use LLM to extract fields from the message
        extracted_data = self._extract_fields_with_llm(user_message)

        # Update the collected data with extracted fields
        for field, value in extracted_data.items():
            if field in self.user_data and self.user_data[field] is None:
                self.user_data[field] = value

        missing_fields = [field for field, value in self.user_data.items() if value is None]

        if missing_fields:
            response = self._generate_prompt_for_field(missing_fields)
        else:
            response = "Thank you! All required preferences have been collected."

        return response, self.user_data

    def _extract_fields_with_llm(self, user_message):
        prompt = f"""
        You are a travel assistant. Extract the following details from the user's message:
        - City: The city the user wants to visit.
        - Budget: The budget for the trip.
        - Interests: The user's interests (e.g., historical sites, shopping).
        - Start Time: The time the user wants to start the trip.
        - End Time: The time the user wants to end the trip.
        If a detail is not mentioned, return 'None' for it.

        User's Message: "{user_message}"

        Respond with a JSON object containing the extracted details.
        """
        llm_response = self.llm(prompt)
        try:
            extracted_data = eval(llm_response)  
        except Exception as e:
            extracted_data = {field: None for field in self.required_fields}  # None by default
        return extracted_data

    def _generate_prompt_for_field(self, field):
        prompt = f"""
        You are a travel assistant. Give a short, concise, and interactive
        prompt to ask user to provide missing fields.

        Missing field: "{field}"

        Respond with a prompt string for user.
        """
        llm_response = self.llm(prompt)
        return llm_response

  
class ItineraryAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_itinerary(self, preferences):
        prompt = f"""
        You are a travel assistant. Based on these preferences:
        {preferences}, plan a one-day itinerary for the user.
        """
        response = self.llm(prompt)
        return response


# Fetch weather information
class WeatherAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_weather(self, city):
        url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={city}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch weather data"}


class OptimizationAgent:
    def optimize_itinerary(self, itinerary, budget, time_constraints):
        # TODO: Optimization Logic
        optimized_itinerary = itinerary 
        return f"Optimized Itinerary: {optimized_itinerary}"


class MemoryAgent:
    def __init__(self, database_manager):
        self.db = database_manager

    def store_preferences(self, user_id, preferences):
        self.db.store_user_preferences(user_id, preferences)

    def retrieve_preferences(self, user_id):
        return self.db.get_user_preferences(user_id)

