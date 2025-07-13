#!/usr/bin/env python3
"""
Test script untuk Multi-Step Processing System
"""

import asyncio
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from syncara.modules.multi_step_processor import multi_step_processor, StepStatus, WorkflowStatus
from syncara.console import console

async def test_basic_workflow():
    """Test basic workflow creation and execution"""
    console.info("🧪 Testing basic workflow...")
    
    # Create workflow
    workflow_id = multi_step_processor.create_workflow(
        name="Test Basic Workflow",
        description="Simple test workflow with log and delay steps"
    )
    
    # Add steps
    step1_id = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Log Start",
        handler="log",
        params={"message": "Workflow started!", "level": "info"}
    )
    
    step2_id = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Wait 2 seconds",
        handler="delay",
        params={"seconds": 2},
        dependencies=[step1_id]
    )
    
    step3_id = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Log End",
        handler="log",
        params={"message": "Workflow completed!", "level": "info"},
        dependencies=[step2_id]
    )
    
    # Execute workflow
    execution_id = await multi_step_processor.execute_workflow(
        workflow_id=workflow_id,
        context={"test": "basic_workflow"}
    )
    
    # Wait for completion
    await asyncio.sleep(5)
    
    # Check status
    execution = multi_step_processor.get_execution(execution_id)
    progress = multi_step_processor.get_execution_progress(execution_id)
    
    console.info(f"✅ Basic workflow test completed")
    console.info(f"Status: {execution.status.value}")
    console.info(f"Progress: {progress['progress']:.1f}%")
    
    return execution_id

async def test_parallel_workflow():
    """Test parallel step execution"""
    console.info("🧪 Testing parallel workflow...")
    
    # Create workflow with parallel steps
    workflow_id = multi_step_processor.create_workflow(
        name="Test Parallel Workflow",
        description="Workflow with parallel steps",
        max_parallel_steps=3
    )
    
    # Add initial step
    init_step = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Initialize",
        handler="log",
        params={"message": "Starting parallel tasks..."}
    )
    
    # Add parallel steps
    parallel_steps = []
    for i in range(3):
        step_id = multi_step_processor.add_step(
            workflow_id=workflow_id,
            name=f"Parallel Task {i+1}",
            handler="delay",
            params={"seconds": 1},
            dependencies=[init_step]
        )
        parallel_steps.append(step_id)
    
    # Add final step
    final_step = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Finalize",
        handler="log",
        params={"message": "All parallel tasks completed!"},
        dependencies=parallel_steps
    )
    
    # Execute
    execution_id = await multi_step_processor.execute_workflow(
        workflow_id=workflow_id,
        context={"test": "parallel_workflow"}
    )
    
    # Wait for completion
    await asyncio.sleep(5)
    
    # Check status
    execution = multi_step_processor.get_execution(execution_id)
    progress = multi_step_processor.get_execution_progress(execution_id)
    
    console.info(f"✅ Parallel workflow test completed")
    console.info(f"Status: {execution.status.value}")
    console.info(f"Progress: {progress['progress']:.1f}%")
    
    return execution_id

async def test_context_workflow():
    """Test context sharing between steps"""
    console.info("🧪 Testing context workflow...")
    
    # Create workflow
    workflow_id = multi_step_processor.create_workflow(
        name="Test Context Workflow",
        description="Workflow that uses context sharing"
    )
    
    # Add steps that use context
    step1 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Set Context",
        handler="set_context",
        params={"key": "user_name", "value": "AERIS"}
    )
    
    step2 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Get Context",
        handler="get_context",
        params={"key": "user_name"},
        dependencies=[step1]
    )
    
    step3 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Log Context",
        handler="log",
        params={"message": "Context retrieved successfully"},
        dependencies=[step2]
    )
    
    # Execute
    execution_id = await multi_step_processor.execute_workflow(
        workflow_id=workflow_id,
        context={"initial": "context"}
    )
    
    # Wait for completion
    await asyncio.sleep(3)
    
    # Check status
    execution = multi_step_processor.get_execution(execution_id)
    progress = multi_step_processor.get_execution_progress(execution_id)
    
    console.info(f"✅ Context workflow test completed")
    console.info(f"Status: {execution.status.value}")
    console.info(f"Progress: {progress['progress']:.1f}%")
    console.info(f"Final context: {execution.context}")
    
    return execution_id

async def test_error_handling():
    """Test error handling and retry mechanism"""
    console.info("🧪 Testing error handling...")
    
    # Register custom error handler
    async def error_handler(step, execution):
        raise Exception("Intentional test error")
    
    multi_step_processor.register_handler("test_error", error_handler)
    
    # Create workflow with error
    workflow_id = multi_step_processor.create_workflow(
        name="Test Error Workflow",
        description="Workflow that tests error handling"
    )
    
    # Add steps
    step1 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Success Step",
        handler="log",
        params={"message": "This should succeed"}
    )
    
    step2 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Error Step",
        handler="test_error",
        params={},
        dependencies=[step1],
        retry_count=2,
        retry_delay=1
    )
    
    # Execute
    execution_id = await multi_step_processor.execute_workflow(
        workflow_id=workflow_id
    )
    
    # Wait for completion
    await asyncio.sleep(5)
    
    # Check status
    execution = multi_step_processor.get_execution(execution_id)
    progress = multi_step_processor.get_execution_progress(execution_id)
    
    console.info(f"✅ Error handling test completed")
    console.info(f"Status: {execution.status.value}")
    console.info(f"Progress: {progress['progress']:.1f}%")
    
    return execution_id

async def test_conditional_workflow():
    """Test conditional step execution"""
    console.info("🧪 Testing conditional workflow...")
    
    # Create workflow
    workflow_id = multi_step_processor.create_workflow(
        name="Test Conditional Workflow",
        description="Workflow with conditional steps"
    )
    
    # Set context
    step1 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Set Flag",
        handler="set_context",
        params={"key": "should_run", "value": True}
    )
    
    # Conditional step
    step2 = multi_step_processor.add_step(
        workflow_id=workflow_id,
        name="Conditional Step",
        handler="log",
        params={"message": "This step runs conditionally"},
        dependencies=[step1],
        condition="context.get('should_run') == True"
    )
    
    # Execute
    execution_id = await multi_step_processor.execute_workflow(
        workflow_id=workflow_id
    )
    
    # Wait for completion
    await asyncio.sleep(3)
    
    # Check status
    execution = multi_step_processor.get_execution(execution_id)
    progress = multi_step_processor.get_execution_progress(execution_id)
    
    console.info(f"✅ Conditional workflow test completed")
    console.info(f"Status: {execution.status.value}")
    console.info(f"Progress: {progress['progress']:.1f}%")
    
    return execution_id

async def test_workflow_management():
    """Test workflow management functions"""
    console.info("🧪 Testing workflow management...")
    
    # List workflows
    workflows = multi_step_processor.list_workflows()
    console.info(f"Total workflows: {len(workflows)}")
    
    # List executions
    executions = multi_step_processor.list_executions()
    console.info(f"Total executions: {len(executions)}")
    
    # List running executions
    running = multi_step_processor.list_executions(WorkflowStatus.RUNNING)
    console.info(f"Running executions: {len(running)}")
    
    # List completed executions
    completed = multi_step_processor.list_executions(WorkflowStatus.COMPLETED)
    console.info(f"Completed executions: {len(completed)}")
    
    console.info("✅ Workflow management test completed")

async def main():
    """Main test function"""
    console.info("🚀 Starting Multi-Step Processing Tests...")
    
    try:
        # Run all tests
        await test_basic_workflow()
        await asyncio.sleep(1)
        
        await test_parallel_workflow()
        await asyncio.sleep(1)
        
        await test_context_workflow()
        await asyncio.sleep(1)
        
        await test_error_handling()
        await asyncio.sleep(1)
        
        await test_conditional_workflow()
        await asyncio.sleep(1)
        
        await test_workflow_management()
        
        console.info("🎉 All tests completed successfully!")
        
    except Exception as e:
        console.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 