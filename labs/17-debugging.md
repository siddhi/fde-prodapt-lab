# Lab 17: Debugging

When we run the agent, we see that it only asks one question about a skill. Then it goes on to the next skill.

In this lab, we are going to use `mitmproxy` to see what exactly open ai agents SDK is doing, and use that to debug our agent.

## Setting up mitmproxy

1. Install `mitmproxy` - https://www.mitmproxy.org/
1. Then, open terminal and run this command: `pip install -U certifi`
1. If you are on windows, additionally run `pip install -U python-certifi-win32`
1. Open a terminal and run `mitmweb` to start the web interface
1. Configure the proxy settings to point to host `127.0.0.1` and port `8080`. In windows this is in `Settings -> Network & Internet -> Proxy -> Manual Proxy Setup`
1. Open the browser and go to `http://mitm.it`
1. Follow the instructions there to configure the certificates for your operating system
1. Go to any site like `https://www.google.com`. It should show the page on the browser
1. You should be able to see the flow on the mitm dashboard

## High Level Overview

This is how the system is supposed to behave:

Orchestrator Agent
 - Extract Skills
 - User to say "start"
 - Get next skill to evaluate
 - Hand off to Evaluator Agent

Evaluator Agent
  - get question from tool
  - Ask question
  - User to answer
  - check answer from tool
  - Repeat for question 2 and 3
  - Hand off to Orchestrator Agent

Orchestrator Agent
  - Update database with evaluation result
  - Repeat for skill 2 and 3
  - Return `{"status": "done"}`

1. Start `mitmproxy`
1. Run the agent
1. See the requests that Agents SDK is making to the API
1. Identify what is going wrong
1. Fix the code
1. Run the agent

## Hints

### What is the problem in the code?

<details>
<summary>Answer</summary>

If you see the request in mitmproxy you will notice that when the evaluation agent asks the question and the user replies, the code is running the orchestrator agent with the answer.

The answer is supposed to be processed by the evaluator agent
</details>

### How do I make the fix?

<details>
<summary>Answer</summary>

Add the line `agent = result.last_agent` after the `run_sync` call. This will ensure that the next time we will continue conversation with the agent that replied previously

```python
    result = Runner.run_sync(agent, user_input, session=session, max_turns=20)
    agent = result.last_agent
```
</details>
