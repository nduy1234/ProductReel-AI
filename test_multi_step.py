"""Test script for multi-step problem handling."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.agent import GAIAAgent
from tasks.gaia_task import GAIATask


def test_multi_step_problems():
    """Test various multi-step problems."""
    
    agent = GAIAAgent(seed=42, max_retries=3)
    
    test_cases = [
        {
            "problem": "Calculate 15 multiplied by 7, then add 23.",
            "expected": "128",
            "description": "Multiplication then addition"
        },
        {
            "problem": "What is 20 divided by 4, then subtract 3?",
            "expected": "2",
            "description": "Division then subtraction"
        },
        {
            "problem": "Calculate 10 plus 5, then multiply by 2.",
            "expected": "30",
            "description": "Addition then multiplication"
        },
        {
            "problem": "First calculate 12 multiplied by 3, then add 14.",
            "expected": "50",
            "description": "First-then pattern"
        },
        {
            "problem": "What is 100 minus 37?",
            "expected": "63",
            "description": "Single step (baseline)"
        }
    ]
    
    print("="*70)
    print("MULTI-STEP PROBLEM TESTING")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Problem: {test['problem']}")
        print(f"Expected: {test['expected']}")
        
        result = agent.execute(test['problem'], task_id=f"test_{i}")
        answer = result['answer']
        
        print(f"Got: {answer}")
        print(f"Steps: {len(result['steps'])}")
        
        # Check if answer matches (allowing for string comparison)
        if str(answer).strip() == str(test['expected']).strip():
            print("[PASSED]")
            passed += 1
        else:
            print("[FAILED]")
            failed += 1
            print(f"  Expected: {test['expected']}, Got: {answer}")
        
        # Show steps
        for step in result['steps']:
            if step.get('success'):
                step_result = step.get('result', {})
                if isinstance(step_result, dict):
                    print(f"  Step {step['step_id']}: {step.get('expression', 'N/A')} = {step_result.get('result', 'N/A')}")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(test_cases):.1%}")
    print("="*70)
    
    return passed == len(test_cases)


if __name__ == '__main__':
    success = test_multi_step_problems()
    sys.exit(0 if success else 1)
