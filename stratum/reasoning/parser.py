import json
import logging
from typing import Dict, Any, Optional

class UpdateParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extracts and parses JSON from the LLM response.
        Handles potential markdown formatting (e.g. ```json ... ```).
        """
        try:
            # Clean markdown if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            data = json.loads(cleaned)

            # Ensure basic structure
            if not isinstance(data, dict):
                raise ValueError("LLM response is not a JSON object")

            if "entities" not in data and "relations" not in data:
                # If it's a single entity update, wrap it
                if "id" in data and "type" in data:
                    return {"entities": [data]}
                else:
                    self.logger.warning("LLM response lacks 'entities' or 'relations' keys")

            return data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode LLM JSON: {e}")
            self.logger.debug(f"Raw response: {response_text}")
            raise ValueError(f"Invalid JSON format from LLM: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            raise
