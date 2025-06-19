# Stack Overflow Survey Data Analyzer

A Python library for analyzing Stack Overflow Developer Survey data. This library provides functionality to explore survey structure, search questions, create respondent subsets, and analyze answer distributions for both Single Choice (SC) and Multiple Choice (MC) questions.

## Features

- **Survey Structure Exploration**: Display all questions with their types and descriptions
- **Question Search**: Find questions by keyword in question text or column names
- **Respondent Subsets**: Filter respondents based on specific question responses
- **Answer Distribution Analysis**: Calculate and display answer distributions with percentages
- **Interactive CLI**: Command-line interface for easy data exploration
- **Lazy Loading**: Efficient memory usage by loading data only when needed

## Installation

1. Clone or download this repository
2. Extract the data file:

```bash
unzip data.zip
```

3. Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## Project Structure

```
task-3/
├── stackoverflow_analyzer/
│   ├── __init__.py          # Main library interface
│   ├── analyzer.py          # Core analyzer class
│   └── cli.py              # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_analyzer.py    # Unit tests
├── schema.csv              # Survey schema (questions metadata)
├── raw_data.csv           # Survey responses data
└── README.md              # This file
```

## Usage

### As a Python Library

```python
from stackoverflow_analyzer import StackOverflowAnalyzer

# Initialize the analyzer
analyzer = StackOverflowAnalyzer('schema.csv', 'raw_data.csv')

# Display survey summary
analyzer.display_summary()

# Show survey structure
analyzer.display_survey_structure()

# Search for questions about programming languages
matches = analyzer.search_questions('language')

# Get answer distribution for age groups
analyzer.display_distribution('Age', top_n=5)

# Create subset of professional developers
subset = analyzer.create_subset('MainBranch', 'I am a developer by profession')

# Get unique options for a multiple choice question
options = analyzer.get_unique_options('LanguageHaveWorkedWith')
```

### Using the Interactive CLI

Run the interactive command-line interface:

```bash
python -m stackoverflow_analyzer.cli schema.csv raw_data.csv
```

#### Available CLI Commands

**Data Exploration:**
- `summary` - Show survey summary statistics
- `structure [type]` - Show survey structure (optional: filter by SC, MC, TE)

**Search & Discovery:**
- `search <term>` - Search questions by keyword
- `info <column>` - Get information about a specific question
- `options <column>` - List unique options for a question

**Analysis:**
- `dist <column> [n]` - Show answer distribution (optional: top n results)
- `subset <column> <value>` - Create respondent subset

**Utility:**
- `help` - Show help message
- `quit/exit` - Exit the program

#### CLI Examples

```bash
so-analyzer> structure SC
so-analyzer> search language
so-analyzer> dist Age 5
so-analyzer> subset MainBranch "I am a developer by profession"
so-analyzer> options LanguageHaveWorkedWith
```

## API Reference

### StackOverflowAnalyzer Class

#### Initialization
```python
analyzer = StackOverflowAnalyzer(schema_file, data_file)
```

#### Key Methods

**display_survey_structure(question_type=None)**
- Display survey questions and their types
- Optional filter by question type ('SC', 'MC', 'TE')

**search_questions(search_term, case_sensitive=False)**
- Search for questions containing a specific term
- Returns DataFrame with matching questions

**get_question_info(column_name)**
- Get detailed information about a specific question
- Returns dictionary with question metadata

**create_subset(column_name, option_value, exact_match=True)**
- Create subset of respondents based on question response
- Handles both SC and MC questions appropriately

**get_answer_distribution(column_name, top_n=None)**
- Get answer distribution data for a question
- Returns dictionary with counts and percentages

**display_distribution(column_name, top_n=10)**
- Display formatted answer distribution
- Shows counts and percentages in readable format

**get_unique_options(column_name)**
- Get all unique response options for a question
- Useful for exploring MC question options

**summary_stats()**
- Get overall survey statistics
- Returns completion rates and question type counts

## Data Format

### Schema File (schema.csv)
Contains question metadata with columns:
- `column`: Column name in the data file
- `question_text`: Human-readable question text
- `type`: Question type (SC=Single Choice, MC=Multiple Choice, TE=Text Entry)

### Data File (raw_data.csv)
Contains survey responses where:
- Single Choice (SC): One value per respondent
- Multiple Choice (MC): Semicolon-delimited values (e.g., "Python;JavaScript;HTML/CSS")
- Each row represents one survey respondent

## Running Tests

Execute the unit tests:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_analyzer

# Run with verbose output
python -m unittest tests.test_analyzer -v
```

The test suite includes:
- Schema and data loading tests
- Question search functionality
- Subset creation for SC and MC questions
- Answer distribution calculations
- Error handling scenarios

## Examples

### Basic Analysis Workflow

```python
# Load the analyzer
analyzer = StackOverflowAnalyzer('schema.csv', 'raw_data.csv')

# Explore the survey structure
analyzer.display_summary()

# Find questions about AI
ai_questions = analyzer.search_questions('AI')

# Analyze age distribution
analyzer.display_distribution('Age')

# Look at programming languages
analyzer.display_distribution('LanguageHaveWorkedWith', top_n=10)

# Create subset of remote workers and analyze their language preferences
remote_workers = analyzer.create_subset('RemoteWork', 'Remote')
# Note: You would need to create a new analyzer instance with the subset data
# to analyze the subset further
```

### Advanced Usage

```python
# Get raw distribution data for custom analysis
dist_data = analyzer.get_answer_distribution('Country')
countries = list(dist_data['distribution'].keys())
counts = list(dist_data['distribution'].values())

# Explore multiple choice question options
lang_options = analyzer.get_unique_options('LanguageHaveWorkedWith')
print(f"Survey covers {len(lang_options)} programming languages")

# Find all AI-related questions
ai_questions = analyzer.search_questions('AI')
for _, question in ai_questions.iterrows():
    print(f"{question['column']}: {question['type']}")
```

## Notes

- The library uses lazy loading to handle large datasets efficiently
- Multiple choice questions are split on semicolon (`;`) delimiters
- All percentage calculations are based on valid (non-null) responses
- The CLI provides an interactive way to explore data without writing code

## Requirements

- Python 3.6+
- pandas
- Standard library modules: csv, os, sys, tempfile (for tests)

## License

This project is provided as-is for educational and analysis purposes.