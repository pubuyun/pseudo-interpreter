DECLARE Text : STRING
FOR I <- 1 TO 5
    Text <- ""
    FOR J <- 1 TO I
        Text <- Text & J & " "
    NEXT
    OUTPUT Text
NEXT I

DECLARE Counter : INTEGER
DECLARE AnotherCounter : INTEGER
Counter <- 1
WHILE Counter <= 3 DO
    FOR i <- 1 TO 3
        AnotherCounter <- 1
        REPEAT
            OUTPUT Counter & ", " & i & ", " & AnotherCounter
            AnotherCounter <- AnotherCounter + 1
        UNTIL AnotherCounter > 3
    NEXT i
    Counter <- Counter + 1
ENDWHILE
