import time
import requests
import threading

class ActionRouter:
    def __init__(self, memory, max_retries=3, retry_delay=2):
        self.memory = memory
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _trigger_action_sync(self, action_type, payload):
        """
        Simulate triggering a follow-up action via REST call.
        Retries on failure up to max_retries.
        Logs action and result in shared memory.
        """
        url_map = {
            "crm_escalate": "http://example.com/crm/escalate",
            "crm_log": "http://example.com/crm/log",
            "risk_alert": "http://example.com/risk_alert",
            "ticket_create": "http://example.com/ticket/create"
        }

        url = url_map.get(action_type)
        if not url:
            result = {"error": f"Unknown action type: {action_type}"}
            self.memory.add_extracted_fields("ActionRouter", result)
            return result

        attempt = 0
        while attempt < self.max_retries:
            try:
                response = requests.post(url, json=payload, timeout=5)
                if response.status_code == 200:
                    result = {"status": "success", "action": action_type, "payload": payload}
                    self.memory.add_extracted_fields("ActionRouter", result)
                    return result
                else:
                    attempt += 1
                    time.sleep(self.retry_delay)
            except Exception as e:
                attempt += 1
                time.sleep(self.retry_delay)

        # After retries failed
        result = {"status": "failed", "action": action_type, "payload": payload}
        self.memory.add_extracted_fields("ActionRouter", result)
        return result

    def trigger_action(self, action_type, payload):
        # Run the synchronous trigger in a background thread to avoid blocking
        thread = threading.Thread(target=self._trigger_action_sync, args=(action_type, payload))
        thread.daemon = True
        thread.start()
        return {"status": "triggered_async", "action": action_type}
