Feature: Identifiers
  This tests checks that identifiers comply language's rules

  Scenario Outline: Identifiers with less than 20 chars
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | some_identifier_name                                     |
      | short_name                                               |
      | anotherone                                               |
      | somewhat_long_valid                                      |


  Scenario Outline: Identifiers with more than 20 chars
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must reject the input

    Examples:
      | program                                                  |
      | some_very_very_long_identifier_name                      |
      | invalid_more_than_20_lines_id_name_                      |
      | anotherone_so_so_long_more_than_twenty_chars             |


  Scenario Outline: Identifiers with letters an digits
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
    | program                                                  |
    | a                                                        |
    | i                                                        |
    | temp                                                     |
    | name                                                     |


  Scenario Outline: Valid identifiers
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
    | program                                                  |
    | a                                                        |
    | i                                                        |
    | temp                                                     |
    | name                                                     |


  Scenario Outline: Invalid identifiers
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must reject the input

    Examples:
    | program                                                  |
    | some_very_very_long_identifier_name                      |
    | 258some_very_very_long_identifier_name                   |
    | 238_identifier_name                                      |
