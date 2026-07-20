import sys
import os
from dotenv import load_dotenv
from app.services.langgraph_agent import DocumentAnalysisAgent

load_dotenv()

print("="*60)
print("Testing DocumentAnalysisAgent with Ollama")
print("="*60)

sample_chunks = [
    """
    Employment Agreement
    
    This contract is between John Smith (Employee) and Acme Corporation (Employer).
    
    Position: Senior Developer
    Salary: \$150,000 per year
    Start Date: February 1, 2024
    
    Contact Information:
    Email: john@acme.com
    Phone: +1-555-0123
    Office: New York, NY
    """,
    
    """
    Employment Terms
    
    The employee agrees to work full-time at Acme Corporation's New York office.
    
    Benefits include:
    - Health insurance
    - 401k matching (6%)
    - Paid time off (20 days/year)
    - Professional development budget
    
    The employment is at-will and can be terminated by either party with 2 weeks notice.
    """,
    
    """
    Confidentiality and IP Rights
    
    All work created during employment is the property of Acme Corporation.
    The employee agrees not to disclose confidential information.
    
    Signed: John Smith ____________________
    Date: January 15, 2024
    
    Witnessed by: Jane Doe ____________________
    """,
]

try:
    print("\n[1/2] Initializing agent...")
    agent = DocumentAnalysisAgent()
    print("✅ Agent initialized")
    
    print("\n[2/2] Running analysis (30-60 seconds)...")
    state = agent.execute(
        document_id="test-employment-001",
        chunks=sample_chunks
    )
    
    # Print results
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📄 Document ID: {state.document_id}")
    
    print(f"\n📝 Summary:\n{state.summary}")
    
    print(f"\n🏷️  Topics: {', '.join(state.topics)}")
    
    print(f"\n👥 Entities:")
    for entity_type, values in state.entities.items():
        if values:
            print(f"   {entity_type}: {values}")
    
    print(f"\n⚠️  Compliance Flags:")
    if state.compliance_flags:
        for flag in state.compliance_flags:
            print(f"   [{flag.get('severity', 'unknown')}] {flag.get('type', 'Unknown')}")
            print(f"      → {flag.get('description', '')}")
    else:
        print("   ✅ No issues found")
    
    print(f"\n🔗 Knowledge Graph:")
    if state.knowledge_graph:
        for rel in state.knowledge_graph[:3]:
            print(f"   {rel.get('entity1', '?')} --{rel.get('relation', '?')}→ {rel.get('entity2', '?')}")
    else:
        print("   No relationships found")
    
    print(f"\n⏱️  Execution Times:")
    for node, exec_time in state.node_execution_times.items():
        print(f"   {node}: {exec_time:.2f}s")
    
    if state.errors:
        print(f"\n⚠️  Errors:")
        for error in state.errors:
            print(f"   - {error}")
    else:
        print(f"\n✅ No errors")
    
    print("\n" + "="*60)
    print("✅ TEST PASSED")
    print("="*60)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)