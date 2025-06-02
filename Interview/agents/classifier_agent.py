import json
from datetime import datetime

class ClassifierAgent:
    def __init__(self, memory):
        self.memory = memory

    def classify(self, raw_input):
        """
        Dummy classification logic:
        - Detect format: PDF (bytes starting with %PDF), JSON (parseable), Email (text with typical email headers)
        - Detect intent: simple keyword matching
        """
        format_ = "Unknown"
        intent = "Unknown"

        # Detect format
        if isinstance(raw_input, bytes):
            if raw_input.startswith(b'%PDF'):
                format_ = "PDF"
            else:
                try:
                    json.loads(raw_input.decode('utf-8'))
                    format_ = "JSON"
                except Exception:
                    format_ = "Unknown"
        elif isinstance(raw_input, str):
            try:
                json.loads(raw_input)
                format_ = "JSON"
            except Exception:
                # Simple heuristic for email detection
                if "From:" in raw_input or "Subject:" in raw_input:
                    format_ = "Email"
                else:
                    format_ = "Unknown"

        # Detect intent by keyword matching
        text = raw_input if isinstance(raw_input, str) else raw_input.decode('utf-8', errors='ignore')
        text_lower = text.lower()
        if "invoice" in text_lower:
            intent = "Invoice"
        elif "rfq" in text_lower:
            intent = "RFQ"
        elif "complaint" in text_lower:
            intent = "Complaint"
        elif "regulation" in text_lower:
            intent = "Regulation"
        else:
            intent = "General"

        return {"format": format_, "intent": intent}

    def get_timestamp(self):
        return datetime.utcnow().isoformat()
