import json
import random
from typing import Literal, Tuple
from config import settings
from agents import Agent, Runner, SQLiteSession, function_tool, set_default_openai_key, set_trace_processors
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from braintrust import init_logger, load_prompt
from braintrust.wrappers.openai import BraintrustTracingProcessor
from openai import OpenAI

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
    print(f"Extracted skills: {skills}")
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
def get_next_skill_to_evaluate(session_id: str) -> str | None:
    """Retrieve the next skill to evaluate. Returns None if there are no more skills to evaluate"""
    all_skills = db["state"][session_id]["skills"]
    evaluated = db["state"][session_id]["evaluation"]
    evaluated_skills = [item[0] for item in evaluated]
    remaining_skills = set(all_skills) - set(evaluated_skills)
    try:
        next_skill = remaining_skills.pop()
        print("NEXT SKILL TOOL", next_skill)
        return next_skill
    except KeyError:
        print("No more skills")
        return None

ORCHESTRATOR_SYSTEM_PROMPT = """
{RECOMMENDED_PROMPT_PREFIX}

You are an interview orchestrator. Your goal is to evaluate the candidate on the required skills.

# INSTRUCTIONS

Follow the following steps exactly

1. Extract key skills from the job description using extract_skills tool
2. Then welcome the candidate, explain the screening process and ask the candidate if they are ready 
3. Then, use the get_next_skill_to_evaluate tool to get the skill to evaluate
4. If the skill is not `None` then hand off to the "Skills Evaluator Agent" to perform the evaluation. Pass in the skill to evaluate
4. Once you get the response, use the update_evaluation tool to save the evaluation result into the database
5. Once get_next_skill_to_evaluate returns `None`, return a json with a single field `status` set to "done" to indicate completion
"""

ORCHESTRATOR_USER_PROMPT = """
Start an interview for the following values:

session_id: {session_id}
job_id: {job_id}

Begin by welcoming the applicant, extracting the key skills, then evaluate each one.
"""

question_bank = {
    "python": {
        "easy": [
            "If `d` is a dictionary, then what does `d['name'] = 'Siddharta'` do?",
            "if `l1` is a list and `l2` is a list, then what is `l1 + l2`?",
        ],
        "medium": [
            "How do you remove a key from a dictionary?",
            "How do you reverse a list in python?"
        ],
        "hard": [
            "If `d` is a dictionary, then what does `d.get('name', 'unknown')` do?",
            "What is the name of the `@` operator (Example `a @ b`) in Python?"
        ]
    },
    "sql": {
        "easy": [
            "What does LIMIT 1 do at the end of a SQL statement?",
            "Explain this SQL: SELECT product_name FROM products WHERE cost < 500'"
        ],
        "medium": [
            "What is a view in SQL?",
            "How do we find the number of records in a table called `products`?"
        ],
        "hard": [
            "What is the difference between WHERE and HAVING in SQL?",
            "Name a window function in SQL"
        ]
    },
    "system design": {
        "easy": [
            "Give one reason where you would prefer a SQL database over a Vector database",
            "RAG requires a vector database. True or False?"
        ],
        "medium": [
            "Give one advantage and one disadvantage of chaining multiple prompts?",
            "Mention three reasons why we may not want to use the most powerful model?"
        ],
        "hard": [
            "Mention ways to speed up retrieval from a vector database",
            "Give an overview of Cost - Accuracy - Latency tradeoffs in an AI system"
        ]
    }
}

@function_tool
def get_question(topic: str, difficulty: Literal['easy', 'medium', 'hard']) -> str:
    """Return a question from the question bank given a topic and the difficulty of the question"""
    questions = question_bank[topic.lower()][difficulty.lower()]
    return random.choice(questions)

@function_tool
def check_answer(skill:str, question: str, answer: str) -> Tuple[bool, str]:
    """Given a question and an answer for a particular skill, validate if the answer is correct. Returns a tuple (correct, reasoning)"""

    prompt = load_prompt(project="Prodapt", slug="check-answer-prompt-0d7c")
    details = prompt.build(skill=skill, question=question, answer=answer)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-5.1", temperature=0,
        response_format=details["response_format"],
        messages=details["messages"]
    )
    return json.loads(response.choices[0].message.content)

EVALUATION_SYSTEM_PROMPT = """
{RECOMMENDED_PROMPT_PREFIX}

You are a specialised skill evaluator. Your job is to evaluate the candidate's proficiency in a given skill

1. Identify which skill you're evaluating (it will be mentioned in the conversation)
2. Use the get_question tool to get a question to ask (start with 'medium' difficulty). Ask the question verbatim, DO NOT MODIFY it in any way
3. After each candidate answer, use check_answer tool to evaluate
4. Decide the next question:
   - If the check_answer tool returned correct, choose the next higher difficulty, without going above 'hard'
   - If the check_answer tool returned incorrect, choose the lower difficulty, without going below 'easy'
   - Stop after 3 questions MAXIMUM
5. If the correctly answered two of the three questions, then they pass, otherwise they fail
6. After completion of 3 questions, hand off to the "Interview Orchestrator Agent" passing in the result of the evaluation

# DECISION RULES:

- Do not give feedback on the user's answer. Always proceed to the next question
- 3 questions per skill

# OUTPUT:

After the evaluation is complete, return the pass/fail in a json object with the following properties
- result: true or false
"""

EVALUATION_USER_PROMPT = """
Evaluate the user on the following skill: {skill}
"""

def run(session_id, job_id):
    session = SQLiteSession(f"screening-{session_id}")
    orchestrator_agent = Agent(
        name="Interview Orchestrator Agent",
        instructions=ORCHESTRATOR_SYSTEM_PROMPT.format(RECOMMENDED_PROMPT_PREFIX=RECOMMENDED_PROMPT_PREFIX),
        model="gpt-5.1",
        tools=[extract_skills, get_next_skill_to_evaluate, update_evaluation]
    )
    evaluation_agent = Agent(
        name="Skills Evaluator Agent",
        instructions=EVALUATION_SYSTEM_PROMPT.format(RECOMMENDED_PROMPT_PREFIX=RECOMMENDED_PROMPT_PREFIX),
        model="gpt-5.1",
        tools=[get_question, check_answer]
    )
    orchestrator_agent.handoffs = [evaluation_agent]
    evaluation_agent.handoffs = [orchestrator_agent]
    user_input = ORCHESTRATOR_USER_PROMPT.format(job_id=job_id, session_id=session_id)
    agent = orchestrator_agent
    while user_input != 'bye':
        result = Runner.run_sync(agent, user_input, session=session, max_turns=20)
        agent = result.last_agent
        print(result.final_output)
        user_input = input("User: ")

def main():
    set_trace_processors([BraintrustTracingProcessor(init_logger("Prodapt", api_key=settings.BRAINTRUST_API_KEY))])
    set_default_openai_key(settings.OPENAI_API_KEY)
    job_id = 1
    session_id = "session123"
    run(session_id, job_id)
    print("FINAL EVALUATION STATE", db)

if __name__ == "__main__":
    main()