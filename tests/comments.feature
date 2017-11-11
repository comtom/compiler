Feature: Comments
  This tests checks that comments starts with "&&" and ends with CR/LF

  Scenario Outline: Well defined comments
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must remove comments and accept the input

    Examples:
      | program                                                  |
      | && valid comment \n                                      |
      | && valid comment if \n                                   |
      | && valid comment #1 \n                                   |
      | && valid comment #2 \n                                   |


  Scenario Outline: Invalid comments
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must not accept the input

    Examples:
      | program                                                   |
      | & invalid comment                                         |
      | & valid comment #0 '''                                    |
      | /* valid comment #1 */                                    |
