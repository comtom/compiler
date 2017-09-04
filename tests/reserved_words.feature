# Created by comtom at 9/3/17
Feature: Reserved Words
  This test tests reserved words case, as the language is case sensitive

  Scenario Outline: Reserved words written in lower caps
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                   |
      | if some_thing == other_thing { a = 1 }                    |
      | else a = 0                                                |
      | endif                                                     |
      | print a                                                   |


  Scenario Outline: Reserved words written in uppercase
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                   |
      | if some_thing == other_thing { a = 1 }                    |
      | else a = 0                                                |
      | endif                                                     |
      | print a                                                   |
      | while                                                     |
      | integer                                                   |
      | longint                                                   |


  Scenario Outline: Reserved words written in mixed case
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must reject the input

    Examples:
      | program                                                   |
      | If some_thing == other_thing { a = 1 }                    |
      | iF some_thing == other_thing { a = 1 }                    |
      | ElSe a = 0                                                |
      | elSe a = 0                                                |
      | EndIf                                                     |
      | endIf                                                     |
      | EnDiF                                                     |
      | prinT a                                                   |
      | Print a                                                   |
      | prInT a                                                   |
      | wHiLe                                                     |
      | While                                                     |

