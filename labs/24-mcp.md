# Lab 24: Bonus: Model Context Protocol

In this lab, we will create an MCP server and connect to it using Bruno

## High level overview

1. Install `fastmcp` package
1. Create a file `mcp_server.py`
1. Create an `add` tool as follows

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        The sum of a and b
    """
    return a + b
```

1. Now similarly create another tool of your choice. 
  - Make sure you put all the types and use descriptive names. 
  - Don't forget to add the documentation string. 
  - The decorator will read all these values and provide it to the client

1. Add code to run the server

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)
```

1. Now run the server in the terminal: ```python mcp_server.py```

Next, we will use Bruno to connect to this server

1. Load the collection which is in the directory `bruno/mcp` into Bruno
1. Make a call to the first API. This API connects to the server and initialises the session
1. The initialisation will return an MCP Session ID in the response headers. Copy it
1. Now call the second API. In the headers, fill in the session ID that you copied from the initialisation
1. Similarly call all the remaining APIs. Understand the input and output formats

These API calls happen in our agent code as well. When we configure the MCP server, openai agents sdk will

- Initialise the session
- Get a list of tools
- These tools will be added to the prompt automatically
- When the LLM returns a tool call, the agent will make a call to the MCP server with the defined parameters to get the response

# Explore Github MCP Server

Github MCP Server is located at url `https://api.githubcopilot.com/mcp`

Use bruno to find which tools are available on Github MCP Server

**Note**: Github MCP Server requires authorisation. Go to Github and create a Personal Access Token (Create it here - https://github.com/settings/personal-access-tokens)

For all calls you will have to add the `Authorization` header with value `Bearer <token>`
