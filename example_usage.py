#!/usr/bin/env python3
"""
Example usage of the Stack Overflow Survey Analyzer

This script demonstrates the main features of the library.
"""

from stackoverflow_analyzer import StackOverflowAnalyzer

def main():
    """Demonstrate library features."""
    print("=" * 80)
    print("STACK OVERFLOW SURVEY ANALYZER - EXAMPLE USAGE")
    print("=" * 80)
    
    # Initialize the analyzer
    print("\n1. Initializing analyzer...")
    analyzer = StackOverflowAnalyzer('schema.csv', 'raw_data.csv')
    
    # Show survey summary
    print("\n2. Survey Summary:")
    analyzer.display_summary()
    
    # Search for questions about programming languages
    print("\n3. Searching for 'language' questions:")
    language_questions = analyzer.search_questions('language')
    
    # Show survey structure for single choice questions
    print("\n4. Single Choice Questions:")
    analyzer.display_survey_structure('SC')
    
    # Get age distribution
    print("\n5. Age Distribution:")
    analyzer.display_distribution('Age')
    
    # Get programming language distribution (top 10)
    print("\n6. Top 10 Programming Languages:")
    analyzer.display_distribution('LanguageHaveWorkedWith', top_n=10)
    
    # Create subset of professional developers
    print("\n7. Creating subset of professional developers:")
    subset = analyzer.create_subset('MainBranch', 'I am a developer by profession')
    print(f"Subset contains {len(subset)} respondents")
    
    # Show unique options for employment status
    print("\n8. Employment Status Options:")
    employment_options = analyzer.get_unique_options('Employment')
    for i, option in enumerate(employment_options[:10], 1):  # Show first 10
        print(f"   {i}. {option}")
    if len(employment_options) > 10:
        print(f"   ... and {len(employment_options) - 10} more options")
    
    # Get question info
    print("\n9. Question Information:")
    info = analyzer.get_question_info('RemoteWork')
    if info:
        print(f"   Column: {info['column']}")
        print(f"   Type: {info['type']}")
        print(f"   Question: {info['question_text']}")
    
    print("\n" + "=" * 80)
    print("Example completed! Try the interactive CLI:")
    print("python -m stackoverflow_analyzer.cli schema.csv raw_data.csv")
    print("=" * 80)

if __name__ == "__main__":
    main()