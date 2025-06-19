"""
Stack Overflow Survey Data Analysis Library

This module provides functionality to analyze Stack Overflow Developer Survey data,
including displaying survey structure, searching questions, creating respondent subsets,
and analyzing answer distributions.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
import re
from collections import Counter


class StackOverflowSurveyAnalyzer:
    """
    A comprehensive analyzer for Stack Overflow Developer Survey data.
    
    This class provides methods to load, analyze, and interact with survey data,
    supporting both single-choice and multiple-choice questions.
    """
    
    def __init__(self, data_file: str, schema_file: str):
        """
        Initialize the analyzer with survey data and schema.
        
        Args:
            data_file (str): Path to the CSV file containing survey responses
            schema_file (str): Path to the CSV file containing question schema
        """
        self.data_file = data_file
        self.schema_file = schema_file
        self.data = None
        self.schema = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load survey data and schema from CSV files."""
        try:
            print("Loading survey data...")
            self.data = pd.read_csv(self.data_file, low_memory=False)
            self.schema = pd.read_csv(self.schema_file)
            
            # Create schema lookup dictionary
            self.schema_dict = self.schema.set_index('column').to_dict('index')
            
            print(f"Successfully loaded {len(self.data)} survey responses")
            print(f"Schema contains {len(self.schema)} questions")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not find required files: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading data: {e}")
    
    def display_survey_structure(self, question_type: Optional[str] = None) -> None:
        """
        Display the survey structure (list of questions) to CLI.
        
        Args:
            question_type (str, optional): Filter by question type ('SC', 'MC', 'TE')
        """
        if question_type:
            filtered_schema = self.schema[self.schema['type'] == question_type]
            print(f"\n=== Survey Questions ({question_type}) ===")
        else:
            filtered_schema = self.schema
            print("\n=== All Survey Questions ===")
        
        for _, row in filtered_schema.iterrows():
            print(f"\nColumn: {row['column']}")
            print(f"Type: {row['type']}")
            print(f"Question: {row['question_text']}")
            print("-" * 80)
        
        print(f"\nTotal questions: {len(filtered_schema)}")
    
    def search_questions(self, search_term: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Search for questions containing a specific term.
        
        Args:
            search_term (str): Term to search for in question text
            case_sensitive (bool): Whether search should be case-sensitive
            
        Returns:
            List[Dict]: List of matching questions with column, question_text, and type
        """
        if not case_sensitive:
            search_term = search_term.lower()
            search_column = self.schema['question_text'].str.lower()
        else:
            search_column = self.schema['question_text']
        
        # Escape special regex characters to treat search term as literal string
        escaped_search_term = re.escape(search_term)
        matches = self.schema[search_column.str.contains(escaped_search_term, na=False, regex=True)]
        
        results = []
        for _, row in matches.iterrows():
            results.append({
                'column': row['column'],
                'question_text': row['question_text'],
                'type': row['type']
            })
        
        return results
    
    def get_questions_by_type(self, question_type: str) -> List[Dict]:
        """
        Get all questions of a specific type.
        
        Args:
            question_type (str): Question type ('SC', 'MC', 'TE')
            
        Returns:
            List[Dict]: List of questions of the specified type
        """
        filtered_schema = self.schema[self.schema['type'] == question_type]
        
        results = []
        for _, row in filtered_schema.iterrows():
            results.append({
                'column': row['column'],
                'question_text': row['question_text'],
                'type': row['type']
            })
        
        return results
    
    def create_subset(self, column: str, value: str, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Create a subset of respondents based on question and option criteria.
        
        Args:
            column (str): Column name to filter on
            value (str): Value to filter for
            data (pd.DataFrame, optional): Data to filter (defaults to main dataset)
            
        Returns:
            pd.DataFrame: Filtered subset of respondents
        """
        if data is None:
            data = self.data
        
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in data")
        
        # Get question type
        question_type = self.schema_dict.get(column, {}).get('type', 'Unknown')
        
        if question_type == 'MC':  # Multiple Choice
            # For MC questions, check if value is in the semicolon-separated list
            mask = data[column].str.contains(re.escape(value), na=False)
            subset = data[mask]
        else:  # Single Choice or Text Entry
            subset = data[data[column] == value]
        
        print(f"Created subset with {len(subset)} respondents (filtered by {column} = '{value}')")
        return subset
    
    def get_unique_values(self, column: str, data: Optional[pd.DataFrame] = None) -> List[str]:
        """
        Get unique values for a column, handling both SC and MC questions.
        
        Args:
            column (str): Column name
            data (pd.DataFrame, optional): Data to analyze (defaults to main dataset)
            
        Returns:
            List[str]: List of unique values
        """
        if data is None:
            data = self.data
        
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in data")
        
        question_type = self.schema_dict.get(column, {}).get('type', 'Unknown')
        
        if question_type == 'MC':  # Multiple Choice
            # Split semicolon-separated values and flatten
            all_values = []
            for value_string in data[column].dropna():
                if pd.isna(value_string) or value_string == '':
                    continue
                values = [v.strip() for v in str(value_string).split(';')]
                all_values.extend(values)
            return sorted(list(set(all_values)))
        else:  # Single Choice or Text Entry
            return sorted(data[column].dropna().unique().tolist())
    
    def get_distribution(self, column: str, data: Optional[pd.DataFrame] = None, 
                        limit: int = 20) -> Dict[str, Any]:
        """
        Get answer distribution for a column.
        
        Args:
            column (str): Column name to analyze
            data (pd.DataFrame, optional): Data to analyze (defaults to main dataset)
            limit (int): Maximum number of options to return (for MC questions)
            
        Returns:
            Dict: Distribution data with counts, percentages, and metadata
        """
        if data is None:
            data = self.data
        
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in data")
        
        question_info = self.schema_dict.get(column, {})
        question_type = question_info.get('type', 'Unknown')
        question_text = question_info.get('question_text', column)
        
        total_responses = len(data)
        valid_responses = data[column].notna().sum()
        
        if question_type == 'MC':  # Multiple Choice
            # Count all individual choices
            all_choices = []
            for value_string in data[column].dropna():
                if pd.isna(value_string) or value_string == '':
                    continue
                choices = [v.strip() for v in str(value_string).split(';')]
                all_choices.extend(choices)
            
            choice_counts = Counter(all_choices)
            
            # Calculate percentages based on valid responses
            distribution = {}
            for choice, count in choice_counts.most_common(limit):
                percentage = (count / valid_responses) * 100
                distribution[choice] = {
                    'count': count,
                    'percentage': percentage
                }
        
        else:  # Single Choice or Text Entry
            value_counts = data[column].value_counts()
            
            distribution = {}
            for value, count in value_counts.head(limit).items():
                percentage = (count / total_responses) * 100
                distribution[str(value)] = {
                    'count': count,
                    'percentage': percentage
                }
        
        return {
            'column': column,
            'question_text': question_text,
            'question_type': question_type,
            'total_responses': total_responses,
            'valid_responses': valid_responses,
            'distribution': distribution
        }
    
    def display_distribution(self, column: str, data: Optional[pd.DataFrame] = None, 
                           limit: int = 20) -> None:
        """
        Display answer distribution for a column to CLI.
        
        Args:
            column (str): Column name to analyze
            data (pd.DataFrame, optional): Data to analyze (defaults to main dataset)
            limit (int): Maximum number of options to display
        """
        dist_data = self.get_distribution(column, data, limit)
        
        print("\n=== Distribution Analysis ===")
        print(f"Column: {dist_data['column']}")
        print(f"Question: {dist_data['question_text']}")
        print(f"Type: {dist_data['question_type']}")
        print(f"Total Responses: {dist_data['total_responses']:,}")
        print(f"Valid Responses: {dist_data['valid_responses']:,}")
        print(f"Response Rate: {(dist_data['valid_responses'] / dist_data['total_responses']) * 100:.1f}%")
        print("\nDistribution:")
        print("-" * 80)
        
        for option, stats in dist_data['distribution'].items():
            # Create a simple bar visualization
            bar_length = int(stats['percentage'] / 2)  # Scale down for display
            bar = "█" * bar_length
            
            print(f"{option:<40} {stats['count']:>8,} ({stats['percentage']:>5.1f}%) {bar}")
        
        print("-" * 80)
    
    def _handle_search_command(self) -> None:
        """Handle the search questions command."""
        search_term = input("Enter search term: ").strip()
        if search_term:
            results = self.search_questions(search_term)
            if results:
                print(f"\nFound {len(results)} matching questions:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['column']} ({result['type']})")
                    print(f"   {result['question_text']}")
            else:
                print("No matching questions found.")
    
    def _handle_distribution_command(self, current_data: pd.DataFrame) -> None:
        """Handle the distribution analysis command."""
        column = input("Enter column name to analyze: ").strip()
        if column in current_data.columns:
            limit = input("Maximum options to show (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            self.display_distribution(column, current_data, limit)
        else:
            print(f"Column '{column}' not found.")
            print("Available columns:", list(current_data.columns)[:10], "...")
    
    def _handle_subset_command(self, current_data: pd.DataFrame) -> tuple[pd.DataFrame, str]:
        """Handle the create subset command."""
        column = input("Enter column name to filter on: ").strip()
        if column in current_data.columns:
            # Show available values
            unique_values = self.get_unique_values(column, current_data)
            print(f"\nAvailable values for '{column}' (showing first 10):")
            for i, value in enumerate(unique_values[:10], 1):
                print(f"  {i}. {value}")
            if len(unique_values) > 10:
                print(f"  ... and {len(unique_values) - 10} more")
            
            value = input("\nEnter value to filter for: ").strip()
            if value:
                try:
                    subset = self.create_subset(column, value, current_data)
                    use_subset = input("Use this subset for further analysis? (y/n): ").strip().lower()
                    if use_subset == 'y':
                        return subset, f"Filtered by {column}='{value}'"
                except Exception as e:
                    print(f"Error creating subset: {e}")
        else:
            print(f"Column '{column}' not found.")
        
        return current_data, "No changes"

    def _execute_command(self, command: str, current_data: pd.DataFrame, current_subset_name: str) -> tuple[pd.DataFrame, str]:
        """Execute a command and return updated data and subset name."""
        if command in ['quit', 'exit', 'q']:
            return current_data, "QUIT"
        
        elif command == 'help':
            self._show_help()
        
        elif command == '1':
            question_type = input("Filter by type (SC/MC/TE) or press Enter for all: ").strip().upper()
            if question_type and question_type in ['SC', 'MC', 'TE']:
                self.display_survey_structure(question_type)
            else:
                self.display_survey_structure()
        
        elif command == '2':
            self._handle_search_command()
        
        elif command == '3':
            self._show_question_types()
        
        elif command == '4':
            self._handle_distribution_command(current_data)
        
        elif command == '5':
            new_data, subset_name = self._handle_subset_command(current_data)
            if subset_name != "No changes":
                return new_data, subset_name
        
        elif command == '6':
            self._show_data_info(current_data)
        
        else:
            print("Invalid command. Type 'help' for available commands.")
        
        return current_data, current_subset_name

    def interactive_mode(self) -> None:
        """Start an interactive CLI session for data exploration."""
        self._show_interactive_header()
        
        current_data = self.data
        current_subset_name = "Full Dataset"
        
        while True:
            print(f"\nCurrent dataset: {current_subset_name} ({len(current_data):,} responses)")
            command = input("\nEnter command: ").strip().lower()
            
            try:
                current_data, current_subset_name = self._execute_command(command, current_data, current_subset_name)
                
                if current_subset_name == "QUIT":
                    print("Goodbye!")
                    break
            
            except KeyboardInterrupt:
                print("\nOperation interrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_interactive_header(self) -> None:
        """Show the interactive mode header."""
        print("\n" + "="*80)
        print("Stack Overflow Survey Data Analyzer - Interactive Mode")
        print("="*80)
        print("Commands:")
        print("  1 - Display survey structure")
        print("  2 - Search questions")
        print("  3 - View question types")
        print("  4 - Analyze distribution")
        print("  5 - Create subset")
        print("  6 - Show data info")
        print("  help - Show this help")
        print("  quit - Exit interactive mode")
        print("="*80)
    
    def _show_help(self) -> None:
        """Show help text."""
        print("\nCommands:")
        print("  1 - Display survey structure")
        print("  2 - Search questions")
        print("  3 - View question types")
        print("  4 - Analyze distribution")
        print("  5 - Create subset")
        print("  6 - Show data info")
        print("  help - Show this help")
        print("  quit - Exit interactive mode")
    
    def _show_question_types(self) -> None:
        """Show question type statistics."""
        sc_count = len(self.get_questions_by_type('SC'))
        mc_count = len(self.get_questions_by_type('MC'))
        te_count = len(self.get_questions_by_type('TE'))
        
        print("\nQuestion Types:")
        print(f"  Single Choice (SC): {sc_count}")
        print(f"  Multiple Choice (MC): {mc_count}")
        print(f"  Text Entry (TE): {te_count}")
        print(f"  Total: {sc_count + mc_count + te_count}")
    
    def _show_data_info(self, data: pd.DataFrame) -> None:
        """Show dataset information."""
        print("\nDataset Info:")
        print(f"  Shape: {data.shape}")
        print(f"  Columns: {len(data.columns)}")
        print(f"  Memory usage: {data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        print(f"  Missing values: {data.isnull().sum().sum():,}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics about the dataset.
        
        Returns:
            Dict: Summary statistics including response counts, question types, etc.
        """
        sc_questions = len(self.get_questions_by_type('SC'))
        mc_questions = len(self.get_questions_by_type('MC'))
        te_questions = len(self.get_questions_by_type('TE'))
        
        return {
            'total_responses': len(self.data),
            'total_questions': len(self.schema),
            'question_types': {
                'single_choice': sc_questions,
                'multiple_choice': mc_questions,
                'text_entry': te_questions
            },
            'data_shape': self.data.shape,
            'missing_values': self.data.isnull().sum().sum(),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024**2
        }


def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python so_survey_analyzer.py <data_file> <schema_file>")
        sys.exit(1)
    
    data_file, schema_file = sys.argv[1], sys.argv[2]
    
    try:
        analyzer = StackOverflowSurveyAnalyzer(data_file, schema_file)
        analyzer.interactive_mode()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
