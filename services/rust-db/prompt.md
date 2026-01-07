You're in a bootstrapped rust project.

Your job is to build a simple KV database using Rust and axum as a web server, the database should be backed by PostgreSQL.

All opperations are namespaced to a "project" - just a UUID that must be included in the URL.

All keys should have:
* name/path
* mime-type
* content

The endpoints should be as follows:

- GET /project/{project}/get/{key} - Retrieve the value associated with the given key
- GET /project/{project}/list/{key-prefix} - List all keys that start with the given prefix, returning path and mime-type
- POST /project/{project}/{key} - Store the given value associated with the given key
- DELETE /project/{project}/{key} - Delete the key-value pair associated with the given key
- POST /project/new - Create a new project, returns a UUID

There are no permissions initially, any user can perform any operation.

Run `make lint` after making changes to make sure the code is clean and follows best practices.

Plan this application, look up the docs of all the libaries, you need to confirm you have the right plan.

Also write a Python file test_node_build.py which uses pytest and requests to test the functionality, do not run it, return once it's written. NEVER use class based tests, all tests should be top level functions. Make sure the python code targets Python 3.14 and ALWAYS uses new style type hints. Use `uv add --script test_node_build.py pytest requests` to add inline dependencies, also add `if __name__ == '__main__': pytest.main()` to run tests on running the script.
