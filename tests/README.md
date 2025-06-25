# Tests for GPT Researcher

This directory contains unit tests for the GPT Researcher project. The tests are designed to verify the functionality of various utility functions and core components.

## Test Structure

The test suite is organized into the following modules:

- `test_pipeline.py` - Tests for the pipeline module, specifically the `generate_task_id` function
- `test_singleton.py` - Tests for the Singleton metaclass implementation
- `test_class_loader.py` - Tests for the dynamic class loading utility
- `test_time_usage_record.py` - Tests for time formatting functions
- `test_config_center.py` - Tests for configuration management utilities

## Running Tests

### Using the Test Runner

The easiest way to run all tests is using the provided test runner:

```bash
python run_tests.py
```

This will run all tests with verbose output and provide a summary of results.

### Using Python's unittest module

You can also run tests directly using Python's built-in unittest module:

```bash
# Run all tests
python -m unittest discover tests -v

# Run a specific test file
python -m unittest tests.test_pipeline -v

# Run a specific test class
python -m unittest tests.test_pipeline.TestPipeline -v

# Run a specific test method
python -m unittest tests.test_pipeline.TestPipeline.test_generate_task_id_basic -v
```

## Test Coverage

The current test suite covers:

### Pipeline Module
- `generate_task_id` function with various input scenarios:
  - Basic string processing
  - Special character handling
  - Unicode character handling
  - Edge cases (empty strings, only special characters)
  - Leading/trailing underscore stripping

### Singleton Pattern
- Single instance creation and reuse
- Different classes having separate instances
- Inheritance behavior
- Constructor argument handling
- Instance storage verification

### Class Loader
- Dynamic class loading from modules
- Inheritance chain detection
- Filtering of base classes and unrelated classes
- Error handling for non-existent modules

### Time Usage Record
- Time formatting consistency
- Various timestamp scenarios
- Edge cases (epoch time, future dates)

### Config Center
- Dictionary merging functionality
- Nested dictionary handling
- Type mixing and overwriting behavior
- Edge cases (empty dictionaries)

## Test Design Principles

The tests follow these principles:

1. **Isolation**: Each test is independent and doesn't rely on external dependencies
2. **Clarity**: Test names clearly describe what is being tested
3. **Coverage**: Tests cover both normal use cases and edge cases
4. **Maintainability**: Tests are easy to understand and modify

## Adding New Tests

When adding new tests:

1. Create a new test file following the naming convention `test_<module_name>.py`
2. Import the necessary modules and functions
3. Create test classes inheriting from `unittest.TestCase`
4. Write descriptive test method names starting with `test_`
5. Include docstrings explaining what each test verifies
6. Test both normal cases and edge cases
7. Use appropriate assertions (`assertEqual`, `assertTrue`, `assertRaises`, etc.)

## Dependencies

The tests use only Python's standard library:
- `unittest` for the testing framework
- `sys` and `os` for path manipulation
- `tempfile` for temporary file creation in some tests
- `time` for time-related testing

No external dependencies are required to run the tests.