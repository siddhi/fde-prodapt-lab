# Lab 10: Synthetic Data Generation

We have manually selected a few examples for our test samples, but that is not enough. Ideally we want around 100 test samples.

## Step 1: Scenario Creation

The evaluation samples that we have are mainly developer roles. This is not diverse enough. We might have all sorts of jobs on our system, like teachers or factory supervisors. We need to ensure our test sample set is diverse so we can evaluate with many different possibilities.

To do that, we need to come up with the different dimensions that might affect the job descriptions.

For example, the Industry might be one dimension -- It could be Technology, Education, Manufacturing, Marketing etc

Another dimension might be the length of the description: less than 100 words, 100 to 500 words, more than 500 words

Like this, there will be many dimensions, each dimension will have some possible values.

1. Normally, we will talk to the customer / user / domain expert to understand this better. For this lab, discuss with your partner and come up with three more dimensions along with 3-5 values per dimension
1. Then randomly select about 50 combinations of samples. Example, one combination may be: (Marketing, less than 100 words, X, Y, Z). You can prompt ChatGPT to generate these combinations if you want

## Step 2: Data Generation

Now that we have the list of tuples, we need to ask ChatGPT to generate one job description for each tuple. It has to generate the job description that follows the style given in the tuple

By the end, we should have 50 synthetic data samples

## Hints

### What prompt can I give ChatGPT to generate the scenarios?

<details>
<summary>Answer</summary>

```
I am designing a Application Tracking System and want to test it with a diverse set of user scenarios. Please generate 50 unique combinations (tuples) using the following key dimensions and their possible values: 

- Industry: Technology, Marketing, Manufacturing, Teaching, Medicine, Shipping 
- Length: Less than 100 words, 100 to 500 words, more than 500 words 
- Language: Easy to understand, biased language, confusing, jargon heavy 
- Type: Onsite, Remote, Hybrid 
- Seniority: Fresher, Mid Level, Executive 

Each combination should select one value from each dimension. Present the results as a list of tuples, where each tuple contains one value for each dimension in the following order: (Industry, Length, Language, Type, Seniority). Ensure that the combinations are varied and realistic.
```
</details>

### What prompt can I give ChatGPT to generate the synthetic data?

<details>
<summary>Answer</summary>

```
Convert these dimension combinations into realistic job descriptions for an application tracking system. 

Include variations in: 
- Structuring (Free text vs structured with headings) 
- Common typos 
- Natural language patterns 
- Realistic context and urgency 

Include only 1 example per dimension_example. 

<dimension_examples>
{put the tuples here}
</dimension_examples>
```
</details>
