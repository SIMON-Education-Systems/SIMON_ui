# Installation

Run the following command in the root directory of the project:
> python build.py

Wait for the executable to finish building. It will be located under the `dist/` folder

# Usage

## Windows

Navigate to the `dist/` directory in the file explorer and double click `ultrasound.exe`

## OSX

Navigate to the `dist/` directory in the file explorer and double click `ultrasound`

or 

In the terminal, navigate to the project directory and run

> ./dist/ultrasound

# Development

Create a python virtual environment by running

> python3 -m venv env

Activate it (to deactivate simply type `deactivate` in your terminal)

> ./env/Scripts/Activate.ps1

Install the required packages

> pip install -r requirements.txt

You should now be able to run the script by running

> python ultrasound.py
