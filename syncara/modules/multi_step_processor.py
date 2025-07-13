"""
Multi-Step Processing System untuk SyncaraBot

Sistem ini memungkinkan pemrosesan bertahap dengan state management,
workflow definition, dan error handling yang robust.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from uuid import uuid4
import traceback

from syncara.console import console
from syncara.database import db

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class StepResult:
    """Result dari eksekusi step"""
    success: bool
    data: Any = None
    error: str = None
    execution_time: float = 0
    metadata: Dict[str, Any] = None

@dataclass
class WorkflowStep:
    """Definisi step dalam workflow"""
    id: str
    name: str
    handler: str  # Nama handler function
    params: Dict[str, Any]
    dependencies: List[str] = None  # Step IDs yang harus selesai dulu
    timeout: int = 300  # 5 menit default
    retry_count: int = 3
    retry_delay: int = 5
    condition: Optional[str] = None  # Kondisi untuk menjalankan step
    status: StepStatus = StepStatus.PENDING
    result: Optional[StepResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0

@dataclass
class WorkflowDefinition:
    """Definisi workflow lengkap"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    global_timeout: int = 1800  # 30 menit
    max_parallel_steps: int = 5
    auto_retry: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class WorkflowExecution:
    """Eksekusi workflow dengan state management"""
    id: str
    workflow_id: str
    definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_step: Optional[str] = None
    context: Dict[str, Any] = None  # Shared context antar steps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None
    message_id: Optional[int] = None
    progress: float = 0.0  # 0-100%

class MultiStepProcessor:
    """
    Processor untuk menangani multi-step workflows
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
        # Load built-in handlers
        self._register_builtin_handlers()
        
        # Start background processor
        self.processor_task = None
        
    def _register_builtin_handlers(self):
        """Register built-in step handlers"""
        self.handlers.update({
            'delay': self._handler_delay,
            'log': self._handler_log,
            'send_message': self._handler_send_message,
            'execute_shortcode': self._handler_execute_shortcode,
            'set_context': self._handler_set_context,
            'get_context': self._handler_get_context,
            'condition_check': self._handler_condition_check,
            'parallel_group': self._handler_parallel_group,
            'api_call': self._handler_api_call,
            'file_operation': self._handler_file_operation,
            'database_operation': self._handler_database_operation,
            'notification': self._handler_notification,
        })
    
    def register_handler(self, name: str, handler: Callable):
        """Register custom step handler"""
        self.handlers[name] = handler
        console.info(f"✅ Handler '{name}' registered")
    
    def create_workflow(self, 
                       name: str, 
                       description: str = "",
                       global_timeout: int = 1800,
                       max_parallel_steps: int = 5,
                       auto_retry: bool = True,
                       metadata: Dict[str, Any] = None) -> str:
        """Create new workflow definition"""
        workflow_id = str(uuid4())
        
        workflow = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            steps=[],
            global_timeout=global_timeout,
            max_parallel_steps=max_parallel_steps,
            auto_retry=auto_retry,
            metadata=metadata or {}
        )
        
        self.workflows[workflow_id] = workflow
        console.info(f"✅ Workflow '{name}' created with ID: {workflow_id}")
        return workflow_id
    
    def add_step(self, 
                workflow_id: str,
                name: str,
                handler: str,
                params: Dict[str, Any] = None,
                dependencies: List[str] = None,
                timeout: int = 300,
                retry_count: int = 3,
                retry_delay: int = 5,
                condition: str = None) -> str:
        """Add step to workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        step_id = str(uuid4())
        step = WorkflowStep(
            id=step_id,
            name=name,
            handler=handler,
            params=params or {},
            dependencies=dependencies or [],
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            condition=condition
        )
        
        self.workflows[workflow_id].steps.append(step)
        console.info(f"✅ Step '{name}' added to workflow {workflow_id}")
        return step_id
    
    async def execute_workflow(self, 
                             workflow_id: str,
                             context: Dict[str, Any] = None,
                             user_id: int = None,
                             chat_id: int = None,
                             message_id: int = None) -> str:
        """Execute workflow asynchronously"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        execution_id = str(uuid4())
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            definition=self.workflows[workflow_id],
            context=context or {},
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            started_at=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        # Start execution task
        task = asyncio.create_task(self._execute_workflow_task(execution_id))
        self.running_tasks[execution_id] = task
        
        console.info(f"🚀 Workflow execution started: {execution_id}")
        return execution_id
    
    async def _execute_workflow_task(self, execution_id: str):
        """Main workflow execution task"""
        execution = self.executions[execution_id]
        
        try:
            execution.status = WorkflowStatus.RUNNING
            await self._save_execution_state(execution)
            
            # Execute steps
            await self._execute_steps(execution)
            
            # Mark as completed
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.progress = 100.0
            
            console.info(f"✅ Workflow execution completed: {execution_id}")
            
        except asyncio.CancelledError:
            execution.status = WorkflowStatus.CANCELLED
            console.warning(f"⚠️ Workflow execution cancelled: {execution_id}")
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()
            console.error(f"❌ Workflow execution failed: {execution_id} - {str(e)}")
            console.error(traceback.format_exc())
        finally:
            await self._save_execution_state(execution)
            if execution_id in self.running_tasks:
                del self.running_tasks[execution_id]
    
    async def _execute_steps(self, execution: WorkflowExecution):
        """Execute all steps in workflow"""
        definition = execution.definition
        completed_steps = set()
        running_steps = {}
        
        while len(completed_steps) < len(definition.steps):
            # Find ready steps
            ready_steps = []
            for step in definition.steps:
                if (step.id not in completed_steps and 
                    step.id not in running_steps and
                    step.status == StepStatus.PENDING):
                    
                    # Check dependencies
                    if self._check_dependencies(step, completed_steps):
                        # Check condition
                        if await self._check_condition(step, execution):
                            ready_steps.append(step)
            
            if not ready_steps and not running_steps:
                # No more steps to run
                break
            
            # Start ready steps (up to max parallel)
            available_slots = definition.max_parallel_steps - len(running_steps)
            for step in ready_steps[:available_slots]:
                task = asyncio.create_task(self._execute_step(step, execution))
                running_steps[step.id] = task
                step.status = StepStatus.RUNNING
                step.started_at = datetime.now()
                execution.current_step = step.id
                
                console.info(f"🔄 Starting step: {step.name} ({step.id})")
            
            # Wait for at least one step to complete
            if running_steps:
                done, pending = await asyncio.wait(
                    running_steps.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed steps
                for task in done:
                    step_id = None
                    for sid, t in running_steps.items():
                        if t == task:
                            step_id = sid
                            break
                    
                    if step_id:
                        step = next(s for s in definition.steps if s.id == step_id)
                        try:
                            result = await task
                            if result.success:
                                step.status = StepStatus.COMPLETED
                                completed_steps.add(step_id)
                                console.info(f"✅ Step completed: {step.name}")
                            else:
                                step.status = StepStatus.FAILED
                                console.error(f"❌ Step failed: {step.name} - {result.error}")
                                
                                if not definition.auto_retry or step.attempts >= step.retry_count:
                                    raise Exception(f"Step {step.name} failed: {result.error}")
                                
                        except Exception as e:
                            step.status = StepStatus.FAILED
                            console.error(f"❌ Step error: {step.name} - {str(e)}")
                            
                            if not definition.auto_retry or step.attempts >= step.retry_count:
                                raise
                        
                        finally:
                            step.completed_at = datetime.now()
                            del running_steps[step_id]
                            
                            # Update progress
                            execution.progress = (len(completed_steps) / len(definition.steps)) * 100
                            await self._save_execution_state(execution)
            
            # Small delay to prevent tight loop
            await asyncio.sleep(0.1)
    
    async def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Execute single step"""
        step.attempts += 1
        start_time = time.time()
        
        try:
            # Get handler
            if step.handler not in self.handlers:
                raise ValueError(f"Handler '{step.handler}' not found")
            
            handler = self.handlers[step.handler]
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(step, execution),
                timeout=step.timeout
            )
            
            execution_time = time.time() - start_time
            
            if isinstance(result, StepResult):
                result.execution_time = execution_time
                step.result = result
                return result
            else:
                # Wrap result
                step_result = StepResult(
                    success=True,
                    data=result,
                    execution_time=execution_time
                )
                step.result = step_result
                return step_result
                
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Step timeout after {step.timeout} seconds"
            
            result = StepResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            step.result = result
            
            # Retry if configured
            if step.attempts < step.retry_count:
                console.warning(f"⏰ Step timeout, retrying: {step.name} (attempt {step.attempts}/{step.retry_count})")
                await asyncio.sleep(step.retry_delay)
                return await self._execute_step(step, execution)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            result = StepResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            step.result = result
            
            # Retry if configured
            if step.attempts < step.retry_count:
                console.warning(f"❌ Step failed, retrying: {step.name} (attempt {step.attempts}/{step.retry_count}) - {error_msg}")
                await asyncio.sleep(step.retry_delay)
                return await self._execute_step(step, execution)
            
            return result
    
    def _check_dependencies(self, step: WorkflowStep, completed_steps: set) -> bool:
        """Check if step dependencies are satisfied"""
        if not step.dependencies:
            return True
        
        return all(dep_id in completed_steps for dep_id in step.dependencies)
    
    async def _check_condition(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Check if step condition is satisfied"""
        if not step.condition:
            return True
        
        try:
            # Simple condition evaluation
            # Format: "context.key == 'value'" or "context.key > 10"
            condition = step.condition.replace("context.", "execution.context.")
            return eval(condition)
        except Exception as e:
            console.error(f"Error evaluating condition '{step.condition}': {str(e)}")
            return False
    
    async def _save_execution_state(self, execution: WorkflowExecution):
        """Save execution state to database"""
        try:
            # Convert to dict for JSON serialization
            execution_dict = {
                'id': execution.id,
                'workflow_id': execution.workflow_id,
                'status': execution.status.value,
                'current_step': execution.current_step,
                'context': execution.context,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'user_id': execution.user_id,
                'chat_id': execution.chat_id,
                'message_id': execution.message_id,
                'progress': execution.progress,
                'steps': []
            }
            
            # Add step states
            for step in execution.definition.steps:
                step_dict = {
                    'id': step.id,
                    'name': step.name,
                    'status': step.status.value,
                    'attempts': step.attempts,
                    'started_at': step.started_at.isoformat() if step.started_at else None,
                    'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                }
                
                if step.result:
                    step_dict['result'] = {
                        'success': step.result.success,
                        'data': step.result.data,
                        'error': step.result.error,
                        'execution_time': step.result.execution_time,
                        'metadata': step.result.metadata
                    }
                
                execution_dict['steps'].append(step_dict)
            
            # Save to database
            await db.workflow_executions.update_one(
                {'id': execution.id},
                {'$set': execution_dict},
                upsert=True
            )
            
        except Exception as e:
            console.error(f"Error saving execution state: {str(e)}")
    
    # ==================== BUILT-IN HANDLERS ====================
    
    async def _handler_delay(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk delay/sleep"""
        seconds = step.params.get('seconds', 1)
        await asyncio.sleep(seconds)
        return StepResult(success=True, data=f"Delayed for {seconds} seconds")
    
    async def _handler_log(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk logging"""
        message = step.params.get('message', 'Log message')
        level = step.params.get('level', 'info')
        
        if level == 'error':
            console.error(message)
        elif level == 'warning':
            console.warning(message)
        else:
            console.info(message)
        
        return StepResult(success=True, data=message)
    
    async def _handler_send_message(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk mengirim pesan"""
        try:
            from syncara import bot
            
            text = step.params.get('text', 'Test message')
            chat_id = step.params.get('chat_id') or execution.chat_id
            
            if not chat_id:
                return StepResult(success=False, error="No chat_id provided")
            
            # Replace context variables in text
            if execution.context:
                for key, value in execution.context.items():
                    text = text.replace(f"{{context.{key}}}", str(value))
            
            message = await bot.send_message(chat_id, text)
            return StepResult(success=True, data=message.id)
            
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def _handler_execute_shortcode(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk mengeksekusi shortcode"""
        try:
            from syncara.shortcode import registry
            from syncara import bot
            
            shortcode = step.params.get('shortcode')
            params = step.params.get('params', '')
            
            if not shortcode:
                return StepResult(success=False, error="No shortcode provided")
            
            # Create mock message object
            class MockMessage:
                def __init__(self, chat_id, user_id, message_id):
                    self.chat = type('Chat', (), {'id': chat_id})()
                    self.from_user = type('User', (), {'id': user_id})()
                    self.id = message_id
            
            mock_message = MockMessage(
                execution.chat_id or 0,
                execution.user_id or 0,
                execution.message_id or 0
            )
            
            success = await registry.execute_shortcode(shortcode, bot, mock_message, params)
            return StepResult(success=success, data=f"Shortcode {shortcode} executed")
            
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def _handler_set_context(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk set context variable"""
        key = step.params.get('key')
        value = step.params.get('value')
        
        if not key:
            return StepResult(success=False, error="No key provided")
        
        execution.context[key] = value
        return StepResult(success=True, data=f"Context {key} set to {value}")
    
    async def _handler_get_context(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk get context variable"""
        key = step.params.get('key')
        
        if not key:
            return StepResult(success=False, error="No key provided")
        
        value = execution.context.get(key)
        return StepResult(success=True, data=value)
    
    async def _handler_condition_check(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk condition check"""
        condition = step.params.get('condition')
        
        if not condition:
            return StepResult(success=False, error="No condition provided")
        
        try:
            # Simple condition evaluation
            condition = condition.replace("context.", "execution.context.")
            result = eval(condition)
            return StepResult(success=True, data=result)
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def _handler_parallel_group(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk parallel group execution"""
        tasks = step.params.get('tasks', [])
        
        if not tasks:
            return StepResult(success=False, error="No tasks provided")
        
        # Execute tasks in parallel
        results = []
        for task_def in tasks:
            # Create sub-step
            sub_step = WorkflowStep(
                id=str(uuid4()),
                name=task_def.get('name', 'Parallel task'),
                handler=task_def.get('handler'),
                params=task_def.get('params', {})
            )
            
            result = await self._execute_step(sub_step, execution)
            results.append(result)
        
        # Check if all succeeded
        all_success = all(r.success for r in results)
        return StepResult(success=all_success, data=results)
    
    async def _handler_api_call(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk API call"""
        try:
            import aiohttp
            
            url = step.params.get('url')
            method = step.params.get('method', 'GET').upper()
            headers = step.params.get('headers', {})
            data = step.params.get('data')
            
            if not url:
                return StepResult(success=False, error="No URL provided")
            
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    result_data = await response.text()
                    
                    if response.status < 400:
                        return StepResult(success=True, data=result_data)
                    else:
                        return StepResult(success=False, error=f"HTTP {response.status}: {result_data}")
                        
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def _handler_file_operation(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk file operations"""
        try:
            import aiofiles
            
            operation = step.params.get('operation')  # read, write, append, delete
            file_path = step.params.get('file_path')
            content = step.params.get('content')
            
            if not operation or not file_path:
                return StepResult(success=False, error="Operation and file_path required")
            
            if operation == 'read':
                async with aiofiles.open(file_path, 'r') as f:
                    data = await f.read()
                return StepResult(success=True, data=data)
            
            elif operation == 'write':
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(content or '')
                return StepResult(success=True, data=f"File written: {file_path}")
            
            elif operation == 'append':
                async with aiofiles.open(file_path, 'a') as f:
                    await f.write(content or '')
                return StepResult(success=True, data=f"Content appended to: {file_path}")
            
            elif operation == 'delete':
                import os
                os.remove(file_path)
                return StepResult(success=True, data=f"File deleted: {file_path}")
            
            else:
                return StepResult(success=False, error=f"Unknown operation: {operation}")
                
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def _handler_database_operation(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk database operations"""
        try:
            operation = step.params.get('operation')  # find, insert, update, delete
            collection = step.params.get('collection')
            query = step.params.get('query', {})
            data = step.params.get('data', {})
            
            if not operation or not collection:
                return StepResult(success=False, error="Operation and collection required")
            
            db_collection = getattr(db, collection)
            
            if operation == 'find':
                result = await db_collection.find(query).to_list(length=None)
                return StepResult(success=True, data=result)
            
            elif operation == 'insert':
                result = await db_collection.insert_one(data)
                return StepResult(success=True, data=str(result.inserted_id))
            
            elif operation == 'update':
                result = await db_collection.update_one(query, {'$set': data})
                return StepResult(success=True, data=f"Modified: {result.modified_count}")
            
            elif operation == 'delete':
                result = await db_collection.delete_one(query)
                return StepResult(success=True, data=f"Deleted: {result.deleted_count}")
            
            else:
                return StepResult(success=False, error=f"Unknown operation: {operation}")
                
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def _handler_notification(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Handler untuk notification"""
        try:
            message = step.params.get('message', 'Notification')
            notification_type = step.params.get('type', 'info')  # info, warning, error, success
            
            if notification_type == 'error':
                console.error(f"🔔 {message}")
            elif notification_type == 'warning':
                console.warning(f"🔔 {message}")
            elif notification_type == 'success':
                console.info(f"🔔 ✅ {message}")
            else:
                console.info(f"🔔 {message}")
            
            return StepResult(success=True, data=message)
            
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    # ==================== MANAGEMENT METHODS ====================
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition"""
        return self.workflows.get(workflow_id)
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution"""
        return self.executions.get(execution_id)
    
    def list_workflows(self) -> List[WorkflowDefinition]:
        """List all workflows"""
        return list(self.workflows.values())
    
    def list_executions(self, status: WorkflowStatus = None) -> List[WorkflowExecution]:
        """List workflow executions"""
        executions = list(self.executions.values())
        if status:
            executions = [e for e in executions if e.status == status]
        return executions
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        if execution_id in self.running_tasks:
            self.running_tasks[execution_id].cancel()
            return True
        return False
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause workflow execution"""
        if execution_id in self.executions:
            self.executions[execution_id].status = WorkflowStatus.PAUSED
            return True
        return False
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume workflow execution"""
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            if execution.status == WorkflowStatus.PAUSED:
                execution.status = WorkflowStatus.RUNNING
                # Restart execution task
                task = asyncio.create_task(self._execute_workflow_task(execution_id))
                self.running_tasks[execution_id] = task
                return True
        return False
    
    def get_execution_progress(self, execution_id: str) -> Dict[str, Any]:
        """Get execution progress"""
        if execution_id not in self.executions:
            return {}
        
        execution = self.executions[execution_id]
        
        return {
            'id': execution.id,
            'workflow_name': execution.definition.name,
            'status': execution.status.value,
            'progress': execution.progress,
            'current_step': execution.current_step,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'steps': [
                {
                    'id': step.id,
                    'name': step.name,
                    'status': step.status.value,
                    'attempts': step.attempts,
                    'execution_time': step.result.execution_time if step.result else 0
                }
                for step in execution.definition.steps
            ]
        }

# Global instance
multi_step_processor = MultiStepProcessor() 