FUNCTION factorial(x : INTEGER) RETURNS INTEGER
    IF x = 0 THEN
        RETURN 1
    ENDIF
    RETURN x * factorial(x - 1)
ENDFUNCTION

FOR i <- 1 TO 10
    OUTPUT factorial(i)
NEXT i