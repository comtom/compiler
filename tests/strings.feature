Feature: Strings
  This test ensures that the compiler accepts valid strings defined as '''example'''. The string must have a + at the end of each extra line

  Scenario Outline: Well defined strings
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | " valid string "                                         |
      | " valid string #1 "                                      |
      | " valid string #2 +\n  Other line +\n  Last line "       |


  Scenario Outline: Invalid strings
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must not accept the input

    Examples:
      | program                                                  |
      | " invalid string \n "                                    |
      | "" valid string #0 """                                   |
      | " valid string #1 '                                      |
      | " valid string #2 \n  Other line +\n  Last line "        |
      | " valid string #3 +\n  Other line \n  Last line "        |
