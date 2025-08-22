# Opportunity Intake Chatbot - Backend

AI-enabled chatbot backend for streamlining the opportunity intake process for the Digital Products and Innovation team.

## Overview

This backend service provides the AI intelligence and data management for the opportunity intake chatbot, handling conversational flow, data validation, and integration with external systems.

## Features

- AI-driven conversational routing and response generation
- Dynamic question flow based on user responses
- Data validation and intelligent linking
- Integration with Airtable for opportunity tracking
- Multi-table data organization (clients, opportunities, stakeholders, pursuit leads)
- Secure, scalable API architecture

## Tech Stack

- FastAPI
- Python 3.9+
- WebSocket support
- AI/LLM integration
- Airtable API integration
- MongoDB for data storage
- Redis for caching

## Getting Started

```bash
pip install -r requirements.txt
python main.py
```

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `/api/chat/ws/{session_id}` - WebSocket chat endpoint
- `/api/auth/*` - Authentication endpoints
- `/api/configs/*` - Configuration management 