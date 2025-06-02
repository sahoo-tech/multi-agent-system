# Multi-Agent System Flow and Chaining Diagram

This document describes the flow and chaining of agents in the multi-agent system.

## Overview

User inputs (Email, JSON, PDF) are received by the backend `/intake/` endpoint. The system performs the following steps:

1. **Classifier Agent**
   - Detects input format: JSON, Email, PDF
   - Detects business intent: RFQ, Complaint, Invoice, Regulation, Fraud Risk
   - Passes classification metadata to shared memory

2. **Routing to Specialized Agents**
   - Based on classification, routes input to:
     - Email Agent
     - JSON Agent
     - PDF Agent

3. **Specialized Agents Processing**
   - **Email Agent**
     - Extracts structured fields: sender, urgency, issue/request
     - Identifies tone (escalation, polite, threatening)
     - Triggers action based on tone and urgency (e.g., escalate to CRM)
   - **JSON Agent**
     - Parses webhook data
     - Validates schema fields
     - Flags anomalies and logs alerts
   - **PDF Agent**
     - Extracts fields using PDF parsing
     - Parses invoice line items or policy documents
     - Flags high invoice totals or policy mentions

4. **Shared Memory Store**
   - All agents read/write metadata, extracted fields, and action traces

5. **Action Router**
   - Based on agent outputs, triggers follow-up actions via REST calls
   - Actions include creating tickets, escalating issues, flagging compliance risks
   - Includes retry logic for failed actions

## Flow Diagram (Textual)

```
User Input (Email/JSON/PDF)
        |
        v
+-------------------+
| Classifier Agent  |
+-------------------+
        |
        v
+-------------------+
| Routing Decision   |
+-------------------+
        |
        +-------------------+-------------------+-------------------+
        |                   |                   |
        v                   v                   v
+---------------+   +---------------+   +---------------+
| Email Agent   |   | JSON Agent    |   | PDF Agent     |
+---------------+   +---------------+   +---------------+
        |                   |                   |
        v                   v                   v
+-------------------------------------------------------+
|                Shared Memory Store                    |
+-------------------------------------------------------+
        |
        v
+-------------------+
| Action Router     |
+-------------------+
        |
        v
+-------------------+
| Follow-up Actions |
+-------------------+
```

## Notes

- The system supports dynamic chaining of actions based on extracted data.
- The UI allows users to upload inputs and view routing and processing results.
- The entire system is containerized using Docker for easy deployment.
