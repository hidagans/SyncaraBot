# syncara/shortcode/python_execution.py
from syncara.console import console
import sys
import io
import contextlib
import traceback
import asyncio
import re

class PythonExecutionShortcode:
    def __init__(self):
        self.handlers = {
            'PYTHON:EXEC': self.execute_python,
            'CODE:PYTHON': self.execute_python,
            'CALC:PYTHON': self.execute_python,
        }
        
        self.descriptions = {
            'PYTHON:EXEC': 'Execute Python code safely. Usage: [PYTHON:EXEC:print("Hello World")]',
            'CODE:PYTHON': 'Execute Python code safely. Usage: [CODE:PYTHON:2+2*3]',
            'CALC:PYTHON': 'Calculate using Python. Usage: [CALC:PYTHON:import math; math.sqrt(16)]'
        }
        
        self.pending_results = {}
        
        # Security restrictions
        self.forbidden_imports = [
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'requests',
            'ftplib', 'telnetlib', 'smtplib', 'poplib', 'imaplib', 'nntplib',
            'http', 'webbrowser', 'ctypes', 'multiprocessing', 'threading',
            'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3', 'zipfile',
            'tarfile', 'tempfile', 'glob', 'platform', 'getpass'
        ]
        
        self.forbidden_functions = [
            'open', 'file', 'input', 'raw_input', 'execfile', 'reload',
            'compile', 'eval', 'exec', '__import__', 'globals', 'locals',
            'vars', 'dir', 'help', 'exit', 'quit'
        ]

    async def execute_python(self, client, message, params):
        """Execute Python code safely"""
        try:
            code = params.strip()
            if not code:
                console.error("[PYTHON:EXEC] Empty code provided")
                return False
            
            console.info(f"[PYTHON:EXEC] Executing code: {code[:100]}...")
            
            # Security check
            security_result = self._check_security(code)
            if not security_result['safe']:
                # Store error for delayed sending
                result_id = f"python_security_error_{message.id}"
                self.pending_results[result_id] = {
                    'text': f"🚫 **Security Error**\n\n❌ {security_result['reason']}\n\n**Forbidden items:**\n{', '.join(security_result['violations'])}",
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                console.error(f"[PYTHON:EXEC] Security violation: {security_result['reason']}")
                return result_id
            
            # Execute code safely
            execution_result = await self._execute_code_safely(code)
            
            # Store result for delayed sending
            result_id = f"python_result_{message.id}"
            
            if execution_result['success']:
                output_text = f"🐍 **Python Execution Result**\n\n"
                output_text += f"**Code:**\n```python\n{code}\n```\n\n"
                
                if execution_result['output']:
                    output_text += f"**Output:**\n```\n{execution_result['output']}\n```"
                else:
                    output_text += "**Output:** ✅ Executed successfully (no output)"
                
                if execution_result['return_value'] is not None:
                    output_text += f"\n\n**Return Value:** `{execution_result['return_value']}`"
                
                self.pending_results[result_id] = {
                    'text': output_text,
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                console.info(f"[PYTHON:EXEC] Code executed successfully: {result_id}")
            else:
                error_text = f"🐍 **Python Execution Error**\n\n"
                error_text += f"**Code:**\n```python\n{code}\n```\n\n"
                error_text += f"**Error:**\n```\n{execution_result['error']}\n```"
                
                self.pending_results[result_id] = {
                    'text': error_text,
                    'chat_id': message.chat.id,
                    'reply_to_message_id': message.id
                }
                console.error(f"[PYTHON:EXEC] Code execution failed: {execution_result['error']}")
            
            return result_id
            
        except Exception as e:
            console.error(f"[PYTHON:EXEC] Error: {e}")
            return False
    
    def _check_security(self, code):
        """Check if code is safe to execute"""
        code_lower = code.lower()
        violations = []
        
        # Check forbidden imports
        for forbidden in self.forbidden_imports:
            if re.search(rf'\b(import\s+{forbidden}|from\s+{forbidden})', code_lower):
                violations.append(f"import {forbidden}")
        
        # Check forbidden functions
        for forbidden in self.forbidden_functions:
            if re.search(rf'\b{forbidden}\s*\(', code_lower):
                violations.append(f"{forbidden}()")
        
        # Check dangerous patterns
        dangerous_patterns = [
            (r'__.*__', 'dunder methods'),
            (r'\..*\(.*\)', 'method calls on objects'),
            (r'open\s*\(', 'file operations'),
            (r'exec\s*\(', 'dynamic execution'),
            (r'eval\s*\(', 'dynamic evaluation'),
        ]
        
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, code_lower):
                violations.append(desc)
        
        if violations:
            return {
                'safe': False,
                'reason': 'Code contains forbidden operations',
                'violations': violations
            }
        
        # Additional length check
        if len(code) > 1000:
            return {
                'safe': False,
                'reason': 'Code too long (max 1000 characters)',
                'violations': ['code length > 1000']
            }
        
        return {'safe': True, 'reason': 'Code is safe', 'violations': []}
    
    async def _execute_code_safely(self, code):
        """Execute code in a safe environment"""
        try:
            # Create safe namespace
            safe_namespace = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'abs': abs,
                    'round': round,
                    'pow': pow,
                    'divmod': divmod,
                }
            }
            
            # Add safe math operations
            import math
            safe_namespace['math'] = math
            
            # Capture output
            old_stdout = sys.stdout
            captured_output = io.StringIO()
            
            return_value = None
            
            try:
                sys.stdout = captured_output
                
                # Try to evaluate as expression first (for calculations)
                try:
                    return_value = eval(code, safe_namespace)
                    if return_value is not None:
                        print(return_value)
                except SyntaxError:
                    # If not an expression, execute as statement
                    exec(code, safe_namespace)
                
                output = captured_output.getvalue()
                
                return {
                    'success': True,
                    'output': output.strip() if output.strip() else None,
                    'return_value': return_value,
                    'error': None
                }
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'return_value': None,
                'error': str(e)
            }
    
    async def send_pending_results(self, client, result_ids):
        """Send pending Python execution results"""
        sent_results = []
        
        for result_id in result_ids:
            if result_id in self.pending_results:
                result_data = self.pending_results[result_id]
                
                try:
                    await client.send_message(
                        chat_id=result_data['chat_id'],
                        text=result_data['text'],
                        reply_to_message_id=result_data['reply_to_message_id']
                    )
                    sent_results.append(result_id)
                    console.info(f"[PYTHON:EXEC] Sent result: {result_id}")
                    
                except Exception as e:
                    console.error(f"[PYTHON:EXEC] Error sending result {result_id}: {e}")
                    
                # Clean up
                del self.pending_results[result_id]
                
        return sent_results 