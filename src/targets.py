

import sys
import simpleeval

def main():
    """Read from stdin and evaluate expressions"""
    try:
        input_expr = sys.stdin.read().strip()
        
        if not input_expr:
            print("Empty input")
            return
        
        # Simpleeval
        evaluator = simpleeval.SimpleEval(
            names={
                'x': -10,
                'y': 22,
                'z': 13,
                'pi': 3.14159,
                'e': 2.71828,
                'value': 67
            },
            functions={
                'abs': abs,
                'max': max,
                'min': min,
                'round': round,
                'triple': lambda x: x*3,
                'advanced': lambda x:(x^3.14159)/x**2
            }
        )
        
        # Evaluate expression
        result = evaluator.eval(input_expr)
        print(f"SUCCESS: {result}")
        
    # Exception handing for errors
    except simpleeval.InvalidExpression as e:
        print(f"INVALID_EXPRESSION: {e}", file=sys.stderr)
        sys.exit(1)
    except simpleeval.FunctionNotDefined as e:
        print(f"FUNCTION_NOT_DEFINED: {e}", file=sys.stderr)
        sys.exit(1)
    except simpleeval.NameNotDefined as e:
        print(f"NAME_NOT_DEFINED: {e}", file=sys.stderr)
        sys.exit(1)
    except ZeroDivisionError as e:
        print(f"ZERO_DIVISION_ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, TypeError, ArithmeticError) as e:
        print(f"VALUE/TYPE/ARITHMETIC_ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED_ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()