DECLARE a:INTEGER
a <- 1
FOR y <- 1 TO 5
    CASE OF y
        1: OUTPUT 1
        1 + 1: OUTPUT 2
        4 - a: OUTPUT 3
        a * 4: OUTPUT 4
        OTHERWISE: OUTPUT "5 and 6" 
    ENDCASE
NEXT y