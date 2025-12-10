# Lab 23: Online Scoring

In this lab, we are going to enable our JD scoring judge to review traces as they happen in production.

## High Level Overview

1. In Braintrust, go to project `Configuration` at the bottom of the sidebar
1. Go to "Online Scoring" section and create a new scoring rule
1. Create a rule as follows:
  - Name: JD Structure Eval
  - Scorers: JD Structure Judge (that we created in previous lab)
  - Turn on "Root Spans" and put the name as "Review Job Application" (this should match the custom trace name created in lab 21)
  - Sampling rate 100%
1. Save the rule
1. Now perform the job description review from the UI
1. Come to braintrust logs section and click on the latest "Review Job Application" trace
1. At the bottom of the trace, you should see the judge running on this trace. It will evaluate this trace and calculate the score
1. Later on, traces can be flagged for detailed human review and can be added to evaluation datasets
