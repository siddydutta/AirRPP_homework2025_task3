"""
Unit tests for Stack Overflow Survey Analyzer

This module contains comprehensive tests for all major functionality
of the StackOverflowSurveyAnalyzer class.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open
import os
import sys

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from so_survey_analyzer import StackOverflowSurveyAnalyzer


class TestStackOverflowSurveyAnalyzer:
    """Test cases for StackOverflowSurveyAnalyzer class."""
    
    @pytest.fixture
    def test_data_dir(self):
        """Get the test data directory path."""
        return os.path.join(os.path.dirname(__file__), 'test_data')
    
    @pytest.fixture
    def analyzer(self, test_data_dir):
        """Create an analyzer instance with test data."""
        data_file = os.path.join(test_data_dir, 'test_raw_data.csv')
        schema_file = os.path.join(test_data_dir, 'test_schema.csv')
        return StackOverflowSurveyAnalyzer(data_file, schema_file)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample test data."""
        return pd.DataFrame({
            'MainBranch': ['I am a developer by profession', 'I am learning to code', 'I am a developer by profession'],
            'Age': ['25-34 years old', '18-24 years old', '35-44 years old'],
            'LanguageHaveWorkedWith': ['Python;JavaScript', 'Python', 'Java;Python;SQL'],
            'Country': ['USA', 'Canada', 'UK']
        })
    
    @pytest.fixture
    def sample_schema(self):
        """Create sample schema data."""
        return pd.DataFrame({
            'column': ['MainBranch', 'Age', 'LanguageHaveWorkedWith', 'Country'],
            'question_text': [
                'Which describes you?',
                'What is your age?',
                'Which languages have you worked with?',
                'Where do you live?'
            ],
            'type': ['SC', 'SC', 'MC', 'SC']
        })
    
    def test_initialization(self, analyzer):
        """Test that the analyzer initializes correctly."""
        assert analyzer.data is not None
        assert analyzer.schema is not None
        assert len(analyzer.data) == 5  # Test data has 5 rows
        assert len(analyzer.schema) == 10  # Test schema has 10 questions
        assert analyzer.schema_dict is not None
    
    def test_initialization_file_not_found(self):
        """Test that proper exception is raised when files don't exist."""
        with pytest.raises(FileNotFoundError):
            StackOverflowSurveyAnalyzer('nonexistent.csv', 'also_nonexistent.csv')
    
    def test_search_questions(self, analyzer):
        """Test the search_questions method."""
        # Test case-insensitive search
        results = analyzer.search_questions('programming')
        assert len(results) == 2  # Should find LanguageHaveWorkedWith and LanguageWantToWorkWith
        
        # Test case-sensitive search
        results = analyzer.search_questions('Programming', case_sensitive=True)
        assert len(results) == 0  # Should find nothing with capital P
        
        # Test search with no results
        results = analyzer.search_questions('nonexistent_term')
        assert len(results) == 0
        
        # Test that results have correct structure
        results = analyzer.search_questions('language')
        for result in results:
            assert 'column' in result
            assert 'question_text' in result
            assert 'type' in result
    
    def test_get_questions_by_type(self, analyzer):
        """Test filtering questions by type."""
        sc_questions = analyzer.get_questions_by_type('SC')
        mc_questions = analyzer.get_questions_by_type('MC')
        
        # Verify we get expected counts
        assert len(sc_questions) == 6  # SC questions in test data
        assert len(mc_questions) == 4  # MC questions in test data
        
        # Verify all returned questions have correct type
        for question in sc_questions:
            assert question['type'] == 'SC'
        
        for question in mc_questions:
            assert question['type'] == 'MC'
    
    def test_create_subset_single_choice(self, analyzer):
        """Test creating subsets for single-choice questions."""
        # Test filtering by MainBranch
        subset = analyzer.create_subset('MainBranch', 'I am a developer by profession')
        assert len(subset) == 3  # Should have 3 developers in test data
        
        # Test filtering by a value that doesn't exist
        subset = analyzer.create_subset('MainBranch', 'Nonexistent value')
        assert len(subset) == 0
    
    def test_create_subset_multiple_choice(self, analyzer):
        """Test creating subsets for multiple-choice questions."""
        # Test filtering by programming language
        subset = analyzer.create_subset('LanguageHaveWorkedWith', 'Python')
        assert len(subset) == 3  # Should have 3 Python users in test data
        
        subset = analyzer.create_subset('LanguageHaveWorkedWith', 'JavaScript')
        assert len(subset) == 2  # Should have 2 JavaScript users in test data
    
    def test_create_subset_invalid_column(self, analyzer):
        """Test creating subset with invalid column name."""
        with pytest.raises(ValueError, match="Column 'InvalidColumn' not found"):
            analyzer.create_subset('InvalidColumn', 'some_value')
    
    def test_create_subset_with_custom_data(self, analyzer):
        """Test creating subset using custom data parameter."""
        # First create a subset
        first_subset = analyzer.create_subset('MainBranch', 'I am a developer by profession')
        
        # Then create a subset of that subset
        second_subset = analyzer.create_subset('Age', '25-34 years old', data=first_subset)
        
        # Should have developers aged 25-34
        assert len(second_subset) == 2
    
    def test_get_unique_values_single_choice(self, analyzer):
        """Test getting unique values for single-choice questions."""
        unique_values = analyzer.get_unique_values('MainBranch')
        
        expected_values = [
            'I am a developer by profession',
            'I am learning to code',
            'I code primarily as a hobby'
        ]
        
        for value in expected_values:
            assert value in unique_values
    
    def test_get_unique_values_multiple_choice(self, analyzer):
        """Test getting unique values for multiple-choice questions."""
        unique_values = analyzer.get_unique_values('LanguageHaveWorkedWith')
        
        expected_languages = ['Python', 'JavaScript', 'HTML/CSS', 'Java', 'SQL', 'C#']
        
        for language in expected_languages:
            assert language in unique_values
    
    def test_get_unique_values_invalid_column(self, analyzer):
        """Test getting unique values with invalid column name."""
        with pytest.raises(ValueError, match="Column 'InvalidColumn' not found"):
            analyzer.get_unique_values('InvalidColumn')
    
    def test_get_distribution_single_choice(self, analyzer):
        """Test getting distribution for single-choice questions."""
        dist_data = analyzer.get_distribution('MainBranch')
        
        assert dist_data['column'] == 'MainBranch'
        assert dist_data['question_type'] == 'SC'
        assert dist_data['total_responses'] == 5
        assert dist_data['valid_responses'] == 5
        
        # Check that we have the expected options
        distribution = dist_data['distribution']
        assert 'I am a developer by profession' in distribution
        assert distribution['I am a developer by profession']['count'] == 3
        assert abs(distribution['I am a developer by profession']['percentage'] - 60.0) < 0.1
    
    def test_get_distribution_multiple_choice(self, analyzer):
        """Test getting distribution for multiple-choice questions."""
        dist_data = analyzer.get_distribution('LanguageHaveWorkedWith')
        
        assert dist_data['column'] == 'LanguageHaveWorkedWith'
        assert dist_data['question_type'] == 'MC'
        
        distribution = dist_data['distribution']
        assert 'Python' in distribution
        assert distribution['Python']['count'] == 3  # Python appears 3 times
    
    def test_get_distribution_with_limit(self, analyzer):
        """Test getting distribution with limit parameter."""
        dist_data = analyzer.get_distribution('LanguageHaveWorkedWith', limit=2)
        
        # Should only return top 2 results
        assert len(dist_data['distribution']) <= 2
    
    def test_get_distribution_invalid_column(self, analyzer):
        """Test getting distribution with invalid column name."""
        with pytest.raises(ValueError, match="Column 'InvalidColumn' not found"):
            analyzer.get_distribution('InvalidColumn')
    
    def test_get_distribution_with_custom_data(self, analyzer):
        """Test getting distribution using custom data parameter."""
        # Create a subset first
        subset = analyzer.create_subset('MainBranch', 'I am a developer by profession')
        
        # Get distribution of the subset
        dist_data = analyzer.get_distribution('Age', data=subset)
        
        assert dist_data['total_responses'] == 3
        assert len(dist_data['distribution']) == 2  # Should have 2 different ages
    
    @patch('builtins.print')
    def test_display_survey_structure(self, mock_print, analyzer):
        """Test displaying survey structure."""
        analyzer.display_survey_structure()
        
        # Verify that print was called (output was generated)
        assert mock_print.called
        
        # Test filtering by type
        analyzer.display_survey_structure('SC')
        assert mock_print.called
    
    @patch('builtins.print')
    def test_display_distribution(self, mock_print, analyzer):
        """Test displaying distribution."""
        analyzer.display_distribution('MainBranch')
        
        # Verify that print was called (output was generated)
        assert mock_print.called
    
    def test_get_summary_stats(self, analyzer):
        """Test getting summary statistics."""
        stats = analyzer.get_summary_stats()
        
        assert 'total_responses' in stats
        assert 'total_questions' in stats
        assert 'question_types' in stats
        assert 'data_shape' in stats
        assert 'missing_values' in stats
        assert 'memory_usage_mb' in stats
        
        assert stats['total_responses'] == 5
        assert stats['total_questions'] == 10
        
        question_types = stats['question_types']
        assert 'single_choice' in question_types
        assert 'multiple_choice' in question_types
        assert 'text_entry' in question_types
    
    def test_data_loading_with_missing_values(self, tmp_path):
        """Test data loading with missing values."""
        # Create test files with missing values
        data_content = """MainBranch,Age,Country
I am a developer by profession,25-34 years old,USA
,18-24 years old,Canada
I am learning to code,,UK"""
        
        schema_content = """column,question_text,type
MainBranch,Which describes you?,SC
Age,What is your age?,SC
Country,Where do you live?,SC"""
        
        data_file = tmp_path / "test_data.csv"
        schema_file = tmp_path / "test_schema.csv"
        
        data_file.write_text(data_content)
        schema_file.write_text(schema_content)
        
        analyzer = StackOverflowSurveyAnalyzer(str(data_file), str(schema_file))
        
        # Test that missing values are handled correctly
        unique_values = analyzer.get_unique_values('MainBranch')
        assert len(unique_values) == 2  # Should exclude NaN values
        
        dist_data = analyzer.get_distribution('Age')
        assert dist_data['valid_responses'] == 2  # Should count only non-null values
    
    def test_edge_cases(self, analyzer):
        """Test various edge cases."""
        # Test empty search term
        results = analyzer.search_questions('')
        assert len(results) == 10  # Should return all questions
        
        # Test search with special characters
        results = analyzer.search_questions('?')
        assert len(results) > 0  # Should find questions with question marks
        
        # Test distribution with all missing values column (if such column exists)
        # This would depend on the test data structure
        # No specific test implemented yet
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_mode_quit(self, mock_print, mock_input, analyzer):
        """Test interactive mode quit command."""
        mock_input.return_value = 'quit'
        
        analyzer.interactive_mode()
        
        # Verify that goodbye message was printed
        mock_print.assert_any_call("Goodbye!")
    
    def test_method_chaining(self, analyzer):
        """Test that methods can be chained effectively."""
        # Create a complex analysis pipeline
        developers = analyzer.create_subset('MainBranch', 'I am a developer by profession')
        python_devs = analyzer.create_subset('LanguageHaveWorkedWith', 'Python', data=developers)
        
        assert len(python_devs) == 2  # Should have 2 Python developers
        
        # Get distribution on the filtered data
        dist_data = analyzer.get_distribution('Age', data=python_devs)
        assert dist_data['total_responses'] == 2


class TestAnalyzerHelperMethods:
    """Test helper methods of the analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer with mock data."""
        with patch('pandas.read_csv') as mock_read:
            # Mock data
            mock_data = pd.DataFrame({
                'MainBranch': ['Developer', 'Learning'],
                'Age': ['25-34', '18-24']
            })
            
            mock_schema = pd.DataFrame({
                'column': ['MainBranch', 'Age'],
                'question_text': ['What are you?', 'How old?'],
                'type': ['SC', 'SC']
            })
            
            mock_read.side_effect = [mock_data, mock_schema]
            
            return StackOverflowSurveyAnalyzer('dummy.csv', 'dummy_schema.csv')
    
    def test_show_help(self, analyzer):
        """Test the help display method."""
        with patch('builtins.print') as mock_print:
            analyzer._show_help()
            assert mock_print.called
    
    def test_show_question_types(self, analyzer):
        """Test the question types display method."""
        with patch('builtins.print') as mock_print:
            analyzer._show_question_types()
            assert mock_print.called
    
    def test_show_data_info(self, analyzer):
        """Test the data info display method."""
        with patch('builtins.print') as mock_print:
            analyzer._show_data_info(analyzer.data)
            assert mock_print.called


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_corrupted_csv_handling(self, tmp_path):
        """Test handling of corrupted CSV files."""
        # Create a CSV file that will cause pandas to fail
        corrupted_content = "column1,column2,column3\n\"unclosed quote,value2,value3\nvalue4,value5,value6"
        
        data_file = tmp_path / "corrupted.csv"
        schema_file = tmp_path / "valid_schema.csv"
        
        data_file.write_text(corrupted_content)
        schema_file.write_text("column,question_text,type\ntest,test question,SC")
        
        with pytest.raises(Exception):  # Should raise some kind of exception
            StackOverflowSurveyAnalyzer(str(data_file), str(schema_file))
    
    def test_mismatched_schema(self, tmp_path):
        """Test handling when data and schema don't match."""
        data_content = "Column1,Column2\nValue1,Value2\n"
        schema_content = "column,question_text,type\nColumn3,Different column,SC\n"
        
        data_file = tmp_path / "data.csv"
        schema_file = tmp_path / "schema.csv"
        
        data_file.write_text(data_content)
        schema_file.write_text(schema_content)
        
        analyzer = StackOverflowSurveyAnalyzer(str(data_file), str(schema_file))
        
        # Should handle gracefully when schema refers to non-existent columns
        with pytest.raises(ValueError):
            analyzer.create_subset('Column3', 'some_value')


if __name__ == "__main__":
    pytest.main([__file__])
