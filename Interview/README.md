# Multi-Agent Document Processing System

A FastAPI-based multi-agent system designed to intelligently process and route different types of business documents (emails, JSON data, PDFs) through specialized agents for extraction, analysis, and automated follow-up actions.

## 🏗️ Architecture Overview

The system follows a modular, agent-based architecture where each component has a specific responsibility:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   Agents        │
│   (React)       │◄──►│   Backend        │◄──►│   System        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Shared Memory   │    │ Action Router   │
                       │   (SQLite)       │    │  (REST Calls)   │
                       └──────────────────┘    └─────────────────┘
```

### Core Components

1. **FastAPI Backend** (`main.py`) - Central orchestrator and API gateway
2. **Agent System** (`agents/`) - Specialized processing units
3. **Shared Memory** (`memory/`) - Centralized data storage and state management
4. **Action Router** - Automated follow-up action dispatcher
5. **Frontend** (`frontend/`) - React-based user interface

## 🤖 Agent System Architecture

### 1. Classifier Agent (`agents/classifier_agent.py`)

**Purpose**: Input format detection and business intent classification

**Logic**:
- **Format Detection**:
  - PDF: Detects `%PDF` byte signature
  - JSON: Validates JSON parsing
  - Email: Looks for email headers (`From:`, `Subject:`)
- **Intent Classification**: Keyword-based matching for:
  - Invoice processing
  - RFQ (Request for Quote) handling
  - Complaint management
  - Regulation compliance
  - General inquiries

**Output**: Classification metadata stored in shared memory

### 2. JSON Agent (`agents/json_agent.py`)

**Purpose**: Process structured JSON data and validate against business schemas

**Logic**:
- **Schema Validation**: Maps input to FlowBit schema format
- **Anomaly Detection**: Identifies missing required fields (`id`, `type`)
- **Alert Generation**: Creates alerts for data anomalies
- **Memory Storage**: Persists extracted fields and alerts

**Key Features**:
- Robust error handling for malformed JSON
- Flexible schema mapping
- Automated anomaly flagging

### 3. Email Parser Agent (`agents/email_parser_agent.py`)

**Purpose**: Extract structured data from email communications and determine appropriate actions

**Logic**:
- **Sender Extraction**: Parses email headers for sender information
- **Intent Analysis**: Keyword-based classification of email purpose
- **Urgency Detection**: Identifies priority levels (High/Medium/Low)
- **Tone Analysis**: Categorizes communication tone:
  - Escalation (angry, threatening)
  - Polite (courteous language)
  - Neutral (standard communication)
- **Action Triggering**: Routes to appropriate CRM actions based on tone/urgency

**Integration**: Works with Action Router for automated follow-up

### 4. PDF Agent (`agents/pdf_agent.py`)

**Purpose**: Extract and analyze content from PDF documents

**Logic**:
- **Text Extraction**: Uses PyPDF for content extraction
- **Invoice Processing**: 
  - Regex-based line item parsing
  - Total calculation and validation
  - High-value transaction flagging (>$10,000)
- **Compliance Detection**: Identifies policy mentions (GDPR, FDA, HIPAA, CCPA)
- **Risk Flagging**: Automated alerts for compliance and financial thresholds

**Output**: Structured data with extracted text, invoice details, and compliance flags

### 5. Action Router (`agents/action_router.py`)

**Purpose**: Execute follow-up actions based on agent outputs

**Logic**:
- **Action Mapping**: Routes to external systems via REST APIs:
  - `crm_escalate`: High-priority customer issues
  - `crm_log`: Standard customer interactions
  - `risk_alert`: Compliance or financial risk notifications
  - `ticket_create`: Support ticket generation
- **Retry Mechanism**: Configurable retry logic with exponential backoff
- **Async Processing**: Non-blocking action execution using threading
- **Result Tracking**: Logs all action attempts and outcomes

## 💾 Shared Memory System

### Database Schema (`memory/shared_memory.py`)

The system uses SQLite for persistent storage with three main tables:

```sql
-- Input classification metadata
metadata (id, source, type, intent, timestamp)

-- Agent processing results
extracted_fields (id, agent, data, timestamp)

-- Conversation tracking
conversations (id, conversation_id, metadata, timestamp)
```

### Key Features:
- **Thread-Safe Operations**: Uses locks for concurrent access
- **JSON Serialization**: Flexible data storage for complex objects
- **Audit Trail**: Complete processing history with timestamps
- **Cross-Agent Communication**: Shared state for agent coordination

## 🔄 Processing Flow

### 1. Input Reception
```
POST /intake/ → FastAPI endpoint receives:
├── file: PDF upload
├── json_body: Structured data
└── email_body: Email content
```

### 2. Classification Phase
```
Classifier Agent analyzes input:
├── Format detection (PDF/JSON/Email)
├── Intent classification (Invoice/RFQ/Complaint/etc.)
└── Metadata storage in shared memory
```

### 3. Agent Routing
```
Based on classification:
├── PDF → PDF Agent
├── JSON → JSON Agent
└── Email → Email Parser Agent
```

### 4. Specialized Processing
```
Each agent:
├── Extracts relevant data
├── Applies business logic
├── Stores results in shared memory
└── Triggers appropriate actions
```

### 5. Action Execution
```
Action Router:
├── Evaluates agent outputs
├── Triggers external system calls
├── Handles retries and failures
└── Logs action results
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend)
- SQLite

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Interview
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

4. **Start the backend**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Start the frontend** (in a new terminal)
```bash
cd frontend
npm start
```

### Docker Deployment

```bash
docker build -t multi-agent-system .
docker run -p 8000:8000 multi-agent-system
```

## 📡 API Endpoints

### POST `/intake/`
Main processing endpoint accepting multipart form data:

**Parameters**:
- `file`: PDF file upload (optional)
- `json_body`: JSON string data (optional)
- `email_body`: Email content text (optional)

**Response**:
```json
{
  "classification": {
    "format": "PDF|JSON|Email",
    "intent": "Invoice|RFQ|Complaint|Regulation|General"
  },
  "extraction": {
    // Agent-specific extracted data
  }
}
```

### OPTIONS `/intake/`
CORS preflight support for frontend integration.

## 🔧 Configuration

### Environment Variables
- `DATABASE_PATH`: SQLite database location (default: `memory.db`)
- `MAX_RETRIES`: Action router retry attempts (default: 3)
- `RETRY_DELAY`: Delay between retries in seconds (default: 2)

### Agent Customization
Each agent can be extended by:
1. Modifying processing logic in respective agent files
2. Adding new action types in `ActionRouter`
3. Extending database schema for additional metadata

## 🧪 Testing

### Backend Tests
```bash
python test_backend.py
python test_api.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

### CORS Testing
Open `test_cors.html` in a browser to verify cross-origin requests.

## 📊 Monitoring and Debugging

### Logging
- Comprehensive logging throughout the system
- Error tracking with stack traces
- Processing time monitoring

### Memory Inspection
Query the SQLite database directly to inspect:
- Processing history
- Agent outputs
- Action results
- Conversation threads

### Debug Endpoints
The system provides detailed error responses and processing logs for troubleshooting.

## 🔮 Future Enhancements

### Planned Features
- **Machine Learning Integration**: Replace rule-based classification with ML models
- **Real-time Processing**: WebSocket support for live document processing
- **Advanced Analytics**: Dashboard for processing metrics and trends
- **Plugin Architecture**: Dynamic agent loading and configuration
- **Multi-tenant Support**: Isolated processing environments

### Scalability Considerations
- **Database Migration**: PostgreSQL for production workloads
- **Message Queuing**: Redis/RabbitMQ for async processing
- **Microservices**: Split agents into independent services
- **Load Balancing**: Horizontal scaling for high-throughput scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the existing documentation
2. Review the agent flow diagram (`agent_flow_diagram.md`)
3. Examine the test files for usage examples
4. Create an issue with detailed reproduction steps

---

*This system demonstrates a practical implementation of multi-agent architecture for document processing, showcasing intelligent routing, specialized processing, and automated action execution in a production-ready FastAPI application.*