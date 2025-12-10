"""
Example workflow definitions for the workflow engine
"""

# Code Review Workflow
CODE_REVIEW_WORKFLOW = {
    "name": "Code Review Agent",
    "description": "Analyzes code quality through multiple steps with iterative improvement",
    "nodes": [
        {
            "name": "extract",
            "type": "function",
            "function_name": "extract_functions",
            "description": "Extract functions from code"
        },
        {
            "name": "complexity",
            "type": "function",
            "function_name": "check_complexity",
            "description": "Check complexity of extracted functions"
        },
        {
            "name": "detect",
            "type": "function",
            "function_name": "detect_issues",
            "description": "Detect code issues"
        },
        {
            "name": "suggest",
            "type": "function",
            "function_name": "suggest_improvements",
            "description": "Suggest improvements"
        },
        {
            "name": "increment",
            "type": "function",
            "function_name": "increment_iteration",
            "description": "Increment iteration counter"
        },
        {
            "name": "end",
            "type": "function",
            "function_name": "pass_through",
            "description": "End node"
        }
    ],
    "edges": [
        {
            "from_node": "extract",
            "to_node": "complexity",
            "type": "direct"
        },
        {
            "from_node": "complexity",
            "to_node": "detect",
            "type": "direct"
        },
        {
            "from_node": "detect",
            "to_node": "suggest",
            "type": "direct"
        },
        {
            "from_node": "suggest",
            "to_node": "increment",
            "type": "direct"
        },
        {
            "from_node": "increment",
            "to_node": "end",
            "type": "conditional",
            "condition": "quality_score >= 70 or iteration >= 3"
        },
        {
            "from_node": "increment",
            "to_node": "complexity",
            "type": "conditional",
            "condition": "quality_score < 70 and iteration < 3"
        }
    ],
    "start_node": "extract",
    "end_nodes": ["end"]
}


# Simple Linear Workflow (for testing)
SIMPLE_WORKFLOW = {
    "name": "Simple Linear Workflow",
    "description": "A simple workflow that extracts functions and checks complexity",
    "nodes": [
        {
            "name": "extract",
            "type": "function",
            "function_name": "extract_functions",
            "description": "Extract functions from code"
        },
        {
            "name": "complexity",
            "type": "function",
            "function_name": "check_complexity",
            "description": "Check complexity"
        },
        {
            "name": "end",
            "type": "function",
            "function_name": "pass_through",
            "description": "End node"
        }
    ],
    "edges": [
        {
            "from_node": "extract",
            "to_node": "complexity",
            "type": "direct"
        },
        {
            "from_node": "complexity",
            "to_node": "end",
            "type": "direct"
        }
    ],
    "start_node": "extract",
    "end_nodes": ["end"]
}


# Branching Workflow Example
BRANCHING_WORKFLOW = {
    "name": "Conditional Branching Workflow",
    "description": "Demonstrates conditional branching based on complexity",
    "nodes": [
        {
            "name": "extract",
            "type": "function",
            "function_name": "extract_functions",
            "description": "Extract functions"
        },
        {
            "name": "complexity",
            "type": "function",
            "function_name": "check_complexity",
            "description": "Check complexity"
        },
        {
            "name": "detect",
            "type": "function",
            "function_name": "detect_issues",
            "description": "Detect issues for complex code"
        },
        {
            "name": "end",
            "type": "function",
            "function_name": "pass_through",
            "description": "End node"
        }
    ],
    "edges": [
        {
            "from_node": "extract",
            "to_node": "complexity",
            "type": "direct"
        },
        {
            "from_node": "complexity",
            "to_node": "detect",
            "type": "conditional",
            "condition": "average_complexity > 5"
        },
        {
            "from_node": "complexity",
            "to_node": "end",
            "type": "conditional",
            "condition": "average_complexity <= 5"
        },
        {
            "from_node": "detect",
            "to_node": "end",
            "type": "direct"
        }
    ],
    "start_node": "extract",
    "end_nodes": ["end"]
}


# Sample code for testing
SAMPLE_CODE_SIMPLE = """
def calculate_sum(a, b):
    return a + b

def calculate_product(a, b):
    return a * b
"""

SAMPLE_CODE_COMPLEX = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item + 1)
        elif item < 0:
            result.append(abs(item))
    return result

def ComplexFunction(x, y, z):
    if x > 0 and y > 0:
        if z > 0:
            return x + y + z
        else:
            return x + y - z
    elif x < 0 or y < 0:
        return 0
    return -1
"""

SAMPLE_CODE_WITH_ISSUES = """
def risky_function(code):
    try:
        result = eval(code)
    except:
        result = None
    return result

def VeryLongLineFunctionThatDoesNotFollowPep8NamingConventions(parameter1, parameter2, parameter3):
    return parameter1 + parameter2 + parameter3
"""
