# Lab 4: AI Correction (Backend + Frontend)

In this lab, we will add AI correction workflow.

We need to update the code to use the full sequence of 3 prompts:

- Prompt 1: Identify problems in job description (Lab 3)
- Prompt 2: Rewrite parts of the job description
- Prompt 3: Fix the original job description

Here are the steps to implement this lab:

1. Update the `review_application` function in `ai.py` to pass the output of prompt 1 into the second prompt and then the third prompt.
1. Make the API return the rewritten job description along with the overall summary
1. Update the frontend to read the rewritten description along with the summary
1. When the summary is displayed, also display a button "Fix for me"
1. When the `Fix for me` button is clicked, take the rewritten description and put it in the description textarea

**Note:** `gpt-5.1` which we used in lab 3 is a slow model. Because we are going to do three prompts in series, it can take up to 60 seconds to process. For that reason, for this lab update the model to `gpt-5.1-chat-latest` (GPT 5.1 Instant) which is a faster model without reasoning. 

## High Level Approach

1. First work on the backend. Start by updating the LLM model to `gpt-5.1-chat-latest`
1. Just like `analysis_chain` we need to also create a `rewrite_chain` and `finalise_chain`. Note that `finalise_chain` output is a text, so there is no output parsing required
1. Invoke `rewrite_chain` with the two inputs - Job description and output from first chain. Use `analysis.json()` to convert the output from first chain to JSON format and use that as the input
1. Invoke `finalise_chain` with the inputs - Job description and output from rewrite chain
1. Update `ReviewedReviewedApplication` class to add a `revised_description` field (type `str`). Then fill both fields when returning the output
1. Test backend with Bruno
1. Now we can come to the frontend. Our API is returning the fixed description along with the summary. Create a state variable `revisedDescription` to store it using `useState` (initial value empty string)
1. When the review api returns, update the state variable with the value from the API
1. Add a button below the summary. Label it `Fix for me`
1. Use `useRef` to create a reference variable. Set the reference to the textarea
1. Create a click handler function. This function will set the `revisedDescription` value to the text area
1. Update the button to set the click handler function for the `onClick` event

## Hints

### What are the prompts for the rewrite chain?

<details>
<summary>Answer</summary>

```python
REWRITE_SYSTEM_PROMPT = """
You are an expert HR editor specializing in rewriting job descriptions for clarity, inclusivity,
and accessibility.

You will receive:
1. The original job description.
2. A structured analysis of issues found in Step 1.

Your task is to rewrite ONLY the problematic sections, not the entire job description.

For each identified issue:
- Include the original problematic text (quoted exactly)
- Include the category (clarity, jargon, bias, or missing_information)
- Provide an improved, inclusive alternative that preserves meaning
- Maintain neutral, professional tone
- Ensure suggestions follow inclusive hiring practices

Return ONLY valid JSON matching the provided schema. Do not write any prose outside JSON.
"""

REWRITE_USER_PROMPT = """
Original Job Description:
-------------------------
{job_description}

Analysis Findings:
------------------
{analysis_json}

Rewrite ONLY the problematic sections using the schema.
Return only JSON.

{format_instructions}
"""
```
</details>

### What is the output format for the rewrite chain?

<details>
<summary>Answer</summary>

```python
class RewrittenSection(BaseModel):
    category: Literal["clarity", "jargon", "bias", "missing_information"]
    original_text: str
    issue_explanation: str
    improved_text: str

class JDRewriteOutput(BaseModel):
    rewritten_sections: List[RewrittenSection]
```
</details>

### What are the prompts for the finalise chain?

<details>
<summary>Answer</summary>

```python
FINALISE_SYSTEM_PROMPT = """
You are an expert HR writer specializing in creating clear, concise, and inclusive job descriptions.

Your job is to produce the final polished version of the job description.

You will receive:
1. The original job description.
2. A list of rewritten sections (from Step 2).

Your tasks:
- Incorporate all improved rewritten sections into the original job description.
- Remove or replace the problematic text that was flagged in earlier steps.
- Maintain the original intent, structure, and role scope.
- Ensure clarity, inclusivity, and accessibility.
- Make tone consistent: professional, warm, and concise.
- Improve flow and readability where necessary.
- Do NOT invent new responsibilities, requirements, or benefits.

Return ONLY the final polished job description as plain text. Do not include JSON.
"""

FINALISE_USER_PROMPT = """
Original Job Description:
-------------------------
{job_description}

Rewritten Sections:
-------------------
{rewritten_sections_json}

Create the final polished job description by integrating the improvements.
Return only the final text.
"""
```
</details>

### What is the output format for the finalise chain?

<details>
<summary>Answer</summary>

Nothing! Finalise chain output is plain text
</details>

### How do I create the rewrite chain? 

<details>
<summary>Answer</summary>

```python
rewrite_parser = PydanticOutputParser(pydantic_object=JDRewriteOutput)
    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", REWRITE_SYSTEM_PROMPT),
        ("human", REWRITE_USER_PROMPT),
    ]).partial(format_instructions=rewrite_parser.get_format_instructions())
    rewrite_chain = rewrite_prompt | llm | rewrite_parser
```
</details>

### How do I invoke the rewrite chain? 

<details>
<summary>Answer</summary>

```python
    rewrite = rewrite_chain.invoke({"job_description": job_description, "analysis_json": analysis.json()})
```
</details>

### How do I create / invoke the finalise chain?

<details>
<summary>Answer</summary>

Just like the rewrite chain above, except finalise chain does not have output parser
</details>

### What should I return from review_applications?

<details>
<summary>Answer</summary>

First, update the return model

```python
class ReviewedApplication(BaseModel):
    revised_description: str
    overall_summary: str
```

Then fill in both fields and return

```python
    revised_description = final_output.text
    overall_summary = analysis.overall_summary
    return ReviewedApplication(revised_description=revised_description, overall_summary=overall_summary)
```
</details>

### How do I set the revised description into the state?

<details>
<summary>Answer</summary>

First, create the state variable

```python
const [revisedDescription, setRevisedDescription] = useState("")
```

Then set the value along with the other variables

```python
  if (actionData && reviewed === "false") {
    setSummary(actionData.overall_summary);
    setRevisedDescription(actionData.revised_description)
    setReviewed("true")
  }
```
</details>

### How do I create the reference variable?

<details>
<summary>Answer</summary>

```python
const textareaRef = useRef(null)
```
</details>

### How do I attach the reference to the text area?

<details>
<summary>Answer</summary>

Set the `ref` prop on the node

```python
<Textarea
  id="description"
  name="description"
  ref={textboxRef}
  required
/>
```
</details>

### Where do I add the "Fix for me" button?

<details>
<summary>Answer</summary>

Put it just below the review summary

```python
  {reviewed === "true" ? (
    <div>
    <p>{summary}</p>
    <Button type="button">Fix for me</Button>
    </div>
  ) : <div></div>}
```
</details>

### How do I connect a click handler to the button?

<details>
<summary>Answer</summary>

First, create a click handler function. This function will take the value from the `revisedDescription` state variable and set it to the textarea using the reference variable

```python
  const fix_job_description = () => {
      textboxRef.current.value = revisedDescription
  }
```

Then configure the `onClick` prop on the button

```python
<Button type="button" onClick={fix_job_description}>Fix for me</Button>
```
</details>
