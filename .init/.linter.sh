#!/bin/bash
cd /home/kavia/workspace/code-generation/employee-performance-and-management-system-163463-162810/employee_system_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

