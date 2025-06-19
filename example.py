#!/usr/bin/env python3
"""
Example usage of the Stack Overflow Survey Analyzer Library

This script demonstrates how to use the main features of the analyzer.
"""

from so_survey_analyzer import StackOverflowSurveyAnalyzer


def main():
    """Main function demonstrating library usage."""
    print("Stack Overflow Survey Analyzer - Example Usage")
    print("=" * 60)
    
    # Initialize the analyzer
    print("1. Initializing analyzer...")
    try:
        analyzer = StackOverflowSurveyAnalyzer('raw_data.csv', 'schema.csv')
        print(f"   ✓ Loaded {len(analyzer.data):,} survey responses")
        print(f"   ✓ Loaded {len(analyzer.schema)} questions")
    except FileNotFoundError:
        print("   ✗ Data files not found. Please ensure raw_data.csv and schema.csv exist.")
        print("   If you have data.zip, extract it first: unzip data.zip")
        return
    except Exception as e:
        print(f"   ✗ Error loading data: {e}")
        return
    
    print("\n2. Getting summary statistics...")
    stats = analyzer.get_summary_stats()
    print(f"   • Total responses: {stats['total_responses']:,}")
    print(f"   • Total questions: {stats['total_questions']}")
    print(f"   • Single choice questions: {stats['question_types']['single_choice']}")
    print(f"   • Multiple choice questions: {stats['question_types']['multiple_choice']}")
    print(f"   • Text entry questions: {stats['question_types']['text_entry']}")
    print(f"   • Memory usage: {stats['memory_usage_mb']:.1f} MB")
    
    print("\n3. Searching for AI-related questions...")
    ai_questions = analyzer.search_questions('AI')
    print(f"   Found {len(ai_questions)} AI-related questions:")
    for i, question in enumerate(ai_questions[:3], 1):  # Show first 3
        print(f"   {i}. {question['column']} ({question['type']})")
        print(f"      {question['question_text'][:80]}...")
    
    print("\n4. Analyzing developer types...")
    analyzer.display_distribution('MainBranch', limit=5)
    
    print("\n5. Creating subset: Professional developers only...")
    developers = analyzer.create_subset('MainBranch', 'I am a developer by profession')
    print(f"   Created subset with {len(developers):,} professional developers")
    
    print("\n6. Analyzing programming languages among developers...")
    analyzer.display_distribution('LanguageHaveWorkedWith', data=developers, limit=10)
    
    print("\n7. Analyzing AI tool usage...")
    analyzer.display_distribution('AISelect')
    
    print("\n8. Comparing remote work preferences...")
    remote_workers = analyzer.create_subset('RemoteWork', 'Remote')
    print(f"   Remote workers: {len(remote_workers):,}")
    
    hybrid_workers = analyzer.create_subset('RemoteWork', 'Hybrid (some remote, some in-person)')
    print(f"   Hybrid workers: {len(hybrid_workers):,}")
    
    inperson_workers = analyzer.create_subset('RemoteWork', 'In-person')
    print(f"   In-person workers: {len(inperson_workers):,}")
    
    print("\n9. Example: Complex analysis pipeline...")
    # Find developers who use AI tools and work remotely
    ai_users = analyzer.create_subset('AISelect', 'Yes')
    remote_ai_users = analyzer.create_subset('RemoteWork', 'Remote', data=ai_users)
    
    print(f"   Developers using AI tools: {len(ai_users):,}")
    print(f"   Remote developers using AI tools: {len(remote_ai_users):,}")
    
    if len(remote_ai_users) > 0:
        print("\n   Top programming languages among remote AI-using developers:")
        analyzer.display_distribution('LanguageHaveWorkedWith', data=remote_ai_users, limit=5)
    
    print("\n" + "=" * 60)
    print("Example completed! Try the interactive mode:")
    print("python so_survey_analyzer.py raw_data.csv schema.csv")
    print("\nOr use the library programmatically:")
    print("from so_survey_analyzer import StackOverflowSurveyAnalyzer")
    print("analyzer = StackOverflowSurveyAnalyzer('raw_data.csv', 'schema.csv')")
    print("analyzer.interactive_mode()")


if __name__ == "__main__":
    main()
