import json
from datetime import datetime

class JSONAgent:
    def __init__(self, memory):
        self.memory = memory

    def process(self, raw_json):
        """
        Process arbitrary JSON input:
        - Parse JSON
        - Reformat to FlowBit schema (dummy example)
        - Identify anomalies or missing fields
        - Log alert in memory if anomalies detected
        """
        try:
            if isinstance(raw_json, str):
                data = json.loads(raw_json)
            elif isinstance(raw_json, bytes):
                data = json.loads(raw_json.decode('utf-8'))
            else:
                return {"error": "Invalid input type", "details": f"Expected str or bytes, got {type(raw_json)}"}
        except json.JSONDecodeError as e:
            return {"error": "Invalid JSON format", "details": str(e)}
        except UnicodeDecodeError as e:
            return {"error": "Invalid encoding", "details": str(e)}
        except Exception as e:
            return {"error": "Unexpected error parsing JSON", "details": str(e)}

        # Dummy FlowBit schema example: expecting keys 'id', 'type', 'attributes'
        flowbit_schema = {
            "id": data.get("id"),
            "type": data.get("type"),
            "attributes": data.get("attributes", {})
        }

        missing_fields = []
        for field in ["id", "type"]:
            if flowbit_schema[field] is None:
                missing_fields.append(field)

        anomalies = []
        if missing_fields:
            anomalies.append(f"Missing fields: {', '.join(missing_fields)}")

        # Store extracted fields in shared memory
        try:
            self.memory.add_extracted_fields("JSONAgent", flowbit_schema)
        except Exception as e:
            # Log error but continue processing
            print(f"Warning: Failed to store extracted fields: {e}")

        # Log alert if anomalies detected
        if anomalies:
            try:
                alert = {
                    "alert_type": "JSON Anomaly",
                    "details": anomalies,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.memory.add_extracted_fields("JSONAgent_Alert", alert)
            except Exception as e:
                # Log error but continue processing
                print(f"Warning: Failed to store alert: {e}")

        return {
            "flowbit_schema": flowbit_schema,
            "anomalies": anomalies
        }
