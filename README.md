# Scaffold CLI

A command-line tool to manage project folders in `~/Documents/Projects`.

## Features

- Create project folders with name validation
- Delete project folders with confirmation
- Create Python 3.12 virtual environments in new project folders
- List all existing projects

## Installation

Make the script executable:

```bash
chmod +x scaffold.py
```

### Option 1: Using an alias in your shell configuration

For easier access, you can add an alias to your shell configuration file (e.g., `.zshrc` or `.bashrc`):

```bash
echo 'alias scaffold="python3 $HOME/Documents/Projects/scaffold/scaffold.py"' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: Using the "go" command (Recommended)

To make the script available globally as the `go` command, add this function to your shell configuration file (e.g., `.zshrc`):

```bash
# Add this to your ~/.zshrc file
function go {
  python3 "$HOME/Documents/Projects/scaffold/scaffold.py" "$@"
}
```

Then reload your shell configuration:

```bash
source ~/.zshrc
```

Now you can use the shorter `go` command from anywhere:
```bash
go create my_project --env
go list
go delete project_name
```

## Usage

### Create a new project

```bash
scaffold create my_project
```

### Create a new project with a Python 3.12 virtual environment

```bash
scaffold create my_python_project --env
```

### Delete a project

```bash
scaffold delete my_project
```

### List all projects

```bash
scaffold list
```

## Project Structure

Projects are created in the `~/Documents/Projects` directory. If a virtual environment is requested, it will be created in a `venv` subdirectory within the project folder.
