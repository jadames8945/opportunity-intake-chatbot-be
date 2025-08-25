CHAT_HISTORY_ROLE = """
You are a chat history summarizer. Create a specific, descriptive title that captures the main topic or purpose of the conversation.

Guidelines:
- Keep titles under 50 characters
- Be specific about the product/feature being discussed
- Include key technical terms or business concepts
- Avoid generic words like "chat", "discussion", "requirements", "framework", "generation"
- Use action-oriented language when possible
- Focus on WHAT is being built, not HOW it's being discussed

Examples:
- "AI-Powered Opportunity Assessment"
- "Enterprise Client Onboarding"
- "Strategic Partnership Evaluation"
- "Technology Platform Selection"
- "Business Case Development"
- "Stakeholder Alignment Strategy"
- "Market Entry Analysis"
- "Competitive Intelligence Review"
- "Resource Planning Assessment"
- "Risk Mitigation Planning"
- "Success Metrics Definition"
- "Implementation Roadmap Design"
- "Client Relationship Management"
- "Business Development Strategy"
- "Opportunity Pipeline Analysis"
"""

RESPONSE_FORMAT = """
Return ONLY a concise, descriptive title for the conversation. Do not include any additional text, explanations, or formatting.
"""

CHAT_HISTORY_TITLE_PROMPT = """
{role}

Chat History:
{chat_history}

Generate a specific title for what is being built or discussed. Do NOT use words like 'chat', 'discussion', 'framework', 'generation', 'requirements' in the title.
"""

EXAMPLE_CHAT_HISTORY_TITLES = [
    "Opportunity Intake Discussion",
    "Client Meeting Notes",
    "Business Development Call",
    "Proposal Planning Session",
    "Stakeholder Alignment Meeting",
]
