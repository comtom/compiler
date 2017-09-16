Feature: Check lexical analyzer
  To check lexical analyzer, compiler output must be equal than input

  Scenario: Input program is equal than compiler output
    Given a program source file named example.code
    When the user invokes the compiler with the program as an argument
    Then input program is equal to output
