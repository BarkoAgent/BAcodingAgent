# Barko Agent - Coding Agent

To install this you can either use docker or just install all the dependencies for python and then run the code

For this agent to work you need to set `ROOT_TEST` variable to the folder path that has the code project you want to work with. Check .env file, you can modify them there.
For example, if your code is in /Users/your_user/Github/your_awesome_code/ then you should export this env variable like this:

- Linux/MacOS:

        export ROOT_TEST=/Users/your_user/Github/your_awesome_code/

in case you are using the docker configuration, change the `docker-compose.yml` file and instead of:

        volumes:
            - .:/app
            - /SomeFolder/Path:/root_test

put:

        volumes:
            - .:/app
            - /Users/your_user/Github/your_awesome_code:/root_test


## Getting started

To install this you can either use docker or just install all the dependencies for python and then run the code

### Option 1: Install with docker

Just in the main directory you can write:

<pre>
    docker-compose up
</pre>

### Option 2: Install python

Make sure you are using the Python versions 3.9 - 3.12

<pre>
    pip install -r requirements.txt
    python client.py
</pre>


### Set up Barko Agent

Before you run the Agent, you will need to get the `BACKEND_WS_URI`

1. Navigate to https://beta.barkoagent.com/chat
2. Create a new project, and select the `Custom Agent`
3. You will get your unique `uuid4` for that project
4. add the `System Prompt` (we have added sample system prompt for this project in [here](system_prompt.txt))
5. Copy the `uuid4` and save the project.
6. Add you `uuid4` to the .env
7. Run your agent


## Your first prompt

You can test this custom agent by writing:

`List all the file structure`

`What is this project about?`

`What can I improve of the project?`
