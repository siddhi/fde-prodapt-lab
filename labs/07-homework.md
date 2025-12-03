# Lab 7: Homework

Update the UI to use the new recommendataion system.

Since this is a repeat of frontend / backend, we won't be doing this in the class. You can try it out by yourself as a practise exercise.

## Part 1

We will start by creating a new page to view job details. 

1. Create a new route to view a single job. In the jobs board page, instead of showing apply button and job dscription, link the job title to route to this new page.
    - What should be the URL structure for this new page?
1. Create a backend api to return details of a single job. Input will be job id. Return the job details as well as the list of all applicants for the job - name, email, resume url
1. Update the single job page to get the job id from url, and call this api. Display the job title, job description. Then show the apply button and then the list of all people who have applied for that job.

## Part 2

1. On this page, add a new button called "Get Recommendation". 
1. When the button is clicked, make a call to the recommendations API that we created in previous lab. Display the applicant name and link to the resume on the screen
