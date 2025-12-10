# Lab 18: Observability

In this lab, we will integrate the OpenAI Agents SDK with Braintrust Observability tool

## Sign up for Braintrust

1. Sign up for Braintrust free plan - https://www.braintrust.dev/pricing
1. You will be asked to create an organisation. Create one in your name
1. After sign up it will ask if you want to add tracing for an existing application. Select that option and it will show you your API key. Copy it.
1. Rename the default project to "Prodapt"

## Configure the app

1. Update `requirements.txt` with `braintrust[openai-agents]==0.3.12` and install the requirements
1. To the `.env` file add `BRAINTRUST_API_KEY=...`
1. Update `config.py` and add the setting `BRAINTRUST_API_KEY: str`
1. Open `agent.py`

Add these imports

```python
from agents import set_trace_processors
from braintrust import init_logger
from braintrust.wrappers.openai import BraintrustTracingProcessor
```

The in the `main()` function configure the tracing. (Assuming that the name of the project in Braintrust is "Prodapt")

```python
set_trace_processors([BraintrustTracingProcessor(init_logger("Prodapt", api_key=settings.BRAINTRUST_API_KEY))])
```

Run the agents app and see the traces in the UI
