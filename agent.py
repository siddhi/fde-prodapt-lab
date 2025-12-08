import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from agents import Agent, Runner, SQLiteSession, function_tool, set_default_openai_key

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

@function_tool
def extract_skills(session_id: str, job_id: int) -> list[str]:
    """Given a job_id, lookup job descriptiona and extract the skills for that job description"""
    job_id = int(job_id)
    job_description = db["job_descriptions"][job_id]
    skills = ["Python", "SQL", "System Design"]
    db["state"][session_id]["skills"] = skills
    print(f"\n📋 Extracted skills: {', '.join(skills)}")
    return skills

@function_tool
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

@function_tool
def transfer_to_skill_evaluator(session_id: str, skill: str) -> bool:
    """This function takes a skill, evaluates it and returns the evaluation result for the skill as a boolean pass / fail"""
    result = True
    print(f"Evaluating skill: {skill}. Result {result}")
    return result

ORCHESTRATOR_SYSTEM_PROMPT = """
You are an interview orchestrator. Your goal is to evaluate the candidate on the required skills.

# INSTRUCTIONS

Follow the following steps exactly

1. Extract key skills from the job description using extract_skills tool
2. Then welcome the candidate, explain the screening process and ask the candidate if they are ready 
3. Then, for EACH skill in the list, use transfer_to_skill_evaluator tool to delegate evaluation
4. Once you get the response, use the update_evaluation tool to save the evaluation result into the database
5. Once all skills are evaluated, mention that the screening is complete and thank the candidate for their time
"""

ORCHESTRATOR_USER_PROMPT = """
Start an interview for the following values:

session_id: {session_id}
job_id: {job_id}

Begin by welcoming the applicant, extracting the key skills, then evaluate each one.
"""

def run_orchestrator_agent(session_id, job_id):
    session = SQLiteSession(f"screening-{session_id}")
    agent = Agent(
        name="Interview Orchestrator Agent",
        instructions=ORCHESTRATOR_SYSTEM_PROMPT,
        model="gpt-5.1",
        tools=[extract_skills, transfer_to_skill_evaluator, update_evaluation]
    )
    user_input = ORCHESTRATOR_USER_PROMPT.format(job_id=job_id, session_id=session_id)
    while user_input != 'bye':
        result = Runner.run_sync(agent, user_input, session=session)
        print(result.final_output)
        user_input = input("User: ")
    return

def main():
    set_default_openai_key(settings.OPENAI_API_KEY)
    job_id = 1
    session_id = "session123"
    run_orchestrator_agent(session_id, job_id)
    print(f"FINAL EVALUATION STATUS: {db['state'][session_id]}")

if __name__ == "__main__":
    main()