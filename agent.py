import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings

db = {
    "job_descriptions": {
        1: "I need an AI Engineer who knows langchain"
    },
    "state": {
        "session123": {
            "skills": [],
            "evaluation": []
        }
    }
}


def extract_skills(session_id: str, job_id: int) -> list[str]:
    """Given a job_id, lookup job descriptiona and extract the skills for that job description"""
    job_id = int(job_id)
    job_description = db["job_descriptions"][job_id]
    skills = ["Python", "SQL", "System Design"]
    db["state"][session_id]["skills"] = skills
    print(f"\n📋 Extracted skills: {', '.join(skills)}")
    return skills
  
def update_evaluation(session_id: str, skill: str, evaluation_result: bool) -> bool:
    """This function takes the session_id, skill, and the evaluation result and saves it to the database. Returns success or failure (bool)"""
    try:
        print(f"Saving to DB: {skill} - {evaluation_result}")
        if isinstance(evaluation_result, str):
            evaluation_result = True if evaluation_result == "True" else False
        db["state"][session_id]["evaluation"]. append((skill, evaluation_result))
        return True
    except KeyError:
        return False

def transfer_to_skill_evaluator(session_id: str, skill: str) -> bool:
    """This function takes a skill, evaluates it and returns the evaluation result for the skill as a boolean pass / fail"""
    result = True
    print(f"Evaluating skill: {skill}. Result {result}")
    return result

tools_mapping = {
    "extract_skills": extract_skills,
    "update_evaluation": update_evaluation,
    "transfer_to_skill_evaluator": transfer_to_skill_evaluator
}

ORCHESTRATOR_SYSTEM_PROMPT = """
You are an interview orchestrator. Your goal is to evaluate the candidate on the required skills.

# INSTRUCTIONS

Follow the following steps exactly

1. Extract key skills from the job description using extract_skills tool
2. Then welcome the candidate, explain the screening process and ask the candidate if they are ready 
3. Then, for EACH skill in the list, use transfer_to_skill_evaluator tool to delegate evaluation
4. Once you get the response, use the update_evaluation tool to save the evaluation result into the database
5. Once all skills are evaluated, mention that the screening is complete and thank the candidate for their time

# OUTPUT FORMAT

Output as a JSON following the JSON schema below:

```
{{
    "type": "object",
    "properties": {{
        "response": {{ "type": "string" }}
        "tool_name": {{ "type": "string"}},
        "tool_params": {{
            "type": "array",
            "items": {{
                "type": "object",
                "properties": {{
                    "param": {{ "type": "string" }},
                    "value": {{ "type": "string" }}
                }}
            }}
        }}
    }},
    "required": []
}}

Use the "tool_name" and "tool_params" properties to execute a tool and use the "response" property to reply to the user without a tool call. 

# TOOLS

You have access to the following tools

1. `extract_skills(session_id: str, job_id: int) -> list[str]`

Given a job_id, lookup job descriptiona and extract the skills for that job description

2. `update_evaluation(session_id: str, skill: str, evaluation_result: bool) -> bool`

This function takes the session_id, skill, and the evaluation result and saves it to the database. Returns success or failure (bool)

3. `transfer_to_skill_evaluator(session_id, skill: str) -> bool`

This function takes a skill, evaluates it and returns the evaluation result for the skill as a boolean pass / fail
"""

ORCHESTRATOR_USER_PROMPT = """
Start an interview for the following values:

session_id: {session_id}
job_id: {job_id}

Begin by welcoming the applicant, extracting the key skills, then evaluate each one.
"""

def run_orchestrator_agent(session_id, job_id):
    llm = ChatOpenAI(model="gpt-5.1", temperature=0, api_key=settings.OPENAI_API_KEY)
    messages = [
        ("system", ORCHESTRATOR_SYSTEM_PROMPT),
        ("human", ORCHESTRATOR_USER_PROMPT),
    ]
    user_reply = ""
    while user_reply != "bye":
        orchestrator_prompt = ChatPromptTemplate.from_messages(messages)
        orchestrator_chain = orchestrator_prompt | llm
        output = orchestrator_chain.invoke({"job_id": job_id, "session_id": session_id})
        data = json.loads(output.content)
        print(f"Output by LLM: {data}")
        if "response" in data:
            print(data["response"])
        if "tool_name" in data and data["tool_name"] != "":
            tool_name = data["tool_name"]
            params = {param["param"]: param["value"] for param in data["tool_params"]}
            tools = tools_mapping[tool_name]
            tool_output = tools(**params)
            print(f"TOOL OUTPUT = {tool_output}")
            messages.append(("assistant", output.content.replace("{", "{{").replace("}", "}}")))
            messages.append(("ai", str(tool_output)))
        else:
            user_reply = input("User: ")
            messages.append(("human", user_reply))

def main():
    job_id = 1
    session_id = "session123"
    run_orchestrator_agent(session_id, job_id)
    print(f"FINAL EVALUATION STATUS: {db['state'][session_id]}")

if __name__ == "__main__":
    main()