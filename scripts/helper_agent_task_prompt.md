Create markdown file with all possible queries and results to agent. Here is all possible @tools/ genearte queries based on that. Here is the script that helps you get results 
@scripts/interact_to_agent_via_api.py based on queries, use it. GUIDE: 0. Generate list of queries for each tool; THEN STEP BY STEP FOR EACH QUERY: 1. Run query to get result; 3. Chat with 
Agent, achieve expecting result based on initial query; 4. collect result-dialog to README.md with initial query and results, dialog steps

USE `1_12_beta` as porfolio_id for test propose

In running script do not forget to retry and ADD THIS:
              if full_response.startswith("ERR::"):
                  raise Exception(full_response)

RUN AND VALIDATE EACH QUERY STEP BY STEP BY YOURSELF, BECAUSE THAT COULD BE ERRORS OR UNEXPECTED RESULTS, YOU HAVE TO CHAT WITH AGENT!!!!!