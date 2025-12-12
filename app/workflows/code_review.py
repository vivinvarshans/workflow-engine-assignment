"""
Code Review Mini-Agent Workflow

This workflow demonstrates the engine's capabilities by implementing
a code review agent that:
1. Extracts functions from code
2. Checks complexity
3. Detects issues
4. Suggests improvements
5. Evaluates quality
6. Loops until quality threshold is met
"""

from typing import Dict, Any


def get_code_review_graph_definition() -> Dict[str, Any]:
    """
    Returns the graph definition for the code review workflow.
    
    This can be used to create a graph via the API.
    """
    return {
        "name": "code_review_workflow",
        "nodes": {
            "extract": {
                "tool": "extract_functions",
                "next": "check_complexity"
            },
            "check_complexity": {
                "tool": "check_complexity",
                "next": "detect_issues"
            },
            "detect_issues": {
                "tool": "detect_issues",
                "next": "suggest_improvements"
            },
            "suggest_improvements": {
                "tool": "suggest_improvements",
                "next": "evaluate_quality"
            },
            "evaluate_quality": {
                "tool": "evaluate_quality",
                "next": {
                    "condition": "quality_score >= 7 or iteration >= 5",
                    "if_true": "end",
                    "if_false": "check_complexity"
                }
            }
        },
        "start_node": "extract",
        "max_iterations": 20
    }


# Example code samples for testing
SAMPLE_CODE_GOOD = """
def calculate_sum(numbers):
    \"\"\"Calculate the sum of a list of numbers.\"\"\"
    return sum(numbers)

def calculate_average(numbers):
    \"\"\"Calculate the average of a list of numbers.\"\"\"
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""

SAMPLE_CODE_BAD = """
def process_data(data):
    result = 0
    for item in data:
        if item > 0:
            if item < 100:
                if item % 2 == 0:
                    result = result + item
                else:
                    result = result + item * 2
            else:
                if item % 3 == 0:
                    result = result + item / 3
                else:
                    result = result - item
        else:
            print("Negative value found")
            try:
                result = result + abs(item)
            except:
                pass
    return result

def very_long_function_that_does_too_many_things(a, b, c, d, e, f, g):
    x = a + b
    y = c + d
    z = e + f
    result = x * y * z
    if result > 100:
        result = result / 2
    if result < 10:
        result = result * 3
    print(result)
    return result
"""

SAMPLE_CODE_MODERATE = """
def validate_user_input(user_input):
    if not user_input:
        return False
    
    if len(user_input) < 3:
        return False
    
    if len(user_input) > 50:
        return False
    
    if not user_input.isalnum():
        return False
    
    return True

def process_items(items):
    processed = []
    for item in items:
        if item:
            processed.append(item.strip().lower())
    return processed
"""


def get_sample_initial_state(code_sample: str = SAMPLE_CODE_MODERATE) -> Dict[str, Any]:
    """
    Returns a sample initial state for the code review workflow.
    
    Args:
        code_sample: Python code to review (defaults to moderate quality code)
    
    Returns:
        Initial state dictionary
    """
    return {
        "code": code_sample,
        "quality_score": 0,
        "iteration": 0,
        "functions": [],
        "complexity_scores": {},
        "issues": [],
        "suggestions": []
    }
