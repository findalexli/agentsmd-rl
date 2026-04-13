Fix the calculator module so that division by zero raises a proper ZeroDivisionError instead of returning None.

The calculator module has a bug where divide(a, b) returns None when b is 0, instead of raising ZeroDivisionError as expected Python behavior.

Modify the calculator.py file to:
1. Raise ZeroDivisionError with message "division by zero" when the divisor is 0
2. Keep all other operations (add, subtract, multiply) working correctly

Files to modify:
- calculator.py
