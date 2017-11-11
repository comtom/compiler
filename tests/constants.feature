Feature: Constants
  This tests checks that constants comply language's rules ( between -2^15 and 2^(15)-1 )

  Scenario Outline: Constants with prefix
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | _i51515                                                  |
      | _i45647                                                  |
      | _i45647                                                  |
      | _l4294967200                                             |
      | _l-4294967200                                            |
      | _i65530                                                  |
      | _i-65530                                                 |


  Scenario Outline: Constants without prefix
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | 51515                                                    |
      | 45647                                                    |


  Scenario Outline: Constants under valid range
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must accept the input

    Examples:
      | program                                                  |
      | 32767                                                    |
      | -32768                                                   |
      | _i32767                                                  |
      | _i-32768                                                 |
      | _l4294967200                                             |
      | _l-4294967200                                            |
      | _l4294967295                                             |
      | _l-4294967296                                            |


  Scenario Outline: Constants out of valid range
    Given a mocked source <program>
    When the user invokes the compiler with the program as an argument
    Then compiler must reject the input

    Examples:
      | program                                                  |
      | 32768                                                    |
      | 320768                                                   |
      | -320769                                                  |
      | -320769                                                  |
      | _i327568                                                 |
      | _i-327639                                                |
      | _l4294967296                                             |
      | _l-4294967297                                            |
