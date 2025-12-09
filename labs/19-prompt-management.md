# Lab 19: Prompt Management

In this lab, we will create a prompt in Braintrust, and then in our code we will read it and use it.

The prompt we are going to configure is the `VALIDATION_PROMPT` that is used to check if the answer provided by the user is correct or not.

## High Level Overview

1. Go the the prompt dashboard, and click the `Prompts` section on the left
1. Create a prompt
  - Name: Check Answer Prompt
  - Slug: `check-answer-prompt-0d7c`
  - Output type: Structured output
    - boolean field `correct`
    - string field `reasoning`

Set this prompt

```
Evaluate the given interview answer. 

Be rigorous but fair. Look for technical accuracy and clarity. 

# Task

Skill: {{skill}} 
Question: {{question}} 
Answer: 
{{answer}}

Evaluation:
```

1. Click `Save new custom prompt` button on the top right
1. In `agents.py`, rewrite the function `check_answer` to use this prompt from braintrust
  - Use `load_prompt` function
  - Directly use OpenAI chat completions to perform the call (no langchain)
  - Documentation: https://www.braintrust.dev/docs/core/functions/prompts#load-a-prompt

## Hints

### How do I implement check_answer?

<details>
<summary>Answer</summary>

```python
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
```
</details>