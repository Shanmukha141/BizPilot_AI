# Calculator, DateTime, File readers
from datetime import datetime

def get_current_datetime() -> str:
    """Returns the current date and time string. Use this when the user asks for the time or date."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def basic_calculator(expression: str) -> str:
    """Evaluates simple mathematical expressions securely. Example input: '2 + 2' or '1500 * 0.18'"""
    try:
        # A basic security measure to prevent code injection via the eval() function
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression."
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"