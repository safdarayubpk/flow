#!/usr/bin/env python3
"""
Final comprehensive verification of Phase 9: Polish & Cross-Cutting Concerns
"""
import subprocess
import sys
import os

def run_test(description, test_cmd):
    """Helper to run a test and report results"""
    print(f"\n{description}")
    print("-" * len(description))

    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ PASSED")
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        print("❌ FAILED")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

    return result.returncode == 0

def main():
    print("🧪 Final Comprehensive Verification - Phase 9: Polish & Cross-Cutting Concerns")
    print("=" * 80)

    # Change to backend directory
    os.chdir('/home/safdarayub/Desktop/claude/Hackathon/flow/backend')

    # Activate virtual environment
    env = os.environ.copy()
    env['PATH'] = f'/home/safdarayub/Desktop/claude/Hackathon/flow/backend/venv/bin:{env["PATH"]}'

    all_passed = True

    # Test 1: CRUD Operations
    all_passed &= run_test(
        "T100: Verify all existing CRUD operations still work correctly",
        "cd backend && python3 -c 'from test_crud_simple import test_crud_operations; test_crud_operations()'"
    )

    # Test 2: User Isolation
    all_passed &= run_test(
        "T101: Test user isolation is maintained across all new features",
        "cd backend && python3 -c 'from test_user_isolation import test_user_isolation; test_user_isolation()'"
    )

    # Test 3: Backward Compatibility
    all_passed &= run_test(
        "T104: Test backward compatibility with old API calls",
        "cd backend && python3 -c 'from test_backward_compat import test_backward_compatibility; test_backward_compatibility()'"
    )

    # Test 4: Edge Cases
    all_passed &= run_test(
        "T106: Test edge cases (invalid tag names, past due dates, recurring tasks)",
        "cd backend && python3 -c 'from test_edge_cases import test_edge_cases; test_edge_cases()'"
    )

    # Test 5: API Endpoints Check
    all_passed &= run_test(
        "T108: Verify all API endpoints exist and are properly configured",
        "cd backend && python3 check_api_endpoints.py"
    )

    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)

    if all_passed:
        print("🎉 ALL PHASE 9 TASKS COMPLETED SUCCESSFULLY!")
        print("\nThe following tasks from Phase 9 have been verified:")
        print("✅ T100: CRUD operations work correctly")
        print("✅ T101: User isolation maintained")
        print("✅ T104: Backward compatibility verified")
        print("✅ T106: Edge cases handled properly")
        print("✅ T108: API endpoints properly configured")
        print("\nAll advanced todo features (priorities, tags, search/filter, sort,")
        print("recurring tasks, due dates & reminders) have been successfully implemented")
        print("and verified to work without breaking existing functionality.")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Phase 9 verification incomplete")
        return 1

if __name__ == "__main__":
    sys.exit(main())