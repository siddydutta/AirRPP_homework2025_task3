"""
Unit tests for the StackOverflowAnalyzer class.
"""

import unittest
import pandas as pd
import tempfile
import os
from unittest.mock import patch
from stackoverflow_analyzer.analyzer import StackOverflowAnalyzer


class TestStackOverflowAnalyzer(unittest.TestCase):
    """Test cases for the StackOverflowAnalyzer class."""
    
    def setUp(self):
        """Set up test data and files."""
        # Create sample schema data
        self.sample_schema = pd.DataFrame({
            'column': ['MainBranch', 'Age', 'Employment', 'LanguageHaveWorkedWith'],
            'question_text': [
                'Which of the following options best describes you today?',
                'What is your age?',
                'Which of the following best describes your current employment status?',
                'Which programming languages have you worked with?'
            ],
            'type': ['SC', 'SC', 'MC', 'MC']
        })
        
        # Create sample survey data
        self.sample_data = pd.DataFrame({
            'MainBranch': ['I am a developer by profession', 'I am learning to code', 'I am a developer by profession'],
            'Age': ['25-34 years old', '18-24 years old', '35-44 years old'],
            'Employment': ['Employed, full-time', 'Student, full-time;Employed, part-time', 'Employed, full-time'],
            'LanguageHaveWorkedWith': ['Python;JavaScript;HTML/CSS', 'Python;Java', 'JavaScript;TypeScript;Python']
        })
        
        # Create temporary files
        self.schema_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        # Write sample data to files
        self.sample_schema.to_csv(self.schema_file.name, index=False)
        self.sample_data.to_csv(self.data_file.name, index=False)
        
        self.schema_file.close()
        self.data_file.close()
        
        # Initialize analyzer
        self.analyzer = StackOverflowAnalyzer(self.schema_file.name, self.data_file.name)
    
    def tearDown(self):
        """Clean up temporary files."""
        os.unlink(self.schema_file.name)
        os.unlink(self.data_file.name)
    
    def test_init_loads_schema(self):
        """Test that initialization properly loads the schema."""
        self.assertIsNotNone(self.analyzer._schema)
        self.assertEqual(len(self.analyzer._schema), 4)
        self.assertTrue('column' in self.analyzer._schema.columns)
        self.assertTrue('question_text' in self.analyzer._schema.columns)
        self.assertTrue('type' in self.analyzer._schema.columns)
    
    def test_lazy_data_loading(self):
        """Test that data is loaded only when accessed."""
        # Initially data should be None
        self.assertIsNone(self.analyzer._data)
        
        # Access data property should trigger loading
        data = self.analyzer.data
        self.assertIsNotNone(self.analyzer._data)
        self.assertEqual(len(data), 3)
    
    def test_get_question_info_valid(self):
        """Test getting information for a valid question."""
        info = self.analyzer.get_question_info('MainBranch')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['column'], 'MainBranch')
        self.assertEqual(info['type'], 'SC')
        self.assertIn('describes you today', info['question_text'])
    
    def test_get_question_info_invalid(self):
        """Test getting information for an invalid question."""
        info = self.analyzer.get_question_info('NonExistentColumn')
        self.assertIsNone(info)
    
    def test_search_questions_found(self):
        """Test searching for questions that exist."""
        with patch('builtins.print') as mock_print:
            matches = self.analyzer.search_questions('programming')
            
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches.iloc[0]['column'], 'LanguageHaveWorkedWith')
            mock_print.assert_called()
    
    def test_search_questions_not_found(self):
        """Test searching for questions that don't exist."""
        with patch('builtins.print') as mock_print:
            matches = self.analyzer.search_questions('nonexistent')
            
            self.assertEqual(len(matches), 0)
            mock_print.assert_called()
    
    def test_create_subset_single_choice(self):
        """Test creating subset for single choice question."""
        with patch('builtins.print'):
            subset = self.analyzer.create_subset('MainBranch', 'I am a developer by profession')
            
            self.assertEqual(len(subset), 2)
            self.assertTrue(all(subset['MainBranch'] == 'I am a developer by profession'))
    
    def test_create_subset_multiple_choice(self):
        """Test creating subset for multiple choice question."""
        with patch('builtins.print'):
            subset = self.analyzer.create_subset('LanguageHaveWorkedWith', 'Python')
            
            self.assertEqual(len(subset), 3)  # All respondents have Python
    
    def test_create_subset_invalid_column(self):
        """Test creating subset with invalid column."""
        with self.assertRaises(ValueError):
            self.analyzer.create_subset('NonExistentColumn', 'SomeValue')
    
    def test_get_answer_distribution_single_choice(self):
        """Test getting distribution for single choice question."""
        dist = self.analyzer.get_answer_distribution('Age')
        
        self.assertEqual(dist['total_responses'], 3)
        self.assertEqual(dist['valid_responses'], 3)
        self.assertEqual(dist['question']['type'], 'SC')
        self.assertIn('distribution', dist)
        self.assertIn('percentages', dist)
        
        # Check that we have the expected age groups
        self.assertIn('25-34 years old', dist['distribution'])
        self.assertIn('18-24 years old', dist['distribution'])
        self.assertIn('35-44 years old', dist['distribution'])
    
    def test_get_answer_distribution_multiple_choice(self):
        """Test getting distribution for multiple choice question."""
        dist = self.analyzer.get_answer_distribution('LanguageHaveWorkedWith')
        
        self.assertEqual(dist['total_responses'], 3)
        self.assertEqual(dist['valid_responses'], 3)
        self.assertEqual(dist['question']['type'], 'MC')
        self.assertIn('total_selections', dist)
        
        # Check that Python appears most frequently
        self.assertIn('Python', dist['distribution'])
        self.assertEqual(dist['distribution']['Python'], 3)
    
    def test_get_unique_options_single_choice(self):
        """Test getting unique options for single choice question."""
        options = self.analyzer.get_unique_options('Age')
        
        self.assertEqual(len(options), 3)
        self.assertIn('25-34 years old', options)
        self.assertIn('18-24 years old', options)
        self.assertIn('35-44 years old', options)
    
    def test_get_unique_options_multiple_choice(self):
        """Test getting unique options for multiple choice question."""
        options = self.analyzer.get_unique_options('LanguageHaveWorkedWith')
        
        self.assertIn('Python', options)
        self.assertIn('JavaScript', options)
        self.assertIn('HTML/CSS', options)
        self.assertIn('Java', options)
        self.assertIn('TypeScript', options)
    
    def test_summary_stats(self):
        """Test getting summary statistics."""
        stats = self.analyzer.summary_stats()
        
        self.assertEqual(stats['total_questions'], 4)
        self.assertEqual(stats['total_respondents'], 3)
        self.assertIn('question_types', stats)
        self.assertEqual(stats['question_types']['SC'], 2)
        self.assertEqual(stats['question_types']['MC'], 2)
    
    def test_display_methods_run_without_error(self):
        """Test that display methods run without error."""
        with patch('builtins.print'):
            # These should not raise exceptions
            self.analyzer.display_survey_structure()
            self.analyzer.display_survey_structure('SC')
            self.analyzer.display_distribution('Age')
            self.analyzer.display_summary()


class TestAnalyzerErrorHandling(unittest.TestCase):
    """Test error handling in StackOverflowAnalyzer."""
    
    def test_init_with_invalid_schema_file(self):
        """Test initialization with invalid schema file."""
        with self.assertRaises(ValueError):
            StackOverflowAnalyzer('nonexistent_schema.csv', 'nonexistent_data.csv')
    
    def test_get_answer_distribution_invalid_column(self):
        """Test getting distribution for invalid column."""
        # Create minimal valid files
        schema_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        try:
            # Write minimal schema
            schema_file.write('column,question_text,type\nTest,Test question,SC\n')
            schema_file.close()
            
            # Write minimal data
            data_file.write('Test\nValue1\n')
            data_file.close()
            
            analyzer = StackOverflowAnalyzer(schema_file.name, data_file.name)
            
            with self.assertRaises(ValueError):
                analyzer.get_answer_distribution('NonExistentColumn')
        
        finally:
            os.unlink(schema_file.name)
            os.unlink(data_file.name)


if __name__ == '__main__':
    unittest.main()