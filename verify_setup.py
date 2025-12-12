#!/usr/bin/env python3
"""
Setup Verification Script

This script verifies that the Workflow Engine is properly set up and ready to use.
Run this before starting development or after installation.
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message"""
    print(f"✓ {text}")


def print_error(text):
    """Print error message"""
    print(f"✗ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version_str} (>= 3.9 required)")
        return True
    else:
        print_error(f"Python {version_str} (>= 3.9 required)")
        print("  Please upgrade Python to 3.9 or higher")
        return False


def check_project_structure():
    """Check if all required files exist"""
    print_header("Checking Project Structure")
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/engine.py",
        "app/models.py",
        "app/tools.py",
        "app/database.py",
        "app/workflows/__init__.py",
        "app/workflows/code_review.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - MISSING")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("sqlalchemy", "SQLAlchemy"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print_success(f"{name}")
        except ImportError:
            print_error(f"{name} - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\n  Install dependencies with:")
        print("  pip install -r requirements.txt")
    
    return all_installed


def check_imports():
    """Check if app modules can be imported"""
    print_header("Checking Module Imports")
    
    modules = [
        ("app.main", "FastAPI Application"),
        ("app.engine", "Workflow Engine"),
        ("app.models", "Data Models"),
        ("app.tools", "Tool Registry"),
        ("app.database", "Database Layer"),
        ("app.workflows.code_review", "Code Review Workflow"),
    ]
    
    all_imported = True
    for module, name in modules:
        try:
            __import__(module)
            print_success(f"{name}")
        except Exception as e:
            print_error(f"{name} - {str(e)}")
            all_imported = False
    
    return all_imported


def check_database():
    """Check database setup"""
    print_header("Checking Database")
    
    try:
        from app.database import engine, Base
        
        # Try to create tables
        Base.metadata.create_all(bind=engine)
        print_success("Database tables created successfully")
        
        # Check if database file exists
        if Path("workflow_engine.db").exists():
            print_success("Database file exists")
        else:
            print_warning("Database file will be created on first run")
        
        return True
    except Exception as e:
        print_error(f"Database setup failed: {str(e)}")
        return False


def check_tools():
    """Check if tools are registered"""
    print_header("Checking Tool Registry")
    
    try:
        from app.tools import tool_registry
        
        tools = tool_registry.list_tools()
        
        if len(tools) > 0:
            print_success(f"Found {len(tools)} registered tools:")
            for tool in tools:
                print(f"  - {tool}")
            return True
        else:
            print_error("No tools registered")
            return False
    except Exception as e:
        print_error(f"Tool registry check failed: {str(e)}")
        return False


def check_example_workflow():
    """Check if example workflow is valid"""
    print_header("Checking Example Workflow")
    
    try:
        from app.workflows.code_review import (
            get_code_review_graph_definition,
            get_sample_initial_state
        )
        
        graph_def = get_code_review_graph_definition()
        initial_state = get_sample_initial_state()
        
        print_success("Code review workflow definition loaded")
        print_success(f"  Nodes: {len(graph_def['nodes'])}")
        print_success(f"  Start node: {graph_def['start_node']}")
        print_success(f"  Initial state keys: {list(initial_state.keys())}")
        
        return True
    except Exception as e:
        print_error(f"Example workflow check failed: {str(e)}")
        return False


def check_documentation():
    """Check if documentation files exist"""
    print_header("Checking Documentation")
    
    doc_files = [
        ("README.md", "Main documentation"),
        ("QUICKSTART.md", "Quick start guide"),
        ("API_REFERENCE.md", "API reference"),
        ("ARCHITECTURE.md", "Architecture docs"),
        ("PROJECT_SUMMARY.md", "Project summary"),
    ]
    
    all_exist = True
    for file_path, description in doc_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print_success(f"{description} ({size:,} bytes)")
        else:
            print_warning(f"{description} - MISSING")
            all_exist = False
    
    return all_exist


def print_next_steps():
    """Print next steps"""
    print_header("Next Steps")
    
    print("\n1. Start the server:")
    print("   uvicorn app.main:app --reload")
    
    print("\n2. Open API documentation:")
    print("   http://localhost:8000/docs")
    
    print("\n3. Run the example:")
    print("   python example_usage.py")
    
    print("\n4. Run tests:")
    print("   python test_api.py")
    
    print("\n5. Read the documentation:")
    print("   - README.md - Overview and features")
    print("   - QUICKSTART.md - Get started quickly")
    print("   - API_REFERENCE.md - Complete API docs")
    print("   - ARCHITECTURE.md - System design")


def main():
    """Main verification flow"""
    print("\n" + "=" * 60)
    print("  Workflow Engine - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Module Imports", check_imports),
        ("Database", check_database),
        ("Tool Registry", check_tools),
        ("Example Workflow", check_example_workflow),
        ("Documentation", check_documentation),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Unexpected error in {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup is ready.")
        print_next_steps()
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
