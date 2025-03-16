# Scaffold CLI

A command-line tool to manage project folders in `~/Documents/Projects`.

## Features

- Create project folders with validation
- Delete project folders with confirmation
- Create Python 3.12 virtual environments in new project folders
- List all existing projects
- Quick navigation to project directories
- Auto-activation of virtual environments when navigating to projects

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

To make the script available globally as the `go` command, follow these simple steps:

1. **Ensure the wrapper script is executable**:
   ```bash
   chmod +x ~/Documents/Projects/scaffold/go
   ```

2. **Add a single alias to your shell configuration file** (e.g., `.zshrc`):
   ```bash
   # Add this to your ~/.zshrc file
   alias go='source $HOME/Documents/Projects/scaffold/go'
   ```

3. **Reload your shell configuration**:
   ```bash
   source ~/.zshrc
   ```

This simplified approach keeps your shell configuration clean while maintaining all functionality, including directory navigation and virtual environment activation.

> **Note**: The `go` command must be sourced, not executed, to allow for directory changes, which is why we use an alias that sources the script.

Now you can use the shorter `go` command from anywhere:
```bash
go create my_project --env
go list
go delete project_name
go my_project  # This will navigate to the project
```

## Usage

### Quick Navigation to Projects

The simplest way to use the tool is to just provide a project name:

```bash
go my_project
```

This will:
- If `my_project` exists: Automatically navigate to that project directory
- If `my_project` doesn't exist: Ask if you want to create it, and if so, ask if you want a Python virtual environment
- If a virtual environment is found in the project directory or any subdirectory, it will be automatically activated

### Create a new project

```bash
go create my_project
```

### Create a new project with a Python 3.12 virtual environment

```bash
go create my_python_project --env
```

### Delete a project

```bash
go delete my_project
```

### List all projects

```bash
go list
```

## Project Structure

Projects are created in the `~/Documents/Projects` directory. If a virtual environment is requested, it will be created in a `venv` subdirectory within the project folder.
