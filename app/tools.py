"""
Tool registry and tool implementations.
Tools are Python functions that can be called by workflow nodes.
"""

from typing import Dict, Any, Callable, List
import re
import ast


class ToolRegistry:
    """Registry for managing workflow tools"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        """Register a tool function"""
        self._tools[name] = func
    
    def get(self, name: str) -> Callable:
        """Get a tool by name"""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self._tools.keys())


# Global tool registry instance
tool_registry = ToolRegistry()


# ============================================================================
# Code Review Tools
# ============================================================================

def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract function definitions from Python code.
    
    Args:
        state: Must contain 'code' key with Python source code
        
    Returns:
        Updated state with 'functions' list
    """
    code = state.get("code", "")
    functions = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "num_lines": (node.end_lineno or node.lineno) - node.lineno + 1
                }
                functions.append(func_info)
    except SyntaxError as e:
        functions.append({
            "error": f"Syntax error in code: {str(e)}",
            "name": "unknown"
        })
    
    state["functions"] = functions
    return state


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate cyclomatic complexity for each function.
    
    Args:
        state: Must contain 'code' and 'functions' keys
        
    Returns:
        Updated state with 'complexity_scores' dict
    """
    code = state.get("code", "")
    functions = state.get("functions", [])
    complexity_scores = {}
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Simple complexity calculation
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    # Count decision points
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                
                complexity_scores[node.name] = complexity
    except:
        pass
    
    state["complexity_scores"] = complexity_scores
    return state


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect code smells and potential issues.
    
    Args:
        state: Must contain 'code', 'functions', and 'complexity_scores'
        
    Returns:
        Updated state with 'issues' list
    """
    code = state.get("code", "")
    functions = state.get("functions", [])
    complexity_scores = state.get("complexity_scores", {})
    issues = []
    
    # Check for high complexity
    for func_name, complexity in complexity_scores.items():
        if complexity > 10:
            issues.append({
                "type": "high_complexity",
                "function": func_name,
                "severity": "high",
                "message": f"Function '{func_name}' has high complexity ({complexity})"
            })
        elif complexity > 5:
            issues.append({
                "type": "moderate_complexity",
                "function": func_name,
                "severity": "medium",
                "message": f"Function '{func_name}' has moderate complexity ({complexity})"
            })
    
    # Check for long functions
    for func in functions:
        if "num_lines" in func and func["num_lines"] > 50:
            issues.append({
                "type": "long_function",
                "function": func["name"],
                "severity": "medium",
                "message": f"Function '{func['name']}' is too long ({func['num_lines']} lines)"
            })
    
    # Check for common code smells
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        # Check for bare except
        if re.search(r'except\s*:', line):
            issues.append({
                "type": "bare_except",
                "line": i,
                "severity": "medium",
                "message": f"Line {i}: Bare except clause catches all exceptions"
            })
        
        # Check for print statements (should use logging)
        if re.search(r'\bprint\s*\(', line):
            issues.append({
                "type": "print_statement",
                "line": i,
                "severity": "low",
                "message": f"Line {i}: Consider using logging instead of print"
            })
    
    state["issues"] = issues
    return state


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate improvement suggestions based on detected issues.
    
    Args:
        state: Must contain 'issues' list
        
    Returns:
        Updated state with 'suggestions' list
    """
    issues = state.get("issues", [])
    suggestions = []
    
    # Group issues by type
    issue_types = {}
    for issue in issues:
        issue_type = issue.get("type", "unknown")
        if issue_type not in issue_types:
            issue_types[issue_type] = []
        issue_types[issue_type].append(issue)
    
    # Generate suggestions
    if "high_complexity" in issue_types or "moderate_complexity" in issue_types:
        suggestions.append(
            "Consider breaking down complex functions into smaller, "
            "more focused functions to improve readability and maintainability."
        )
    
    if "long_function" in issue_types:
        suggestions.append(
            "Long functions should be refactored into smaller functions. "
            "Each function should have a single, well-defined responsibility."
        )
    
    if "bare_except" in issue_types:
        suggestions.append(
            "Replace bare except clauses with specific exception types. "
            "This prevents catching system exits and keyboard interrupts."
        )
    
    if "print_statement" in issue_types:
        suggestions.append(
            "Use Python's logging module instead of print statements "
            "for better control over output and debugging."
        )
    
    if not suggestions:
        suggestions.append("Code looks good! No major issues detected.")
    
    state["suggestions"] = suggestions
    return state


def evaluate_quality(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate overall code quality and assign a score.
    
    Args:
        state: Must contain 'issues' and 'functions'
        
    Returns:
        Updated state with 'quality_score' (0-10) and incremented 'iteration'
    """
    issues = state.get("issues", [])
    functions = state.get("functions", [])
    
    # Start with perfect score
    score = 10
    
    # Deduct points based on issues
    for issue in issues:
        severity = issue.get("severity", "low")
        if severity == "high":
            score -= 2
        elif severity == "medium":
            score -= 1
        elif severity == "low":
            score -= 0.5
    
    # Ensure score is in valid range
    score = max(0, min(10, score))
    
    state["quality_score"] = int(score)
    state["iteration"] = state.get("iteration", 0) + 1
    
    return state


# ============================================================================
# Register all tools
# ============================================================================

tool_registry.register("extract_functions", extract_functions)
tool_registry.register("check_complexity", check_complexity)
tool_registry.register("detect_issues", detect_issues)
tool_registry.register("suggest_improvements", suggest_improvements)
tool_registry.register("evaluate_quality", evaluate_quality)
