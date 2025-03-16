#!/usr/bin/env python3
"""
Scaffold CLI - A tool to manage project folders in ~/Documents/Projects

This tool allows users to:
1. Create project folders with validation
2. Delete project folders with confirmation
3. Create Python 3.12 virtual environments in new project folders
4. Navigate to existing project folders or offer to create them
5. Automatically detect and activate virtual environments
"""

import os
import sys
import shutil
import argparse
import subprocess
import logging
import traceback
from pathlib import Path
from datetime import datetime
import errno
import stat

# Define the projects root directory
PROJECTS_DIR = os.path.expanduser("~/Documents/Projects")

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f'scaffold_{datetime.now().strftime("%Y%m%d")}.log')

# Configure logger
logger = logging.getLogger('scaffold')
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Less verbose for console
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# Global debug flag
DEBUG = False


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


def find_venv(project_path):
    """
    Find a virtual environment in a project folder or its subdirectories.
    
    Args:
        project_path (str): Path to the project folder
        
    Returns:
        str or None: Path to the virtual environment's activate script, or None if not found
    """
    # Check if venv exists in the project root
    venv_path = os.path.join(project_path, "venv")
    activate_script = os.path.join(venv_path, "bin", "activate")
    
    if os.path.exists(activate_script):
        return activate_script
    
    # Check for venv in subdirectories (1 level deep only for performance)
    for item in os.listdir(project_path):
        subdir_path = os.path.join(project_path, item)
        if os.path.isdir(subdir_path):
            subdir_venv = os.path.join(subdir_path, "venv")
            subdir_activate = os.path.join(subdir_venv, "bin", "activate")
            if os.path.exists(subdir_activate):
                return subdir_activate
    
    return None


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
        logger.error(f"Project '{name}' already exists.")
        print(f"Error: Project '{name}' already exists.")
        print(f"You can either:")
        print(f"  1. cd into it: cd ~/Documents/Projects/{name}")
        print(f"  2. Choose another project name")
        return False
    
    try:
        project_path = os.path.join(PROJECTS_DIR, name)
        os.makedirs(project_path, exist_ok=True)
        logger.info(f"Created project folder: {project_path}")
        print(f"Created project folder: {project_path}")
        
        if env:
            create_venv(project_path)
        
        return True
    except Exception as e:
        logger.error(f"Error creating project folder: {str(e)}")
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
        logger.info("Creating Python 3.12 virtual environment...")
        print("Creating Python 3.12 virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", 
                        "--python=python3.12", 
                        os.path.join(project_path, "venv")], 
                        check=True)
        
        # Create a script to activate the virtual environment
        with open(os.path.join(project_path, "activate.sh"), "w") as f:
            f.write(f"#!/bin/bash\nsource {os.path.join(project_path, 'venv/bin/activate')}\n")
        os.chmod(os.path.join(project_path, "activate.sh"), 0o755)
        
        logger.info(f"Virtual environment created at {os.path.join(project_path, 'venv')}")
        print(f"Virtual environment created at {os.path.join(project_path, 'venv')}")
        print(f"You can activate it with: source {os.path.join(project_path, 'activate.sh')}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating virtual environment: {str(e)}")
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
    logger.debug(f"Attempting to delete project: {name}")
    project_path = os.path.join(PROJECTS_DIR, name)
    
    # Log detailed info about the project directory
    logger.debug(f"Project path to delete: {project_path}")
    if os.path.exists(project_path):
        logger.debug(f"Project exists, checking contents...")
        try:
            contents = os.listdir(project_path)
            logger.debug(f"Directory contents: {contents}")
        except Exception as e:
            logger.error(f"Error listing directory contents: {str(e)}")
    else:
        logger.error(f"Project '{name}' does not exist at path: {project_path}")
        print(f"Error: Project '{name}' does not exist.")
        return False
    
    # Ask for confirmation
    logger.debug("Asking for user confirmation...")
    confirm = input(f"Are you sure you want to delete the project '{name}'? This cannot be undone. (y/N): ")
    
    if confirm.lower() not in ["y", "yes"]:
        logger.info("Delete operation cancelled.")
        print("Delete operation cancelled.")
        return False
    
    try:
        logger.debug(f"Attempting to remove directory tree: {project_path}")
        # Use additional error handling for the rmtree operation
        def handle_remove_readonly(func, path, exc):
            excvalue = exc[1]
            logger.warning(f"Error removing {path}: {excvalue}")
            if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
                os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO)
                func(path)
            else:
                raise
        
        shutil.rmtree(project_path, onerror=handle_remove_readonly)
        logger.info(f"Project '{name}' has been deleted.")
        print(f"Project '{name}' has been deleted.")
        return True
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"Error deleting project: {str(e)}")
        return False


def navigate_project(name):
    """
    Navigate to a project folder or offer to create it if it doesn't exist.
    
    Args:
        name (str): Name of the project to navigate to
        
    Returns:
        int: 0 if the project exists, 1 if the project should be created, 2 if cancelled
    """
    # Special case for 'home' - navigate to the projects directory root
    if name.lower() == 'home':
        logger.info(f"Navigating to projects root directory: {PROJECTS_DIR}")
        logger.info(f"NAVIGATE_TO:{PROJECTS_DIR}")
        print(f"NAVIGATE_TO:{PROJECTS_DIR}")
        return 0
    
    project_path = os.path.join(PROJECTS_DIR, name)
    
    # If the project exists, check for virtual environment and return path for navigation
    if os.path.exists(project_path):
        venv_path = find_venv(project_path)
        if venv_path:
            logger.info(f"NAVIGATE_TO:{project_path}")
            logger.info(f"ACTIVATE_VENV:{venv_path}")
            print(f"NAVIGATE_TO:{project_path}")
            print(f"ACTIVATE_VENV:{venv_path}")
        else:
            logger.info(f"NAVIGATE_TO:{project_path}")
            print(f"NAVIGATE_TO:{project_path}")
        return 0
    
    # If the project doesn't exist, ask if we should create it
    create = input(f"Project '{name}' does not exist. Would you like to create it? (y/N): ")
    
    if create.lower() not in ["y", "yes"]:
        logger.info("Operation cancelled.")
        print("Operation cancelled.")
        return 2
    
    # Ask if a virtual environment should be created
    env = input("Would you like to create a Python 3.12 virtual environment in the project? (y/N): ")
    env_flag = env.lower() in ["y", "yes"]
    
    # Create the project
    if create_project(name, env_flag):
        project_path = os.path.join(PROJECTS_DIR, name)
        if env_flag:
            venv_path = os.path.join(project_path, "venv", "bin", "activate")
            logger.info(f"NAVIGATE_TO:{project_path}")
            logger.info(f"ACTIVATE_VENV:{venv_path}")
            print(f"NAVIGATE_TO:{project_path}")
            print(f"ACTIVATE_VENV:{venv_path}")
        else:
            logger.info(f"NAVIGATE_TO:{project_path}")
            print(f"NAVIGATE_TO:{project_path}")
        return 1
    
    return 2


def main():
    """
    Main function to handle command line arguments and execute the appropriate action.
    """
    global DEBUG
    
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Scaffold CLI - Manage project folders in ~/Documents/Projects")
    
    # Add global arguments to the main parser
    parser.add_argument('-v', '--verbose', action='store_true', 
                      help='Enable verbose output for debugging')
    
    # Create subparsers with the parent parser to inherit global arguments
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create project command
    create_parser = subparsers.add_parser('create', 
        help='Create a new project folder and automatically navigate to it',
        description='Create a new project folder with the given name and automatically navigate to it. Optionally create a Python 3.12 virtual environment.',
        prog='go create')
    create_parser.add_argument('name', help='Name of the project to create')
    create_parser.add_argument('--env', action='store_true', help='Create a Python 3.12 virtual environment')
    
    # Delete project command
    delete_parser = subparsers.add_parser('delete', help='Delete a project folder')
    delete_parser.add_argument('name', help='Name of the project to delete')
    
    # List projects command
    list_parser = subparsers.add_parser('list', help='List all projects')
    
    # Navigate to project command (or create if it doesn't exist)
    navigate_parser = subparsers.add_parser('navigate', 
        help='Navigate to a project or create it if it doesn\'t exist',
        description='Navigate to a project folder or create it if it doesn\'t exist. Use "home" as the project name to navigate to the projects root directory.',
        prog='go navigate')
    navigate_parser.add_argument('name', 
        help='Name of the project to navigate to. Use "home" to navigate to the projects root directory.')
    
    args = parser.parse_args()
    
    # If no arguments provided, print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Set global debug flag and configure logging level
    if hasattr(args, 'verbose') and args.verbose:
        DEBUG = True
        console_handler.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
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
            logger.info("Available projects:")
            print("Available projects:")
            for project in sorted(projects):
                project_path = os.path.join(PROJECTS_DIR, project)
                venv_path = find_venv(project_path)
                venv_indicator = " (has venv)" if venv_path else ""
                logger.info(f"  - {project}{venv_indicator}")
                print(f"  - {project}{venv_indicator}")
        else:
            logger.info("No projects found.")
            print("No projects found.")
    elif args.command == 'navigate':
        sys.exit(navigate_project(args.name))
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())
