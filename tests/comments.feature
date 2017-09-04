# Created by comtom at 9/3/17
Feature: Comments
  This tests checks that comments starts with “&&” and ends with CR/LF

  Scenario: Well defined comments
    Given a mocked source program
    When the user invokes the compiler with the program as an argument
      - ''' valid comment '''
      - ''' valid comment #1 '''
      - ''' valid comment #2 +\n  Other line +\n  Last line '''
    Then compiler must remove comments and accept the input


  Scenario: Invalid comments
    Given a mocked source program
    When the user invokes the compiler with the program as an argument
      - ''' invalid comment ''
      - '' valid comment #0 '''
      - ' valid comment #1 '
      - ''' valid comment #2 \n  Other line +\n  Last line '''
      - ''' valid comment #3 +\n  Other line \n  Last line '''
    Then compiler must not accept the input
