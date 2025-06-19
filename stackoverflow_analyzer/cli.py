"""
Command Line Interface for Stack Overflow Survey Analyzer

Provides an interactive CLI/REPL interface for exploring survey data.
"""

import sys
import os
from typing import Optional
from .analyzer import StackOverflowAnalyzer


class StackOverflowCLI:
    """Interactive CLI for Stack Overflow Survey Analysis."""
    
    def __init__(self, schema_file: str, data_file: str):
        """
        Initialize the CLI with an analyzer instance.
        
        Args:
            schema_file: Path to schema CSV file
            data_file: Path to raw data CSV file
        """
        try:
            self.analyzer = StackOverflowAnalyzer(schema_file, data_file)
            self.running = True
        except Exception as e:
            print(f"Error initializing analyzer: {e}")
            sys.exit(1)
    
    def display_help(self):
        """Display available commands."""
        help_text = """
================================================================================
STACK OVERFLOW SURVEY ANALYZER - COMMANDS
================================================================================

Data Exploration:
  summary                    - Show survey summary statistics
  structure [type]           - Show survey structure (optional: SC, MC, TE)
  
Search & Discovery:
  search <term>              - Search questions by term
  info <column>              - Get information about a specific question
  options <column>           - List unique options for a question
  
Analysis:
  dist <column> [n]          - Show answer distribution (optional: top n)
  subset <column> <value>    - Create respondent subset
  
Utility:
  help                       - Show this help message
  quit/exit                  - Exit the program
  
Examples:
  structure SC               - Show only Single Choice questions
  search language            - Find questions containing 'language'
  dist Age 5                - Show top 5 age distributions
  subset MainBranch "I am a developer by profession"
  
================================================================================
        """
        print(help_text)
    
    def process_command(self, command: str) -> bool:
        """
        Process a single command.
        
        Args:
            command: The command string to process
            
        Returns:
            True to continue, False to exit
        """
        parts = command.strip().split()
        
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        try:
            if cmd in ['quit', 'exit', 'q']:
                print("Goodbye!")
                return False
            
            elif cmd in ['help', 'h', '?']:
                self.display_help()
            
            elif cmd == 'summary':
                self.analyzer.display_summary()
            
            elif cmd == 'structure':
                question_type = args[0] if args else None
                self.analyzer.display_survey_structure(question_type)
            
            elif cmd == 'search':
                if not args:
                    print("Usage: search <term>")
                else:
                    search_term = ' '.join(args)
                    self.analyzer.search_questions(search_term)
            
            elif cmd == 'info':
                if not args:
                    print("Usage: info <column_name>")
                else:
                    column_name = args[0]
                    info = self.analyzer.get_question_info(column_name)
                    if info:
                        print(f"\nQuestion: {info['column']} ({info['type']})")
                        print(f"Text: {info['question_text']}")
                    else:
                        print(f"Question '{column_name}' not found.")
            
            elif cmd == 'options':
                if not args:
                    print("Usage: options <column_name>")
                else:
                    column_name = args[0]
                    try:
                        options = self.analyzer.get_unique_options(column_name)
                        print(f"\nUnique options for '{column_name}' ({len(options)} total):")
                        for i, option in enumerate(options, 1):
                            print(f"{i:3d}. {option}")
                    except Exception as e:
                        print(f"Error getting options: {e}")
            
            elif cmd in ['dist', 'distribution']:
                if not args:
                    print("Usage: dist <column_name> [top_n]")
                else:
                    column_name = args[0]
                    top_n = None
                    if len(args) > 1:
                        try:
                            top_n = int(args[1])
                        except ValueError:
                            print("Warning: Invalid number for top_n, showing all results")
                    
                    self.analyzer.display_distribution(column_name, top_n)
            
            elif cmd == 'subset':
                if len(args) < 2:
                    print("Usage: subset <column_name> <value>")
                    print("Note: Use quotes for values with spaces")
                else:
                    column_name = args[0]
                    # Join remaining args as the value (handles quoted strings)
                    value = ' '.join(args[1:]).strip('"\'')
                    subset = self.analyzer.create_subset(column_name, value)
                    print(f"Subset created with {len(subset)} respondents")
            
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")
        
        except Exception as e:
            print(f"Error executing command: {e}")
        
        return True
    
    def run(self):
        """Run the interactive CLI."""
        print("=" * 80)
        print("STACK OVERFLOW SURVEY ANALYZER")
        print("=" * 80)
        print("Type 'help' for available commands, 'quit' to exit")
        
        while self.running:
            try:
                command = input("\nso-analyzer> ").strip()
                if not self.process_command(command):
                    break
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit properly.")
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    """Main entry point for CLI."""
    if len(sys.argv) != 3:
        print("Usage: python -m stackoverflow_analyzer.cli <schema_file> <data_file>")
        print("Example: python -m stackoverflow_analyzer.cli schema.csv raw_data.csv")
        sys.exit(1)
    
    schema_file = sys.argv[1]
    data_file = sys.argv[2]
    
    # Check if files exist
    if not os.path.exists(schema_file):
        print(f"Error: Schema file '{schema_file}' not found")
        sys.exit(1)
    
    if not os.path.exists(data_file):
        print(f"Error: Data file '{data_file}' not found")
        sys.exit(1)
    
    cli = StackOverflowCLI(schema_file, data_file)
    cli.run()


if __name__ == "__main__":
    main()