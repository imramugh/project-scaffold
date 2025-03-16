#!/usr/bin/env python3
"""
Scaffold CLI - A tool to manage project folders in ~/Documents/Projects

This tool allows users to:
1. Create project folders with validation
2. Delete project folders with confirmation
3. Create Python 3.12 virtual environments in new project folders
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

# Define the projects root directory
PROJECTS_DIR = os.path.expanduser("~/Documents/Projects")


def validate_project_name(name):
    """
    Validate that a project name is available.
    
    Args:
        name (str): Name of the project to validate
        
    Returns:
        bool: True if the project name is available, False otherwise
    """
    project_path = os.path.join(PROJECTS_DIR, name)
    return not os.path.exists(project_path)


def create_project(name, env=False):
    """
    Create a new project folder with the given name.
    
    Args:
        name (str): Name of the project to create
        env (bool): Whether to create a Python 3.12 virtual environment
        
    Returns:
        bool: True if the project was created successfully, False otherwise
    """
    if not validate_project_name(name):
        print(f"Error: Project '{name}' already exists.")
        print(f"You can either:")
        print(f"  1. cd into it: cd ~/Documents/Projects/{name}")
        print(f"  2. Choose another project name")
        return False
    
    try:
        project_path = os.path.join(PROJECTS_DIR, name)
        os.makedirs(project_path, exist_ok=True)
        print(f"Created project folder: {project_path}")
        
        if env:
            create_venv(project_path)
        
        return True
    except Exception as e:
        print(f"Error creating project folder: {str(e)}")
        return False


def create_venv(project_path):
    """
    Create a Python 3.12 virtual environment in the project folder.
    
    Args:
        project_path (str): Path to the project folder
        
    Returns:
        bool: True if the virtual environment was created successfully, False otherwise
    """
    try:
        print("Creating Python 3.12 virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", 
                        "--python=python3.12", 
                        os.path.join(project_path, "venv")], 
                        check=True)
        
        # Create a script to activate the virtual environment
        with open(os.path.join(project_path, "activate.sh"), "w") as f:
            f.write(f"#!/bin/bash\nsource {os.path.join(project_path, 'venv/bin/activate')}\n")
        os.chmod(os.path.join(project_path, "activate.sh"), 0o755)
        
        print(f"Virtual environment created at {os.path.join(project_path, 'venv')}")
        print(f"You can activate it with: source {os.path.join(project_path, 'activate.sh')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {str(e)}")
        return False


def delete_project(name):
    """
    Delete a project folder after confirmation.
    
    Args:
        name (str): Name of the project to delete
        
    Returns:
        bool: True if the project was deleted successfully, False otherwise
    """
    project_path = os.path.join(PROJECTS_DIR, name)
    
    if not os.path.exists(project_path):
        print(f"Error: Project '{name}' does not exist.")
        return False
    
    # Ask for confirmation
    confirm = input(f"Are you sure you want to delete the project '{name}'? This cannot be undone. (y/N): ")
    
    if confirm.lower() not in ["y", "yes"]:
        print("Delete operation cancelled.")
        return False
    
    try:
        shutil.rmtree(project_path)
        print(f"Project '{name}' has been deleted.")
        return True
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
        return False


def main():
    """
    Main function to handle command line arguments and execute the appropriate action.
    """
    parser = argparse.ArgumentParser(description="Scaffold CLI - Manage project folders in ~/Documents/Projects")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create project command
    create_parser = subparsers.add_parser('create', help='Create a new project folder')
    create_parser.add_argument('name', help='Name of the project to create')
    create_parser.add_argument('--env', action='store_true', help='Create a Python 3.12 virtual environment')
    
    # Delete project command
    delete_parser = subparsers.add_parser('delete', help='Delete a project folder')
    delete_parser.add_argument('name', help='Name of the project to delete')
    
    # List projects command
    list_parser = subparsers.add_parser('list', help='List all projects')
    
    args = parser.parse_args()
    
    # Ensure the projects directory exists
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    
    if args.command == 'create':
        create_project(args.name, args.env)
    elif args.command == 'delete':
        delete_project(args.name)
    elif args.command == 'list':
        projects = [d for d in os.listdir(PROJECTS_DIR) 
                   if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith('.')]
        if projects:
            print("Available projects:")
            for project in sorted(projects):
                print(f"  - {project}")
        else:
            print("No projects found.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
