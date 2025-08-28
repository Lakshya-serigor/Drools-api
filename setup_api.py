#!/usr/bin/env python3

import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command"""
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

def clone_repository():
    """Clone the Drools API repository"""
    repo_url = "https://github.com/Lakshya-serigor/Drools-api.git"
    project_dir = "Drools-api"

    if Path(project_dir).exists():
        print(f"Directory '{project_dir}' exists, skipping clone.")
    else:
        print("Cloning repository...")
        run_command(["git", "clone", repo_url])

    return Path(project_dir).resolve()

def create_virtual_environment(project_dir):
    """Create virtual environment"""
    venv_dir = project_dir / "venv"

    if venv_dir.exists():
        print("Virtual environment exists.")
        return venv_dir

    print("Creating virtual environment...")
    venv.create(venv_dir, with_pip=True)
    return venv_dir

def get_venv_python(venv_dir):
    """Get venv Python path"""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"

def install_requirements(project_dir, venv_python):
    """Install requirements"""
    requirement_file = project_dir / "requirements.txt"

    if not requirement_file.exists():
        print("Creating requirements.txt...")
        basic_requirements = """fastapi>=0.104.0
uvicorn[standard]
openai
faiss-cpu
python-dotenv
numpy
pydantic
python-multipart"""
        requirement_file.write_text(basic_requirements)

    print("Installing requirements...")
    run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    run_command([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], cwd=project_dir)

def create_env_file(project_dir):
    """Create .env file"""
    env_file = project_dir / ".env"

    if env_file.exists():
        print(".env file exists.")
        return

    api_key = input("Enter OpenAI API key (or press Enter to skip): ").strip()

    if api_key:
        env_content = f"OPENAI_API_KEY={api_key}\n"
    else:
        env_content = "OPENAI_API_KEY=your_api_key_here\n"

    env_file.write_text(env_content)
    print("Created .env file")

def create_run_script(project_dir):
    """Create run script"""
    if os.name == "nt":
        # Windows batch file
        script_content = """@echo off
call venv\Scripts\activate.bat
echo Starting Drools API...
uvicorn api_drools:app --host 0.0.0.0 --port 8503 --reload
"""
        script_path = project_dir / "run_api.bat"
    else:
        # Linux/Mac shell script
        script_content = """#!/bin/bash
source venv/bin/activate
echo "Starting Drools API..."
uvicorn api_main:app --host 0.0.0.0 --port 8503 --reload
"""
        script_path = project_dir / "run_api.sh"

    script_path.write_text(script_content)
    if not os.name == "nt":
        script_path.chmod(0o755)  # Make executable

    print(f"Created {script_path.name}")

def main():
    """Main setup function"""
    print("Drools RAG API Setup")

    # Check git
    run_command(["git", "--version"])

    # Setup
    project_dir = clone_repository()
    venv_dir = create_virtual_environment(project_dir)
    venv_python = get_venv_python(venv_dir)
    install_requirements(project_dir, venv_python)
    create_env_file(project_dir)
    create_run_script(project_dir)

    print("\nSetup complete!")
    print(f"Project: {project_dir}")
    print("Add your OpenAI API key to .env file if needed.")
    print("\nTo start the API:")
    if os.name == "nt":
        print("  run_api.bat")
    else:
        print("  ./run_api.sh")
    print("\nAPI will be available at: http://localhost:8503/docs")

if __name__ == "__main__":
    main()
