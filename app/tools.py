from typing import Dict, Callable, Optional, Any
from app.engine import WorkflowState


class ToolRegistry:
    """Registry for managing workflow tools (functions)"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register(self, name: str, function: Callable) -> None:
        """Register a tool function"""
        self.tools[name] = function
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a registered tool"""
        return self.tools.get(name)
    
    def list_tools(self) -> list:
        """List all registered tools"""
        return list(self.tools.keys())
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            return True
        return False


# Global tool registry instance
tool_registry = ToolRegistry()


# ============================================
# Example Tools for Code Review Workflow
# ============================================

def extract_functions(state: WorkflowState) -> Dict[str, Any]:
    """Extract functions from code"""
    code = state.get("code", "")
    
    # Simple function extraction (looking for 'def ' keyword)
    functions = []
    lines = code.split('\n')
    current_function = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            if current_function:
                functions.append(current_function)
            
            # Extract function name
            func_name = line.strip().split('(')[0].replace('def ', '').strip()
            current_function = {
                'name': func_name,
                'start_line': i + 1,
                'code': line + '\n'
            }
        elif current_function:
            current_function['code'] += line + '\n'
    
    if current_function:
        functions.append(current_function)
    
    return {
        'functions': functions,
        'function_count': len(functions)
    }


def check_complexity(state: WorkflowState) -> Dict[str, Any]:
    """Check code complexity of extracted functions"""
    functions = state.get('functions', [])
    
    complexity_scores = []
    for func in functions:
        code = func.get('code', '')
        
        # Simple complexity metric: count control flow statements
        complexity = 1  # Base complexity
        complexity += code.count('if ')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('elif ')
        complexity += code.count('and ')
        complexity += code.count('or ')
        
        complexity_scores.append({
            'function': func['name'],
            'complexity': complexity,
            'is_complex': complexity > 5
        })
    
    avg_complexity = sum(s['complexity'] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0
    
    return {
        'complexity_scores': complexity_scores,
        'average_complexity': avg_complexity,
        'high_complexity_count': sum(1 for s in complexity_scores if s['is_complex'])
    }


def detect_issues(state: WorkflowState) -> Dict[str, Any]:
    """Detect basic code issues"""
    code = state.get('code', '')
    functions = state.get('functions', [])
    
    issues = []
    
    # Check for common issues
    if 'except:' in code:
        issues.append({
            'type': 'bare_except',
            'severity': 'medium',
            'message': 'Bare except clause found - should specify exception type'
        })
    
    if 'eval(' in code:
        issues.append({
            'type': 'security',
            'severity': 'high',
            'message': 'Use of eval() is dangerous'
        })
    
    # Check function naming
    for func in functions:
        name = func['name']
        if not name.islower():
            issues.append({
                'type': 'naming',
                'severity': 'low',
                'message': f"Function '{name}' should use snake_case"
            })
    
    # Check line length
    long_lines = sum(1 for line in code.split('\n') if len(line) > 100)
    if long_lines > 0:
        issues.append({
            'type': 'style',
            'severity': 'low',
            'message': f'{long_lines} lines exceed 100 characters'
        })
    
    return {
        'issues': issues,
        'issue_count': len(issues),
        'high_severity_count': sum(1 for i in issues if i['severity'] == 'high')
    }


def suggest_improvements(state: WorkflowState) -> Dict[str, Any]:
    """Suggest improvements based on detected issues"""
    issues = state.get('issues', [])
    complexity_scores = state.get('complexity_scores', [])
    
    suggestions = []
    
    # Suggestions based on issues
    for issue in issues:
        if issue['type'] == 'bare_except':
            suggestions.append('Specify exception types in except clauses')
        elif issue['type'] == 'security':
            suggestions.append('Remove eval() and use safer alternatives like ast.literal_eval()')
        elif issue['type'] == 'naming':
            suggestions.append('Rename functions to follow PEP 8 naming conventions')
        elif issue['type'] == 'style':
            suggestions.append('Break long lines into multiple lines')
    
    # Suggestions based on complexity
    for score in complexity_scores:
        if score['is_complex']:
            suggestions.append(f"Refactor function '{score['function']}' to reduce complexity")
    
    # Calculate quality score
    issue_count = state.get('issue_count', 0)
    high_complexity_count = state.get('high_complexity_count', 0)
    quality_score = max(0, 100 - (issue_count * 10) - (high_complexity_count * 15))
    
    return {
        'suggestions': list(set(suggestions)),  # Remove duplicates
        'quality_score': quality_score
    }


def increment_iteration(state: WorkflowState) -> Dict[str, Any]:
    """Increment iteration counter for loops"""
    current_iteration = state.get('iteration', 0)
    return {
        'iteration': current_iteration + 1
    }


# Register all tools
tool_registry.register('extract_functions', extract_functions)
tool_registry.register('check_complexity', check_complexity)
tool_registry.register('detect_issues', detect_issues)
tool_registry.register('suggest_improvements', suggest_improvements)
tool_registry.register('increment_iteration', increment_iteration)


# ============================================
# Generic utility tools
# ============================================

def pass_through(state: WorkflowState) -> Dict[str, Any]:
    """A no-op tool that just passes state through"""
    return {}


def log_state(state: WorkflowState) -> Dict[str, Any]:
    """Log current state (for debugging)"""
    print(f"Current state: {state.snapshot()}")
    return {}


tool_registry.register('pass_through', pass_through)
tool_registry.register('log_state', log_state)
