#!/usr/bin/env python
import sys
import warnings

from crew import AppsecAgents

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

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
        AppsecAgents().crew().kickoff(inputs=inputs)
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
