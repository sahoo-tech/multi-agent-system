import re
from datetime import datetime

class EmailParserAgent:
    def __init__(self, memory, action_router=None):
        self.memory = memory
        self.action_router = action_router

    def process(self, email_body):
        """
        Process email body text (plain or HTML):
        - Extract sender name
        - Extract request intent (simple keyword matching)
        - Extract urgency (simple keyword matching)
        - Identify tone (escalation, polite, threatening)
        - Trigger action based on tone + urgency
        - Return formatted CRM-style record
        - Store conversation ID + parsed metadata in memory
        """
        sender = self.extract_sender(email_body)
        intent = self.extract_intent(email_body)
        urgency = self.extract_urgency(email_body)
        tone = self.identify_tone(email_body)
        conversation_id = self.extract_conversation_id(email_body)

        crm_record = {
            "sender": sender,
            "intent": intent,
            "urgency": urgency,
            "tone": tone,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Store extracted fields and conversation metadata in shared memory
        try:
            self.memory.add_extracted_fields("EmailParserAgent", crm_record)
            if conversation_id:
                self.memory.add_conversation(conversation_id, crm_record)
        except Exception as e:
            print(f"Warning: Failed to store email data: {e}")

        # Trigger action based on tone and urgency
        if self.action_router:
            try:
                if tone == "escalation" or urgency == "High":
                    action_result = self.action_router.trigger_action("crm_escalate", crm_record)
                else:
                    action_result = self.action_router.trigger_action("crm_log", crm_record)
                # Log action result in memory
                self.memory.add_extracted_fields("EmailParserAgent_Action", action_result)
            except Exception as e:
                print(f"Warning: Failed to trigger action: {e}")

        return crm_record

    def extract_sender(self, text):
        # Simple regex to extract sender from typical email header "From: Name <email>"
        match = re.search(r"From:\s*(.*)", text, re.IGNORECASE)
        if match:
            sender_line = match.group(1).strip()
            # Extract name if in format Name <email>
            name_match = re.match(r"(.*)<.*>", sender_line)
            if name_match:
                return name_match.group(1).strip()
            return sender_line
        return "Unknown"

    def extract_intent(self, text):
        text_lower = text.lower()
        if "invoice" in text_lower:
            return "Invoice"
        elif "rfq" in text_lower:
            return "RFQ"
        elif "complaint" in text_lower:
            return "Complaint"
        elif "regulation" in text_lower:
            return "Regulation"
        else:
            return "General"

    def extract_urgency(self, text):
        text_lower = text.lower()
        if "urgent" in text_lower or "asap" in text_lower:
            return "High"
        elif "soon" in text_lower or "priority" in text_lower:
            return "Medium"
        else:
            return "Low"

    def identify_tone(self, text):
        text_lower = text.lower()
        if any(word in text_lower for word in ["angry", "threatening", "escalate", "complain"]):
            return "escalation"
        elif any(word in text_lower for word in ["please", "thank you", "kindly"]):
            return "polite"
        else:
            return "neutral"

    def extract_conversation_id(self, text):
        # Simple heuristic: look for "Conversation-ID: <id>" in text
        match = re.search(r"Conversation-ID:\s*(\S+)", text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
