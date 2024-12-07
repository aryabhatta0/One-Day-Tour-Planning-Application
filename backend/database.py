from neo4j import GraphDatabase

class DatabaseManager:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()

    def store_user_preferences(self, user_id, preferences):
        """
        Store user preferences in the graph database.
        :param user_id: Unique identifier for the user.
        :param preferences: A dictionary of preferences (e.g., interests, budget).
        """
        with self.driver.session() as session:
            for key, value in preferences.items():
                session.run(
                    """
                    MERGE (u:User {id: $user_id})
                    MERGE (p:Preference {type: $key, value: $value})
                    MERGE (u)-[:PREFERS]->(p)
                    """,
                    user_id=user_id, key=key, value=value
                )

    def get_user_preferences(self, user_id):
        """
        Retrieve all preferences for a given user.
        :param user_id: Unique identifier for the user.
        :return: A dictionary of preferences.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[:PREFERS]->(p:Preference)
                RETURN p.type AS type, p.value AS value
                """,
                user_id=user_id
            )
            return {record["type"]: record["value"] for record in result}

    # Update existing user preference
    def update_user_preference(self, user_id, preference_type, new_value):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $user_id})-[:PREFERS]->(p:Preference {type: $type})
                SET p.value = $new_value
                """,
                user_id=user_id, type=preference_type, new_value=new_value
            )

    # Delete specific user preference
    def delete_user_preference(self, user_id, preference_type):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $user_id})-[:PREFERS]->(p:Preference {type: $type})
                DETACH DELETE p
                """,
                user_id=user_id, type=preference_type
            )

# Example Usage
if __name__ == "__main__":
    db_manager = DatabaseManager(uri="bolt://localhost:7687", username="neo4j", password="password")

    user_id = "user123"
    preferences = {"interests": "culture, adventure", "budget": "100", "city": "Rome"}

    db_manager.store_user_preferences(user_id, preferences)
    user_prefs = db_manager.get_user_preferences(user_id)
    print(f"User Preferences: {user_prefs}")

    db_manager.update_user_preference(user_id, "budget", "150")
    db_manager.delete_user_preference(user_id, "city")
    db_manager.close()