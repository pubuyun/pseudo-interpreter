DECLARE myList : ARRAY[0:8] OF INTEGER
DECLARE ub : INTEGER
DECLARE lb : INTEGER
DECLARE i : INTEGER
DECLARE swap : BOOLEAN
DECLARE temp : INTEGER
DECLARE top : INTEGER
ub <- 8
lb <- 0
top <- ub
myList[0] <- 27
myList[1] <- 19
myList[2] <- 36
myList[3] <- 42
myList[4] <- 16
myList[5] <- 89
myList[6] <- 21
myList[7] <- 16
myList[8] <- 55
REPEAT
    FOR i <- lb TO top - 1
        swap <- FALSE
        IF myList[i] > myList[i+1]
          THEN
             temp <- myList[i]
             myList[i] <- myList[i+1]
             myList[i+1] <- temp
             swap <- TRUE
        ENDIF
    NEXT
    top <- top - 1
UNTIL (NOT swap) AND (top = 0)  



FOR i <- 0 TO 8
    OUTPUT myList[i]
NEXT