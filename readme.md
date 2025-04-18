# Topper3418 - Planner

A note taking assistant that takes disjointed notes and organizes them
into todos, actions, curiosities and observations.

## Installation

### Wonderful Helpful Mother/Father intallation

If you are an experienced programmer, you may skip this step.

1) Open CLI (command line interface). My preferred way is by pressing Command 
\+ spacebar and typing "terminal" and pressing enter. This will open the terminal.

2) install the latest version of Homebrew. This is a package manager, you can
think of it as the app store for your CLI. Install by pasting the following command
into the terminal and pressing enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3) Use homebrew to install python. This is the programming language that this 
project runs on. Paste the following command into the terminal and press enter:

```bash
brew install python@3.11
```

4) Use homebrew to install pip. This is the package manager for python (last package manager 
I promise). Paste the following command into the terminal and press enter:

```bash
brew install pip
```

5) Use homebrew to install git. You likely already have it but just to be sure, paste
the following command into the terminal and press enter:

```bash
brew install git
```

6) You're all caught up! proceed to the normal installation

### Normal installation

1) Clone the repository. This will create a local copy of the project on your computer.
   Paste the following command into the terminal and press enter:

```bash
git clone https://github.com/topper3418/planner.git
```

2) Navigate to the project directory. This will change your current working directory
   to the project directory. Paste the following command into the terminal and press enter:

```bash
cd planner
```

3) Create a virtual environment. This will create a isolated environment for the project
   so that it doesn't interfere with other projects. Paste the following command into the
   terminal and press enter:

```bash
python3 -m venv venv
```

4) Acquire an XAI API token. This can be done at their console at
   https://console.x.ai/team/2134b8bb-7660-4c9b-949a-8a1e2c5cd6ad. Else, you can ask your
   son to text one to you.

5) If you are running windows, you'll have to google it or use Windows Subsystem for Linux.
   On mac/linux, add the following line to the end of the .bashrc file, replacing <api key> with the
   API key you acquired in the previous step:

   ```bash
   export XAI_API_KEY=<api key>
   ```
   
   If you are uncomfortable editing it in the command line, run the command (mac)

   ```bash
   open .bashrc
   ```

   then you can make the edits and save

7) Load the .bashrc file. This will load the virtual environment and load helpful aliases
   for running the project. You'll use this command each time you start a new session with
   the planner. Paste the following command into the terminal and press enter:

```bash
source .bashrc
```

7) Use the pip package manager to install the requirements. This will install all the
   packages needed for the project. Paste the following command into the terminal and
   press enter:

```bash
pip install -r requirements/prod.txt
```

That's it! You are now ready to use the project. 

## Usage

### CLI

The main method for running the application is via the CLI. With your current working
directory set to the project directory, initialize the virtual environment and load 
helpful aliases by pasting the following command into the terminal and pressing enter:

```bash
source .bashrc
```

Then, you can run the following commands:

    - Planner - root CLI, can use the --help flag for more info

    - nn - new note, creates a new note stamped with the current time

    - notes - displays notes

    - todos - displays todos

    - observations - displays observations

    - curiosities - displays curiosities

    - cycle - cycles the engine, which processes the notes and creates the
      derivative objects

For each of these commands, you can use the --help flag to see more information

#### My setup

I like to use the terminal with two tabs:

- One tab for the CLI, where I run the commands

- One tab where I run

    ```bash
    cycle -c
    ```

This will run the engine in the background, and I can see the output by 
navigating to that tab.

## Features

### Database

The Sqlite3 Database is located in data/notes.db stores categories, notes,
annotations, actions, todos and commands. The mapping to it is done via
pydantic objects. The notes can be added via the cli, and the rest of the
database manipulation can be done by acessing it with sqlite3

### Engine

The engine is designed to run as a background process. From the CLI, it
can be run a single time, untill there are no further notes to process

### CLI

The main method for running the application is via the CLI. the .bashrc
file contains the following commands:

    - Planner - root CLI, can use the --help flag for more info

    - nn - new note, creates a new note stamped with the current time

    - notes - displays notes

    - todos - displays todos

    - observations - displays observations

    - curiosities - displays curiosities

## License

"This project is licensed under CC BY-NC 4.0. You are free to use, modify,
and share the code for non-commercial purposes, provided you give appropriate
credit. Only the original author (Travis Opperud) may create and sell commercial
versions of this software, such as iOS apps on the Apple App Store."

## Development Milestones

### Initially Useful

- [ ] records notes

- [ ] categorizes and annotates those notes using an LLM

- [ ] uses those annotations to create todos, actions, and commands

- [ ] uses the commands to modify notes, actions and todos

- [ ] Rest API for creating notes and retrieving todos and actions

- [ ] CLI for creating notes and retrieving todos and actions

- [ ] use the LLM to create summaries of your day/week

### More flexible

- [ ] a single note spawns multiple annotations, allowing
for more complex notetaking

### More usable

- [ ] you can retrieve notes from the REST API

- [ ] UI that allows the user to see all the db objects at once.
Could be web, could be local like tkinter

### More powerful

- [ ] Todo dependency. Todos could/should have prerequisites,
and then the prerequisites should be listed in the todos as a tree

- [ ] Tags. the user should create tags which are implemented in
the annotation step. Then they users can apply filters to each
object type and summarize particular projects from one notebook
