"""
Multi-Step Processing Shortcode Management

Shortcode untuk mengelola multi-step workflows dari AI response.
"""

import asyncio
import json
from typing import Dict, List, Any
from syncara.console import console
from syncara.modules.multi_step_processor import multi_step_processor, WorkflowStatus

class MultiStepManagementShortcode:
    def __init__(self):
        self.handlers = {
            'MULTISTEP:CREATE_WORKFLOW': self.create_workflow,
            'MULTISTEP:ADD_STEP': self.add_step,
            'MULTISTEP:EXECUTE': self.execute_workflow,
            'MULTISTEP:STATUS': self.get_status,
            'MULTISTEP:PROGRESS': self.get_progress,
            'MULTISTEP:CANCEL': self.cancel_execution,
            'MULTISTEP:PAUSE': self.pause_execution,
            'MULTISTEP:RESUME': self.resume_execution,
            'MULTISTEP:LIST_WORKFLOWS': self.list_workflows,
            'MULTISTEP:LIST_EXECUTIONS': self.list_executions,
            'MULTISTEP:QUICK_WORKFLOW': self.quick_workflow,
            'MULTISTEP:BATCH_PROCESS': self.batch_process,
            'MULTISTEP:SCHEDULED_WORKFLOW': self.scheduled_workflow,
            'MULTISTEP:TEMPLATE_WORKFLOW': self.template_workflow,
        }
    
    async def create_workflow(self, client, message, params):
        """Create new workflow: name:description:timeout:max_parallel"""
        try:
            parts = params.split(':', 3)
            if len(parts) < 1:
                return "❌ Format: MULTISTEP:CREATE_WORKFLOW:workflow_name:description:timeout:max_parallel"
            
            name = parts[0]
            description = parts[1] if len(parts) > 1 else ""
            timeout = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1800
            max_parallel = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 5
            
            workflow_id = multi_step_processor.create_workflow(
                name=name,
                description=description,
                global_timeout=timeout,
                max_parallel_steps=max_parallel
            )
            
            return f"✅ Workflow '{name}' created!\n🆔 ID: `{workflow_id}`"
            
        except Exception as e:
            console.error(f"Error creating workflow: {str(e)}")
            return f"❌ Error creating workflow: {str(e)}"
    
    async def add_step(self, client, message, params):
        """Add step to workflow: workflow_id:step_name:handler:params_json:dependencies:timeout"""
        try:
            parts = params.split(':', 5)
            if len(parts) < 3:
                return "❌ Format: MULTISTEP:ADD_STEP:workflow_id:step_name:handler:params_json:dependencies:timeout"
            
            workflow_id = parts[0]
            step_name = parts[1]
            handler = parts[2]
            
            # Parse params JSON
            step_params = {}
            if len(parts) > 3 and parts[3]:
                try:
                    step_params = json.loads(parts[3])
                except json.JSONDecodeError:
                    return "❌ Invalid JSON in params"
            
            # Parse dependencies
            dependencies = []
            if len(parts) > 4 and parts[4]:
                dependencies = parts[4].split(',')
            
            # Parse timeout
            timeout = 300
            if len(parts) > 5 and parts[5].isdigit():
                timeout = int(parts[5])
            
            step_id = multi_step_processor.add_step(
                workflow_id=workflow_id,
                name=step_name,
                handler=handler,
                params=step_params,
                dependencies=dependencies,
                timeout=timeout
            )
            
            return f"✅ Step '{step_name}' added to workflow!\n🆔 Step ID: `{step_id}`"
            
        except Exception as e:
            console.error(f"Error adding step: {str(e)}")
            return f"❌ Error adding step: {str(e)}"
    
    async def execute_workflow(self, client, message, params):
        """Execute workflow: workflow_id:context_json"""
        try:
            parts = params.split(':', 1)
            if len(parts) < 1:
                return "❌ Format: MULTISTEP:EXECUTE:workflow_id:context_json"
            
            workflow_id = parts[0]
            
            # Parse context JSON
            context = {}
            if len(parts) > 1 and parts[1]:
                try:
                    context = json.loads(parts[1])
                except json.JSONDecodeError:
                    return "❌ Invalid JSON in context"
            
            execution_id = await multi_step_processor.execute_workflow(
                workflow_id=workflow_id,
                context=context,
                user_id=message.from_user.id if message.from_user else None,
                chat_id=message.chat.id,
                message_id=message.id
            )
            
            return f"🚀 Workflow execution started!\n🆔 Execution ID: `{execution_id}`\n\n💡 Use `MULTISTEP:STATUS:{execution_id}` untuk cek progress"
            
        except Exception as e:
            console.error(f"Error executing workflow: {str(e)}")
            return f"❌ Error executing workflow: {str(e)}"
    
    async def get_status(self, client, message, params):
        """Get execution status: execution_id"""
        try:
            execution_id = params.strip()
            if not execution_id:
                return "❌ Format: MULTISTEP:STATUS:execution_id"
            
            execution = multi_step_processor.get_execution(execution_id)
            if not execution:
                return f"❌ Execution {execution_id} not found"
            
            progress = multi_step_processor.get_execution_progress(execution_id)
            
            status_text = f"📊 **Workflow Status**\n"
            status_text += f"🆔 ID: `{execution.id}`\n"
            status_text += f"📝 Name: {execution.definition.name}\n"
            status_text += f"📈 Status: {execution.status.value.upper()}\n"
            status_text += f"⏳ Progress: {progress['progress']:.1f}%\n"
            
            if execution.started_at:
                status_text += f"🕐 Started: {execution.started_at.strftime('%H:%M:%S')}\n"
            
            if execution.completed_at:
                status_text += f"🏁 Completed: {execution.completed_at.strftime('%H:%M:%S')}\n"
            
            if execution.current_step:
                current_step = next(
                    (s for s in execution.definition.steps if s.id == execution.current_step),
                    None
                )
                if current_step:
                    status_text += f"🔄 Current Step: {current_step.name}\n"
            
            # Show step details
            status_text += f"\n📋 **Steps:**\n"
            for step_info in progress['steps']:
                status_icon = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌',
                    'cancelled': '⏹️'
                }.get(step_info['status'], '❓')
                
                status_text += f"{status_icon} {step_info['name']} ({step_info['status']})\n"
                if step_info['execution_time'] > 0:
                    status_text += f"   ⏱️ {step_info['execution_time']:.2f}s\n"
            
            return status_text
            
        except Exception as e:
            console.error(f"Error getting status: {str(e)}")
            return f"❌ Error getting status: {str(e)}"
    
    async def get_progress(self, client, message, params):
        """Get execution progress: execution_id"""
        try:
            execution_id = params.strip()
            if not execution_id:
                return "❌ Format: MULTISTEP:PROGRESS:execution_id"
            
            progress = multi_step_processor.get_execution_progress(execution_id)
            if not progress:
                return f"❌ Execution {execution_id} not found"
            
            progress_bar = self._create_progress_bar(progress['progress'])
            
            return f"📊 **Progress: {progress['progress']:.1f}%**\n{progress_bar}\n\n📝 Workflow: {progress['workflow_name']}\n📈 Status: {progress['status'].upper()}"
            
        except Exception as e:
            console.error(f"Error getting progress: {str(e)}")
            return f"❌ Error getting progress: {str(e)}"
    
    async def cancel_execution(self, client, message, params):
        """Cancel execution: execution_id"""
        try:
            execution_id = params.strip()
            if not execution_id:
                return "❌ Format: MULTISTEP:CANCEL:execution_id"
            
            success = await multi_step_processor.cancel_execution(execution_id)
            
            if success:
                return f"✅ Execution {execution_id} cancelled"
            else:
                return f"❌ Failed to cancel execution {execution_id}"
                
        except Exception as e:
            console.error(f"Error cancelling execution: {str(e)}")
            return f"❌ Error cancelling execution: {str(e)}"
    
    async def pause_execution(self, client, message, params):
        """Pause execution: execution_id"""
        try:
            execution_id = params.strip()
            if not execution_id:
                return "❌ Format: MULTISTEP:PAUSE:execution_id"
            
            success = await multi_step_processor.pause_execution(execution_id)
            
            if success:
                return f"⏸️ Execution {execution_id} paused"
            else:
                return f"❌ Failed to pause execution {execution_id}"
                
        except Exception as e:
            console.error(f"Error pausing execution: {str(e)}")
            return f"❌ Error pausing execution: {str(e)}"
    
    async def resume_execution(self, client, message, params):
        """Resume execution: execution_id"""
        try:
            execution_id = params.strip()
            if not execution_id:
                return "❌ Format: MULTISTEP:RESUME:execution_id"
            
            success = await multi_step_processor.resume_execution(execution_id)
            
            if success:
                return f"▶️ Execution {execution_id} resumed"
            else:
                return f"❌ Failed to resume execution {execution_id}"
                
        except Exception as e:
            console.error(f"Error resuming execution: {str(e)}")
            return f"❌ Error resuming execution: {str(e)}"
    
    async def list_workflows(self, client, message, params):
        """List all workflows"""
        try:
            workflows = multi_step_processor.list_workflows()
            
            if not workflows:
                return "📝 No workflows found"
            
            result = "📋 **Available Workflows:**\n\n"
            for workflow in workflows:
                result += f"🆔 `{workflow.id}`\n"
                result += f"📝 **{workflow.name}**\n"
                result += f"📄 {workflow.description}\n"
                result += f"🔧 {len(workflow.steps)} steps\n"
                result += f"⏰ Timeout: {workflow.global_timeout}s\n\n"
            
            return result
            
        except Exception as e:
            console.error(f"Error listing workflows: {str(e)}")
            return f"❌ Error listing workflows: {str(e)}"
    
    async def list_executions(self, client, message, params):
        """List executions: status (optional)"""
        try:
            status_filter = None
            if params.strip():
                try:
                    status_filter = WorkflowStatus(params.strip().lower())
                except ValueError:
                    return f"❌ Invalid status: {params}. Valid: created, running, paused, completed, failed, cancelled"
            
            executions = multi_step_processor.list_executions(status_filter)
            
            if not executions:
                return "📝 No executions found"
            
            result = "📊 **Workflow Executions:**\n\n"
            for execution in executions[:10]:  # Limit to 10
                result += f"🆔 `{execution.id}`\n"
                result += f"📝 {execution.definition.name}\n"
                result += f"📈 Status: {execution.status.value.upper()}\n"
                result += f"⏳ Progress: {execution.progress:.1f}%\n"
                if execution.started_at:
                    result += f"🕐 Started: {execution.started_at.strftime('%H:%M:%S')}\n"
                result += "\n"
            
            if len(executions) > 10:
                result += f"... and {len(executions) - 10} more"
            
            return result
            
        except Exception as e:
            console.error(f"Error listing executions: {str(e)}")
            return f"❌ Error listing executions: {str(e)}"
    
    async def quick_workflow(self, client, message, params):
        """Quick workflow creation: name:steps_json"""
        try:
            parts = params.split(':', 1)
            if len(parts) < 2:
                return "❌ Format: MULTISTEP:QUICK_WORKFLOW:name:steps_json"
            
            name = parts[0]
            
            try:
                steps_config = json.loads(parts[1])
            except json.JSONDecodeError:
                return "❌ Invalid JSON in steps configuration"
            
            # Create workflow
            workflow_id = multi_step_processor.create_workflow(name=name)
            
            # Add steps
            for step_config in steps_config:
                multi_step_processor.add_step(
                    workflow_id=workflow_id,
                    name=step_config.get('name', 'Step'),
                    handler=step_config.get('handler', 'log'),
                    params=step_config.get('params', {}),
                    dependencies=step_config.get('dependencies', []),
                    timeout=step_config.get('timeout', 300)
                )
            
            # Execute immediately
            execution_id = await multi_step_processor.execute_workflow(
                workflow_id=workflow_id,
                user_id=message.from_user.id if message.from_user else None,
                chat_id=message.chat.id,
                message_id=message.id
            )
            
            return f"🚀 Quick workflow '{name}' created and started!\n🆔 Execution ID: `{execution_id}`"
            
        except Exception as e:
            console.error(f"Error creating quick workflow: {str(e)}")
            return f"❌ Error creating quick workflow: {str(e)}"
    
    async def batch_process(self, client, message, params):
        """Batch process multiple items: handler:items_json:batch_size"""
        try:
            parts = params.split(':', 2)
            if len(parts) < 2:
                return "❌ Format: MULTISTEP:BATCH_PROCESS:handler:items_json:batch_size"
            
            handler = parts[0]
            batch_size = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 5
            
            try:
                items = json.loads(parts[1])
            except json.JSONDecodeError:
                return "❌ Invalid JSON in items"
            
            # Create batch workflow
            workflow_id = multi_step_processor.create_workflow(
                name=f"Batch Process ({len(items)} items)",
                max_parallel_steps=batch_size
            )
            
            # Add steps for each item
            for i, item in enumerate(items):
                multi_step_processor.add_step(
                    workflow_id=workflow_id,
                    name=f"Process Item {i+1}",
                    handler=handler,
                    params=item if isinstance(item, dict) else {'data': item}
                )
            
            # Execute
            execution_id = await multi_step_processor.execute_workflow(
                workflow_id=workflow_id,
                user_id=message.from_user.id if message.from_user else None,
                chat_id=message.chat.id,
                message_id=message.id
            )
            
            return f"🚀 Batch processing started for {len(items)} items!\n🆔 Execution ID: `{execution_id}`"
            
        except Exception as e:
            console.error(f"Error creating batch process: {str(e)}")
            return f"❌ Error creating batch process: {str(e)}"
    
    async def scheduled_workflow(self, client, message, params):
        """Schedule workflow execution: workflow_id:delay_seconds:context_json"""
        try:
            parts = params.split(':', 2)
            if len(parts) < 2:
                return "❌ Format: MULTISTEP:SCHEDULED_WORKFLOW:workflow_id:delay_seconds:context_json"
            
            workflow_id = parts[0]
            delay_seconds = int(parts[1])
            
            context = {}
            if len(parts) > 2 and parts[2]:
                try:
                    context = json.loads(parts[2])
                except json.JSONDecodeError:
                    return "❌ Invalid JSON in context"
            
            # Schedule execution
            async def delayed_execution():
                await asyncio.sleep(delay_seconds)
                execution_id = await multi_step_processor.execute_workflow(
                    workflow_id=workflow_id,
                    context=context,
                    user_id=message.from_user.id if message.from_user else None,
                    chat_id=message.chat.id,
                    message_id=message.id
                )
                
                # Send notification
                try:
                    await client.send_message(
                        chat_id=message.chat.id,
                        text=f"⏰ Scheduled workflow started!\n🆔 Execution ID: `{execution_id}`"
                    )
                except:
                    pass
            
            asyncio.create_task(delayed_execution())
            
            return f"⏰ Workflow scheduled to run in {delay_seconds} seconds"
            
        except Exception as e:
            console.error(f"Error scheduling workflow: {str(e)}")
            return f"❌ Error scheduling workflow: {str(e)}"
    
    async def template_workflow(self, client, message, params):
        """Create workflow from template: template_name:params_json"""
        try:
            parts = params.split(':', 1)
            if len(parts) < 1:
                return "❌ Format: MULTISTEP:TEMPLATE_WORKFLOW:template_name:params_json"
            
            template_name = parts[0]
            template_params = {}
            
            if len(parts) > 1 and parts[1]:
                try:
                    template_params = json.loads(parts[1])
                except json.JSONDecodeError:
                    return "❌ Invalid JSON in template params"
            
            # Define templates
            templates = {
                'message_sequence': {
                    'name': 'Message Sequence',
                    'steps': [
                        {
                            'name': 'Send Welcome',
                            'handler': 'send_message',
                            'params': {'text': template_params.get('welcome_text', 'Welcome!')}
                        },
                        {
                            'name': 'Delay',
                            'handler': 'delay',
                            'params': {'seconds': template_params.get('delay', 2)}
                        },
                        {
                            'name': 'Send Follow-up',
                            'handler': 'send_message',
                            'params': {'text': template_params.get('followup_text', 'Follow-up message')}
                        }
                    ]
                },
                'data_processing': {
                    'name': 'Data Processing Pipeline',
                    'steps': [
                        {
                            'name': 'Load Data',
                            'handler': 'database_operation',
                            'params': {
                                'operation': 'find',
                                'collection': template_params.get('collection', 'data'),
                                'query': template_params.get('query', {})
                            }
                        },
                        {
                            'name': 'Process Data',
                            'handler': 'log',
                            'params': {'message': 'Processing data...'}
                        },
                        {
                            'name': 'Save Results',
                            'handler': 'database_operation',
                            'params': {
                                'operation': 'insert',
                                'collection': template_params.get('output_collection', 'results'),
                                'data': template_params.get('output_data', {})
                            }
                        }
                    ]
                },
                'notification_flow': {
                    'name': 'Notification Flow',
                    'steps': [
                        {
                            'name': 'Send Notification',
                            'handler': 'notification',
                            'params': {
                                'message': template_params.get('message', 'Notification'),
                                'type': template_params.get('type', 'info')
                            }
                        },
                        {
                            'name': 'Log Event',
                            'handler': 'log',
                            'params': {'message': f"Notification sent: {template_params.get('message', 'Notification')}"}
                        }
                    ]
                }
            }
            
            if template_name not in templates:
                available = ', '.join(templates.keys())
                return f"❌ Template '{template_name}' not found. Available: {available}"
            
            template = templates[template_name]
            
            # Create workflow
            workflow_id = multi_step_processor.create_workflow(name=template['name'])
            
            # Add steps
            for step_config in template['steps']:
                multi_step_processor.add_step(
                    workflow_id=workflow_id,
                    name=step_config['name'],
                    handler=step_config['handler'],
                    params=step_config['params']
                )
            
            # Execute
            execution_id = await multi_step_processor.execute_workflow(
                workflow_id=workflow_id,
                user_id=message.from_user.id if message.from_user else None,
                chat_id=message.chat.id,
                message_id=message.id
            )
            
            return f"🚀 Template workflow '{template['name']}' created and started!\n🆔 Execution ID: `{execution_id}`"
            
        except Exception as e:
            console.error(f"Error creating template workflow: {str(e)}")
            return f"❌ Error creating template workflow: {str(e)}"
    
    def _create_progress_bar(self, progress: float, length: int = 20) -> str:
        """Create text progress bar"""
        filled = int(progress / 100 * length)
        empty = length - filled
        bar = '█' * filled + '░' * empty
        return f"[{bar}] {progress:.1f}%"

# Global instance
multi_step_shortcode = MultiStepManagementShortcode() 