#!/usr/bin/env python3
"""
Debug script for the Router Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def test_router():
    """Test the router agent directly"""
    print("🧪 Testing Router Agent Directly")
    print("=" * 40)

    try:
        from app.agent.router_agent import RouterAgent

        print("✅ Successfully imported Router agent")

        agent = RouterAgent()
        print("✅ Successfully created Router agent instance")

        test_queries = [
            "Create opportunity profile for a new client",
            "Hello, how are you?",
            "I have a business opportunity to discuss",
            "Help me think through this opportunity",
            "Generate opportunity profile for a potential deal",
        ]

        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            try:
                result = agent.route_request(query)
                print(f"✅ Router result: {result}")
            except Exception as e:
                print(f"❌ Router error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_router()
