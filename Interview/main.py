import logging
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from agents.classifier_agent import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_parser_agent import EmailParserAgent
from agents.pdf_agent import PDFAgent
from agents.action_router import ActionRouter
from memory.shared_memory import SharedMemory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared memory
memory = SharedMemory('memory.db')

# Initialize action router
action_router = ActionRouter(memory)

# Initialize agents with action router where needed
classifier_agent = ClassifierAgent(memory)
json_agent = JSONAgent(memory)
email_parser_agent = EmailParserAgent(memory, action_router=action_router)
pdf_agent = PDFAgent(memory)

@app.options("/intake/")
async def intake_options():
    return {"message": "OK"}

from fastapi import HTTPException

@app.post("/intake/")
async def intake(
    file: Optional[UploadFile] = None,
    json_body: Optional[str] = Form(None),
    email_body: Optional[str] = Form(None)
):
    try:
        logger.info("Received request at /intake/")
        logger.info(f"file: {file}")
        logger.info(f"json_body: {json_body}")
        logger.info(f"email_body: {email_body}")
        
        # Add CORS headers manually as well
        from fastapi import Response
        from fastapi.responses import JSONResponse

        """
        Intake endpoint accepts either a file (PDF), JSON body, or email body text.
        """
        raw_input = None
        if file:
            raw_input = await file.read()
        elif json_body:
            raw_input = json_body
        elif email_body:
            raw_input = email_body
        else:
            return JSONResponse(status_code=400, content={"error": "No input provided"})

        # Classify input format and intent
        try:
            classification = classifier_agent.classify(raw_input)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return JSONResponse(status_code=500, content={"error": "Classification failed", "details": str(e)})

        # Route to appropriate agent based on classification
        format_ = classification.get("format")
        intent = classification.get("intent")

        # Fix: If format is "Unknown" but input is JSON string, set format to JSON
        import json
        if format_ == "Unknown":
            try:
                json.loads(raw_input if isinstance(raw_input, str) else raw_input.decode('utf-8'))
                format_ = "JSON"
            except Exception:
                pass

        try:
            memory.add_metadata({
                "source": "user_input",
                "type": format_,
                "intent": intent,
                "timestamp": classifier_agent.get_timestamp()
            })
        except Exception as e:
            logger.error(f"Failed to add metadata: {e}")
            # Continue processing even if metadata fails

        # Process based on format with error handling
        try:
            if format_ == "JSON":
                result = json_agent.process(raw_input)
            elif format_ == "Email":
                result = email_parser_agent.process(raw_input)
            elif format_ == "PDF":
                result = pdf_agent.process(raw_input)
            else:
                result = {"error": "Unknown format"}
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            result = {"error": "Processing failed", "details": str(e)}

        # Trigger follow-up actions based on agent outputs if needed
        # For example, if JSON agent detects anomalies, trigger risk alert
        try:
            if format_ == "JSON" and result.get("anomalies"):
                action_router.trigger_action("risk_alert", {"details": result["anomalies"], "timestamp": classifier_agent.get_timestamp()})
        except Exception as e:
            logger.error(f"Action router failed: {e}")
            # Continue processing even if action fails

        response_content = {"classification": classification, "extraction": result}
        response = JSONResponse(content=response_content)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        logger.error(f"Error processing /intake/ request: {e}\\n{tb_str}")
        raise HTTPException(status_code=500, detail="Internal server error")
