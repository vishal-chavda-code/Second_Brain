"""
ChatGPT/OpenAI processor for Second Brain intelligence
"""
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


class ChatGPTProcessor:
    def __init__(self, model: str = "gpt-4.1"):
        self.model = model
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        self.system_prompt = """You are a helpful Second Brain assistant. Your role is to:
1. Help organize and summarize information
2. Extract key insights and action items
3. Connect related ideas and concepts
4. Provide concise, actionable responses
5. Help with task prioritization and planning

Always be concise and focus on actionable insights."""

    def process(self, user_input: str, context: str = None) -> str:
        """Process input through ChatGPT and return response"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if context:
            messages.append({
                "role": "user", 
                "content": f"Context from my notes:\n{context}\n\n---\n\nMy question/request: {user_input}"
            })
        else:
            messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def summarize_notes(self, notes: list) -> str:
        """Summarize a list of notes"""
        notes_text = "\n\n".join([f"- {note}" for note in notes])
        
        prompt = f"""Please summarize these notes and extract key themes and action items:

{notes_text}

Provide:
1. A brief summary (2-3 sentences)
2. Key themes/topics
3. Action items (if any)"""

        return self.process(prompt)

    def extract_tasks(self, text: str) -> str:
        """Extract actionable tasks from text"""
        prompt = f"""Extract all actionable tasks from this text. Format as a numbered list:

{text}"""
        
        return self.process(prompt)

    def categorize_note(self, note_content: str) -> dict:
        """Suggest categories/tags for a note and extract follow-up date if present"""
        from datetime import datetime, timedelta
        
        prompt = f"""Analyze this note and suggest:
1. 2-3 relevant tags/categories
2. A priority level (high/medium/low)
3. Is it actionable? (yes/no)
4. Follow-up date (extract if mentioned - like "tomorrow", "next week", "on Friday", etc. Today is {datetime.now().strftime('%Y-%m-%d, %A')}. Return date in YYYY-MM-DD format or "none")

Note content:
{note_content}

Respond in this exact format:
Tags: tag1, tag2, tag3
Priority: medium
Actionable: yes
FollowUp: 2026-01-15"""

        response = self.process(prompt)
        
        # Parse response
        result = {"tags": [], "priority": "medium", "actionable": False, "follow_up_date": None}
        for line in response.split("\n"):
            if line.startswith("Tags:"):
                result["tags"] = [t.strip() for t in line.replace("Tags:", "").split(",")]
            elif line.startswith("Priority:"):
                result["priority"] = line.replace("Priority:", "").strip().lower()
            elif line.startswith("Actionable:"):
                result["actionable"] = "yes" in line.lower()
            elif line.startswith("FollowUp:"):
                date_str = line.replace("FollowUp:", "").strip()
                if date_str and date_str.lower() != "none":
                    result["follow_up_date"] = date_str
        
        return result

    def generate_daily_summary(self, notes: list, tasks: list = None) -> str:
        """Generate a daily summary from notes and tasks"""
        content = "Today's Notes:\n" + "\n".join([f"- {n}" for n in notes])
        
        if tasks:
            content += "\n\nPending Tasks:\n" + "\n".join([f"- {t}" for t in tasks])
        
        prompt = f"""Based on this information, create a brief daily summary:

{content}

Include:
1. Key accomplishments/insights
2. Priority items for tomorrow
3. Any patterns or observations"""

        return self.process(prompt)

    def answer_question(self, question: str, relevant_notes: list) -> str:
        """Answer a question using context from notes"""
        context = "\n\n".join(relevant_notes) if relevant_notes else "No relevant notes found."
        
        return self.process(question, context=context)


if __name__ == "__main__":
    # Test connection
    processor = ChatGPTProcessor()
    print("✅ ChatGPT processor initialized!")
    
    # Quick test
    response = processor.process("Say 'Second Brain is ready!' in exactly those words.")
    print(f"Test response: {response}")
