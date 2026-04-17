

#!/usr/bin/env python3

# Mock OpenHands script for testing purposes

import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Mock OpenHands for testing")
    parser.add_argument("--prompt-file", help="File containing the prompt")
    parser.add_argument("--fail", action="store_true", help="Simulate failure")
    args = parser.parse_args()

    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r') as f:
                prompt = f.read()

            # Check if this is the failing task or if fail flag is set
            if args.fail or (prompt and "test-openhands-fail" in prompt):
                print("Mock OpenHands execution failed", file=sys.stderr)
                sys.exit(1)
            else:
                # Generate a mock successful response
                response = {
                    "success": True,
                    "output": "Mock OpenHands execution completed successfully",
                    "task_summary": "Task completed with mock OpenHands",
                    "changes_made": ["Mock change 1", "Mock change 2"]
                }
                print(json.dumps(response))
                sys.exit(0)

        except Exception as e:
            print(f"Error reading prompt file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No prompt file specified", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

