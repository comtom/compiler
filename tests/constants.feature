Feature: Constants
  This tests checks that constants comply language's rules ( between –2^15 and 2^(15–1) )

  Scenario Outline: Constants with prefix
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | i_51515                                                  |
      | i_45647                                                  |


  Scenario Outline: Constants without prefix
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | 51515                                                    |
      | 45647                                                    |



  Scenario Outline: Constants under valid range
    # TODO: table w/ values, testing min & max values (at least 2 values for each)
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | 32767                                                    |
      | -32768                                                   |
      | i_32767                                                  |
      | i_-32768                                                 |

  Scenario Outline: Constants out of valid range
    # TODO: table w/ values, testing min & max values (at least 2 values for each)
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must reject the input

    Examples:
      | program                                                  |
      | 32768                                                    |
      | 320768                                                   |
      | -320769                                                  |
      | -320769                                                  |
      | i_327568                                                 |
      | i_-327639                                                |
