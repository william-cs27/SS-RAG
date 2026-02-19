"""
Command Line Interface for IPC Sunday School RAG
Simple terminal-based query interface
"""

import sys
from dotenv import load_dotenv
from query_engine import IPCRAGEngine


def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)


def print_header():
    """Print CLI header"""
    print_separator()
    print("📖 IPC SUNDAY SCHOOL STUDY ASSISTANT - CLI")
    print_separator()
    print()


def print_result(result):
    """Pretty print query result"""
    print_separator("-")
    print(f"Question: {result['question']}")
    print(f"Mode: {result['mode']}")
    print_separator("-")
    print("\nAnswer:")
    print(result['answer'])
    print()
    print_separator("-")
    print(f"Sources Retrieved: {len(result['sources'])}")
    
    for i, source in enumerate(result['sources'], 1):
        metadata = source['metadata']
        print(f"\nSource {i}:")
        print(f"  Curriculum: {metadata.get('curriculum', 'N/A')}")
        print(f"  Grade: {metadata.get('grade', 'N/A')}")
        print(f"  Lesson: {metadata.get('lesson_number', 'N/A')} - {metadata.get('lesson_title', 'N/A')}")
    
    print_separator()


def interactive_mode(engine):
    """Run interactive query mode"""
    print("\nInteractive Mode - Type 'quit' or 'exit' to stop")
    print("Commands:")
    print("  :mode <student|teacher|exam_prep|verse_lookup> - Change mode")
    print("  :grade <1-13> - Filter by grade")
    print("  :curriculum <IPC|Radiant Life|Christian Identity> - Filter by curriculum")
    print("  :clear - Clear all filters")
    print("  :help - Show this help")
    print()
    
    current_mode = 'student'
    current_filters = {}
    
    while True:
        try:
            # Prompt
            filter_str = ""
            if current_filters:
                filter_parts = [f"{k}={v}" for k, v in current_filters.items()]
                filter_str = f" [{', '.join(filter_parts)}]"
            
            question = input(f"\n[{current_mode}{filter_str}] > ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            # Handle commands
            if question.startswith(':'):
                cmd_parts = question[1:].split()
                cmd = cmd_parts[0].lower()
                
                if cmd == 'mode' and len(cmd_parts) > 1:
                    new_mode = cmd_parts[1]
                    if new_mode in ['student', 'teacher', 'exam_prep', 'verse_lookup']:
                        current_mode = new_mode
                        print(f"✓ Mode changed to: {current_mode}")
                    else:
                        print("✗ Invalid mode. Use: student, teacher, exam_prep, or verse_lookup")
                
                elif cmd == 'grade' and len(cmd_parts) > 1:
                    try:
                        grade = int(cmd_parts[1])
                        if 1 <= grade <= 13:
                            current_filters['grade'] = grade
                            print(f"✓ Filter set: grade={grade}")
                        else:
                            print("✗ Grade must be between 1 and 13")
                    except ValueError:
                        print("✗ Invalid grade number")
                
                elif cmd == 'curriculum' and len(cmd_parts) > 1:
                    curriculum = ' '.join(cmd_parts[1:])
                    if curriculum in ['IPC', 'Radiant Life', 'Christian Identity']:
                        current_filters['curriculum'] = curriculum
                        print(f"✓ Filter set: curriculum={curriculum}")
                    else:
                        print("✗ Invalid curriculum. Use: IPC, Radiant Life, or Christian Identity")
                
                elif cmd == 'clear':
                    current_filters = {}
                    print("✓ All filters cleared")
                
                elif cmd == 'help':
                    print("\nAvailable commands:")
                    print("  :mode <mode> - Change query mode")
                    print("  :grade <1-13> - Filter by grade")
                    print("  :curriculum <name> - Filter by curriculum")
                    print("  :clear - Clear filters")
                    print("  :help - Show this help")
                    print("  quit/exit - Exit program")
                
                else:
                    print("✗ Unknown command. Type :help for help")
                
                continue
            
            # Execute query
            print("\nSearching...")
            result = engine.query(
                question=question,
                mode=current_mode,
                filters=current_filters if current_filters else None,
                k=5
            )
            
            print_result(result)
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")


def quick_query_mode(engine, question, mode='student', grade=None, curriculum=None):
    """Run a single query and exit"""
    filters = {}
    if grade:
        filters['grade'] = int(grade)
    if curriculum:
        filters['curriculum'] = curriculum
    
    result = engine.query(
        question=question,
        mode=mode,
        filters=filters if filters else None,
        k=5
    )
    
    print_result(result)


def main():
    """Main CLI entry point"""
    load_dotenv()
    
    print_header()
    
    # Initialize engine
    try:
        print("Loading RAG engine...")
        engine = IPCRAGEngine()
        print("✓ Engine loaded successfully!\n")
    except Exception as e:
        print(f"✗ Error loading engine: {e}")
        print("\nMake sure you have:")
        print("  1. Run 'python indexer.py' to build the database")
        print("  2. Set up your .env file with API keys")
        return
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        # Quick query mode
        if '--help' in sys.argv or '-h' in sys.argv:
            print("Usage:")
            print("  python cli.py                          # Interactive mode")
            print("  python cli.py \"your question here\"     # Quick query")
            print("  python cli.py \"question\" --mode exam_prep")
            print("  python cli.py \"question\" --grade 5")
            print("  python cli.py \"question\" --curriculum IPC")
            print()
            print("Options:")
            print("  --mode <mode>           Query mode (student, teacher, exam_prep, verse_lookup)")
            print("  --grade <1-13>          Filter by grade")
            print("  --curriculum <name>     Filter by curriculum (IPC, Radiant Life, Christian Identity)")
            print("  --help, -h              Show this help")
            return
        
        question = sys.argv[1]
        mode = 'student'
        grade = None
        curriculum = None
        
        # Parse options
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--mode' and i + 1 < len(sys.argv):
                mode = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--grade' and i + 1 < len(sys.argv):
                grade = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--curriculum' and i + 1 < len(sys.argv):
                curriculum = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        quick_query_mode(engine, question, mode, grade, curriculum)
    else:
        # Interactive mode
        interactive_mode(engine)


if __name__ == "__main__":
    main()
