#!/usr/bin/env python
import json
import sys
import time
import warnings

from appsec_agents.crew import AppsecAgents


import logging
from logging.handlers import RotatingFileHandler
import os

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Ensure the "logs" folder exists
os.makedirs("logs", exist_ok=True)

# Create a rotating file handler
rotating_file_handler = RotatingFileHandler(
    "logs/debug.log",
    maxBytes=50 * 1024,  # 50 KB
    backupCount=5  # Keep up to 5 backups
)
rotating_file_handler.setLevel(logging.DEBUG)
rotating_file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))

# Configure logging with both handlers using basicConfig
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format for the root logger
    handlers=[rotating_file_handler, console_handler]  # Attach both handlers
)

logger = logging.getLogger(__name__)


# This main file allows you to run, test, and train your crew locally.
# Replace the `inputs` dictionary with the appropriate data for your use case.

def run():
    """
    Run the crew to analyze a GitHub repository for security vulnerabilities.
    """
    inputs = {
        'repository_url': 'https://github.com/lochgeo/food-pooling',
        'scan_depth': 3,
        'analysis_mode': 'quick'
    }
    try:
        logger.info("Starting the crew...")
        appsec = AppsecAgents()
        crew = appsec.crew()
        crew.kickoff(inputs=inputs)
        
        # Wait for the crew to complete its execution
        
        while not crew.is_complete():
            time.sleep(1)  # Sleep for a short duration to avoid busy-waiting
            
        logger.info("Crew execution completed.")
        
        # Retrieve and print the results
        results = crew.get_results()
        logger.info("Crew results:")
        logger.info(json.dumps(results, indent=2))

    except Exception as e:
        print(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'repository_url': 'https://github.com/lochgeo/food-pooling',
        'scan_depth': 3,
        'analysis_mode': 'quick'
    }
    try:
        AppsecAgents().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        print(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AppsecAgents().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        print(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and return results for a specific number of iterations.
    """
    inputs = {
        'repository_url': 'https://github.com/example/example-repo',
    }
    try:
        AppsecAgents().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        print(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py [run|train|replay|test] [optional arguments...]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        print("Usage: main.py [run|train|replay|test] [optional arguments...]")
        sys.exit(1)
