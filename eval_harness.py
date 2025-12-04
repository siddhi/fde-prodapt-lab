import pandas as pd
from ai import review_application

def run_input(i, job_description):
    print(f"Processing row {i}")
    return review_application(job_description)

df = pd.read_csv("test/job_rewriting_tests.csv")
results = [run_input(*row) for row in df.itertuples()]
summaries = [result.overall_summary for result in results]
revised_descriptions = [result.revised_description for result in results]
df["Summary"] = summaries
df["Fixed Description"] = revised_descriptions
df.to_csv("eval_output.csv")