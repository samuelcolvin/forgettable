There is a new bootstrapped python project with pydantic-ai and fastapi added in @services/python-agent

Your job is to build a simple FastAPI app and pydantic-ai agent.

Make sure the python code targets Python 3.14 and ALWAYS uses new style type hints.

The agent should build a simple React (client side only applications) by using tools to:
* create file (file_path: str, content: str)
* edit file (file_path: str, diff: Diff)
* delete file (file_path: str)

it should then return a summary of the app it created and any design decisions. "files" created should be stored in the agent deps, not written to disk.

The instructions for the app should explain the goal and say that:
* all react code should be tsx or typescript
* only react itself and tailwindcss are available as dependencies
* the app should be clearly documented with each function or class having a docstring and any non-trivial logic having a concise explanation comment

The fastapi app should have endpoints for:
* creating a new app (takes prompt, returns files as `dict[str, str]` and summary as `str`)
* edit an existing app (app_id: uuid, takes prompt, files: `dict[str, str]`, returns file diffs as `dict[str, Diff]`)
* delete an existing app (takes app_id: uuid)

Run `make lint` after making changes to make sure the code is clean and follows best practices.

Plan this application, look up the docs of all the libaries, you need to confirm you have the right plan.

In particular, you should review https://ai.pydantic.dev and https://fastapi.tiangolo.com/ to make sure you're using those tools correctly.

Also write a Python file test_python_agent.py which uses pytest and requests to test the functionality. NEVER use class based tests, all tests should be top level functions. add `if __name__ == '__main__': pytest.main()` to run tests on running the script.
