#!/usr/bin/env python3
"""
Quick test script to verify StudyBud setup
"""

import sys
import os

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit
        print(f"  ✓ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"  ✗ Streamlit: {e}")
        return False
    
    try:
        import chromadb
        print(f"  ✓ ChromaDB {chromadb.__version__}")
    except ImportError as e:
        print(f"  ✗ ChromaDB: {e}")
        return False
    
    try:
        import langchain
        print(f"  ✓ LangChain {langchain.__version__}")
    except ImportError as e:
        print(f"  ✗ LangChain: {e}")
        return False
    
    try:
        from langchain_anthropic import ChatAnthropic
        print(f"  ✓ LangChain Anthropic")
    except ImportError as e:
        print(f"  ✗ LangChain Anthropic: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print(f"  ✓ Sentence Transformers")
    except ImportError as e:
        print(f"  ✗ Sentence Transformers: {e}")
        return False
    
    return True


def test_services():
    """Test that custom services can be imported"""
    print("\nTesting custom services...")
    
    try:
        from services import agent_service
        print(f"  ✓ Agent service ({len(agent_service.TOOLS)} tools)")
    except ImportError as e:
        print(f"  ✗ Agent service: {e}")
        return False
    
    try:
        from services import vector_db_service
        print(f"  ✓ Vector DB service")
    except ImportError as e:
        print(f"  ✗ Vector DB service: {e}")
        return False
    
    try:
        from services import pdf_service
        print(f"  ✓ PDF service")
    except ImportError as e:
        print(f"  ✗ PDF service: {e}")
        return False
    
    try:
        from services import embedding_service
        print(f"  ✓ Embedding service")
    except ImportError as e:
        print(f"  ✗ Embedding service: {e}")
        return False
    
    return True


def test_ui():
    """Test that UI modules can be imported"""
    print("\nTesting UI modules...")
    
    try:
        from ui import chat_page
        print(f"  ✓ Chat page")
    except ImportError as e:
        print(f"  ✗ Chat page: {e}")
        return False
    
    try:
        from ui import documents_page
        print(f"  ✓ Documents page")
    except ImportError as e:
        print(f"  ✗ Documents page: {e}")
        return False
    
    return True


def test_api_key():
    """Check if API key is set"""
    print("\nChecking API key...")
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        print(f"  ✓ ANTHROPIC_API_KEY is set ({api_key[:10]}...)")
        return True
    else:
        print(f"  ⚠ ANTHROPIC_API_KEY not set")
        print("    Set it with: export ANTHROPIC_API_KEY=sk-ant-...")
        return False


def main():
    print("=" * 60)
    print("StudyBud Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Services", test_services()))
    results.append(("UI Modules", test_ui()))
    results.append(("API Key", test_api_key()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! StudyBud is ready to use.")
        print("\nNext steps:")
        print("  1. Set ANTHROPIC_API_KEY if not already set")
        print("  2. Run: streamlit run app.py")
        print("  3. Upload a PDF and start studying!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
