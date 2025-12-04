# Lab 9: Eval Harness

In this lab we are going to build a simple script that can help us with error analysis. We have test cases in `test/job_rewriting_tests.csv`. We need to run out job rewriting component with these inputs and record the outputs in another csv so that we can analyse them for errors.

We will use `pandas` to read / write the csv file.

First, we need to install pandas. Update `requirements.txt`

```
pandas==2.3.3 # For data analysis
```

Then run `pip install -r requirements.txt`

Here are the steps for this lab:

1. Create a script `eval_harness.py` in the root directory
1. Read the csv file with pandas
1. Use `itertuples` to iterate through each row of the dataframe
  - Pass each input to `review_description`
  - Save all `overall_summary` into a list and all `revised_description` into another list
1. Create a `Summary` column with all the summaries
1. Create a `Fixed Description` column with all the revised descriptions
1. Save the dataframe to `eval.output.csv`

Now we are going to do "Open Coding"

1. First discuss with your partner and come up with a common list of expectations -- what are you expecting in a correct output? Decide on 5 points to look for.
1. Open the CSV in excel
1. Read each row of input and output
1. In the last column, write your feedback of the output

Last step is "Axial Coding"

1. Look through your excel sheet feedback and see if there is an error which is repeated in 2-3 rows
1. This is the failure mode you need to fix in your app

At this step you will make some changes to your application, experiment with some prompt changes to fix the failure mode, then repeat the process to see what has changed

## Hints

### How do I read a csv?

<details>
<summary>Answer</summary>

```python
df = pd.read_csv("test/job_rewriting_tests.csv")
```
</details>

### How do I loop through each row?

<details>
<summary>Answer</summary>

```python
for row in df.itertuples()
```

`row[0]` is the row number, `row[1]` will be the job description
</details>

### How do I create a column in the dataframe?

<details>
<summary>Answer</summary>

```python
df["Summary"] = summaries
df["Fixed Description"] = revised_descriptions
```
</details>

### How do I save to csv?

<details>
<summary>Answer</summary>

```python
df.to_csv("eval_output.csv")
```
</details>