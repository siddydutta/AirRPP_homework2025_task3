"""
Stack Overflow Survey Data Analyzer

Main analyzer class for processing Stack Overflow survey data.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
import re
from collections import Counter


class StackOverflowAnalyzer:
    """
    Main class for analyzing Stack Overflow survey data.
    
    Provides functionality to:
    - Load and explore survey structure
    - Search for questions and options
    - Create respondent subsets
    - Analyze answer distributions for SC and MC questions
    """
    
    def __init__(self, schema_file: str, data_file: str):
        """
        Initialize the analyzer with schema and data files.
        
        Args:
            schema_file: Path to the schema CSV file
            data_file: Path to the raw data CSV file
        """
        self.schema_file = schema_file
        self.data_file = data_file
        self._schema = None
        self._data = None
        self._load_schema()
    
    def _load_schema(self):
        """Load the schema file."""
        try:
            self._schema = pd.read_csv(self.schema_file)
            print(f"Loaded schema with {len(self._schema)} questions")
        except Exception as e:
            raise ValueError(f"Error loading schema file: {e}")
    
    def _load_data(self):
        """Load the data file only when needed (lazy loading)."""
        if self._data is None:
            try:
                self._data = pd.read_csv(self.data_file)
                print(f"Loaded data with {len(self._data)} respondents and {len(self._data.columns)} columns")
            except Exception as e:
                raise ValueError(f"Error loading data file: {e}")
    
    @property
    def schema(self) -> pd.DataFrame:
        """Get the survey schema."""
        return self._schema
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the survey data (loads if not already loaded)."""
        self._load_data()
        return self._data
    
    def display_survey_structure(self, question_type: Optional[str] = None) -> None:
        """
        Display the survey structure (list of questions).
        
        Args:
            question_type: Optional filter by question type ('SC', 'MC', 'TE')
        """
        schema = self._schema
        
        if question_type:
            schema = schema[schema['type'] == question_type.upper()]
        
        print(f"\n{'='*80}")
        print(f"SURVEY STRUCTURE {'(' + question_type + ' questions only)' if question_type else ''}")
        print(f"{'='*80}")
        
        for idx, row in schema.iterrows():
            print(f"\n{idx + 1}. {row['column']} ({row['type']})")
            print(f"   {row['question_text']}")
    
    def search_questions(self, search_term: str, case_sensitive: bool = False) -> pd.DataFrame:
        """
        Search for questions containing a specific term.
        
        Args:
            search_term: Term to search for in question text or column names
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            DataFrame with matching questions
        """
        if not case_sensitive:
            search_term = search_term.lower()
            column_matches = self._schema['column'].str.lower().str.contains(search_term, na=False)
            text_matches = self._schema['question_text'].str.lower().str.contains(search_term, na=False)
        else:
            column_matches = self._schema['column'].str.contains(search_term, na=False)
            text_matches = self._schema['question_text'].str.contains(search_term, na=False)
        
        matches = self._schema[column_matches | text_matches]
        
        if len(matches) > 0:
            print(f"\nFound {len(matches)} question(s) matching '{search_term}':")
            print("-" * 60)
            for idx, row in matches.iterrows():
                print(f"\n{row['column']} ({row['type']})")
                print(f"   {row['question_text']}")
        else:
            print(f"\nNo questions found matching '{search_term}'")
        
        return matches
    
    def get_question_info(self, column_name: str) -> Optional[Dict]:
        """
        Get information about a specific question.
        
        Args:
            column_name: The column name to get info for
            
        Returns:
            Dictionary with question information or None if not found
        """
        match = self._schema[self._schema['column'] == column_name]
        
        if len(match) == 0:
            return None
        
        row = match.iloc[0]
        return {
            'column': row['column'],
            'question_text': row['question_text'],
            'type': row['type']
        }
    
    def create_subset(self, column_name: str, option_value: str, exact_match: bool = True) -> pd.DataFrame:
        """
        Create a subset of respondents based on question and option.
        
        Args:
            column_name: The question column name
            option_value: The option value to filter by
            exact_match: Whether to require exact match or substring match
            
        Returns:
            DataFrame with filtered respondents
        """
        self._load_data()
        
        if column_name not in self._data.columns:
            raise ValueError(f"Column '{column_name}' not found in data")
        
        question_info = self.get_question_info(column_name)
        if not question_info:
            raise ValueError(f"Question '{column_name}' not found in schema")
        
        if question_info['type'] == 'MC':
            # For multiple choice, check if option is in the delimited list
            if exact_match:
                # Split by semicolon and check exact match
                mask = self._data[column_name].apply(
                    lambda x: option_value in str(x).split(';') if pd.notna(x) else False
                )
            else:
                # Substring match
                mask = self._data[column_name].str.contains(option_value, na=False, case=False)
        else:
            # For single choice, direct comparison
            if exact_match:
                mask = self._data[column_name] == option_value
            else:
                mask = self._data[column_name].str.contains(option_value, na=False, case=False)
        
        subset = self._data[mask]
        
        print(f"\nCreated subset with {len(subset)} respondents")
        print(f"Question: {question_info['question_text']}")
        print(f"Filter: {column_name} {'contains' if not exact_match else '='} '{option_value}'")
        
        return subset
    
    def get_answer_distribution(self, column_name: str, top_n: Optional[int] = None) -> Dict:
        """
        Get the distribution of answers for a question.
        
        Args:
            column_name: The question column name
            top_n: Optional limit to top N answers
            
        Returns:
            Dictionary with distribution data
        """
        self._load_data()
        
        if column_name not in self._data.columns:
            raise ValueError(f"Column '{column_name}' not found in data")
        
        question_info = self.get_question_info(column_name)
        if not question_info:
            raise ValueError(f"Question '{column_name}' not found in schema")
        
        result = {
            'question': question_info,
            'total_responses': len(self._data),
            'valid_responses': self._data[column_name].notna().sum(),
            'distribution': {},
            'percentages': {}
        }
        
        if question_info['type'] == 'MC':
            # Multiple choice - split by semicolon and count each option
            all_options = []
            for value in self._data[column_name].dropna():
                if pd.notna(value) and str(value).strip():
                    options = [opt.strip() for opt in str(value).split(';') if opt.strip()]
                    all_options.extend(options)
            
            counts = Counter(all_options)
            
            if top_n:
                counts = dict(counts.most_common(top_n))
            else:
                counts = dict(counts)
            
            result['distribution'] = counts
            total_selections = sum(counts.values())
            result['percentages'] = {k: (v / total_selections * 100) for k, v in counts.items()}
            result['total_selections'] = total_selections
            
        else:
            # Single choice - direct value counts
            counts = self._data[column_name].value_counts()
            
            if top_n:
                counts = counts.head(top_n)
            
            result['distribution'] = counts.to_dict()
            result['percentages'] = (counts / result['valid_responses'] * 100).to_dict()
        
        return result
    
    def display_distribution(self, column_name: str, top_n: Optional[int] = 10) -> None:
        """
        Display the answer distribution for a question in a formatted way.
        
        Args:
            column_name: The question column name
            top_n: Optional limit to top N answers
        """
        try:
            dist_data = self.get_answer_distribution(column_name, top_n)
            
            print(f"\n{'='*80}")
            print(f"ANSWER DISTRIBUTION")
            print(f"{'='*80}")
            print(f"Question: {dist_data['question']['question_text']}")
            print(f"Type: {dist_data['question']['type']}")
            print(f"Total Respondents: {dist_data['total_responses']:,}")
            print(f"Valid Responses: {dist_data['valid_responses']:,}")
            
            if dist_data['question']['type'] == 'MC':
                print(f"Total Selections: {dist_data['total_selections']:,}")
            
            print(f"\n{'-'*80}")
            print(f"{'Option':<50} {'Count':<10} {'Percentage':<10}")
            print(f"{'-'*80}")
            
            for option, count in dist_data['distribution'].items():
                percentage = dist_data['percentages'][option]
                # Truncate long options
                display_option = option[:47] + "..." if len(str(option)) > 50 else str(option)
                print(f"{display_option:<50} {count:<10} {percentage:>9.1f}%")
                
        except Exception as e:
            print(f"Error displaying distribution: {e}")
    
    def get_unique_options(self, column_name: str) -> List[str]:
        """
        Get all unique options for a question (useful for MC questions).
        
        Args:
            column_name: The question column name
            
        Returns:
            List of unique options
        """
        self._load_data()
        
        question_info = self.get_question_info(column_name)
        if not question_info:
            raise ValueError(f"Question '{column_name}' not found in schema")
        
        if question_info['type'] == 'MC':
            # Multiple choice - split by semicolon
            all_options = set()
            for value in self._data[column_name].dropna():
                if pd.notna(value) and str(value).strip():
                    options = [opt.strip() for opt in str(value).split(';') if opt.strip()]
                    all_options.update(options)
            return sorted(list(all_options))
        else:
            # Single choice - unique values
            return sorted(self._data[column_name].dropna().unique().tolist())
    
    def summary_stats(self) -> Dict:
        """
        Get summary statistics about the survey.
        
        Returns:
            Dictionary with summary statistics
        """
        self._load_data()
        
        stats = {
            'total_questions': len(self._schema),
            'total_respondents': len(self._data),
            'question_types': self._schema['type'].value_counts().to_dict(),
            'completion_rate': {}
        }
        
        # Calculate completion rates for a sample of questions
        for q_type in ['SC', 'MC']:
            type_questions = self._schema[self._schema['type'] == q_type]['column'].tolist()
            if type_questions:
                # Sample first few questions of this type
                sample_questions = type_questions[:3]
                completion_rates = []
                for col in sample_questions:
                    if col in self._data.columns:
                        valid_responses = self._data[col].notna().sum()
                        rate = valid_responses / len(self._data) * 100
                        completion_rates.append(rate)
                
                if completion_rates:
                    stats['completion_rate'][q_type] = sum(completion_rates) / len(completion_rates)
        
        return stats
    
    def display_summary(self) -> None:
        """Display summary statistics about the survey."""
        stats = self.summary_stats()
        
        print(f"\n{'='*80}")
        print(f"SURVEY SUMMARY")
        print(f"{'='*80}")
        print(f"Total Questions: {stats['total_questions']}")
        print(f"Total Respondents: {stats['total_respondents']:,}")
        
        print(f"\nQuestion Types:")
        for q_type, count in stats['question_types'].items():
            type_name = {'SC': 'Single Choice', 'MC': 'Multiple Choice', 'TE': 'Text Entry'}.get(q_type, q_type)
            print(f"  {type_name}: {count}")
        
        print(f"\nAverage Completion Rates:")
        for q_type, rate in stats['completion_rate'].items():
            type_name = {'SC': 'Single Choice', 'MC': 'Multiple Choice'}.get(q_type, q_type)
            print(f"  {type_name}: {rate:.1f}%")