# Stack Overflow Survey Data Analysis Library

A Python library for analyzing Stack Overflow Developer Survey data with support for displaying survey structure, searching questions, creating respondent subsets, and analyzing answer distributions.

## Features

- Display survey structure (list of questions) to CLI/REPL
- Search for specific questions or options
- Make respondent subsets based on question + option criteria
- Display distribution of answers (shares) for Single Choice (SC) and Multiple Choice (MC) questions
- Comprehensive unit tests for all primary functions

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project files**

2. **Extract the survey data**
   
   If you have `data.zip`, extract it first:
   ```bash
   unzip data.zip
   ```
   
   This should create `raw_data.csv` and `schema.csv` files in your project directory.

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the example (optional)**
   ```bash
   python example.py
   ```
   
   This will demonstrate all the key features of the library using the survey data.

## Usage

### Basic Usage

```python
from so_survey_analyzer import StackOverflowSurveyAnalyzer

# Initialize the analyzer
analyzer = StackOverflowSurveyAnalyzer('raw_data.csv', 'schema.csv')

# Display survey structure
analyzer.display_survey_structure()

# Search for questions
results = analyzer.search_questions('programming language')
print(results)

# Create a subset of respondents
subset = analyzer.create_subset('MainBranch', 'I am a developer by profession')

# Display answer distribution
analyzer.display_distribution('Age')
```

### Interactive CLI

```python
# Start interactive mode
analyzer.interactive_mode()
```

This will start an interactive session where you can:
- List all questions
- Search questions
- Create subsets
- View distributions
- And more!

### Advanced Usage

```python
# Get specific question types
sc_questions = analyzer.get_questions_by_type('SC')  # Single Choice
mc_questions = analyzer.get_questions_by_type('MC')  # Multiple Choice

# Create complex subsets
subset1 = analyzer.create_subset('Age', '25-34 years old')
subset2 = analyzer.create_subset('RemoteWork', 'Remote', data=subset1)

# Get distribution data programmatically
dist_data = analyzer.get_distribution('LanguageHaveWorkedWith')
```

## Data Structure

The library expects two CSV files:

1. **raw_data.csv**: The main survey response data (~150MB with 65k records)
2. **schema.csv**: Contains column definitions with:
   - `column`: Column name
   - `question_text`: The actual survey question
   - `type`: Question type (SC=Single Choice, MC=Multiple Choice, TE=Text Entry)

## Question Types

- **SC (Single Choice)**: Questions where respondents select one option
- **MC (Multiple Choice)**: Questions where respondents can select multiple options (semicolon-separated)
- **TE (Text Entry)**: Free-form text responses

## Performance

The library is designed to efficiently handle large datasets:
- **Memory Efficient**: Uses pandas with `low_memory=False` for optimal memory usage
- **Large Dataset Support**: Successfully tested with 65k+ survey responses (~150MB data)
- **Fast Operations**: Leverages pandas' optimized operations for data filtering and analysis
- **Interactive Performance**: Subset creation and distribution analysis complete in seconds

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run tests with coverage:

```bash
python -m pytest tests/ --cov=so_survey_analyzer --cov-report=html
```

## Project Structure

```
├── so_survey_analyzer.py      # Main library module
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py       # Unit tests
│   └── test_data/             # Test data files
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── raw_data.csv              # Survey response data (after extraction)
└── schema.csv                # Survey schema
```

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computing
- pytest: Testing framework
- pytest-cov: Coverage reporting

## Examples

### Example 1: Basic Analysis

```python
from so_survey_analyzer import StackOverflowSurveyAnalyzer

analyzer = StackOverflowSurveyAnalyzer('raw_data.csv', 'schema.csv')

# Show all questions about AI
ai_questions = analyzer.search_questions('AI')
for q in ai_questions:
    print(f"{q['column']}: {q['question_text']}")

# Analyze AI tool usage among developers
developers = analyzer.create_subset('MainBranch', 'I am a developer by profession')
analyzer.display_distribution('AISelect', data=developers)
```

### Example 2: Comparative Analysis

```python
# Compare remote vs in-person work preferences
remote_workers = analyzer.create_subset('RemoteWork', 'Remote')
inperson_workers = analyzer.create_subset('RemoteWork', 'In-person')

print("Remote workers language preferences:")
analyzer.display_distribution('LanguageHaveWorkedWith', data=remote_workers)

print("\nIn-person workers language preferences:")
analyzer.display_distribution('LanguageHaveWorkedWith', data=inperson_workers)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is provided as-is for educational and analysis purposes.
