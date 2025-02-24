DECLARE arr : ARRAY[1:10] OF REAL
DECLARE arrTwo : ARRAY[0 : 9] OF INTEGER

FOR i <- 1 TO 10
    arr[i] <- i * 2
    arrTwo[i - 1] <- arr[i]
NEXT i


FOR i <- 0 TO 9
    OUTPUT arr[i + 1]
    OUTPUT arrTwo[i]
NEXT i

DECLARE singleElArr : ARRAY[0:1] OF STRING

singleElArr[0] <- "hello"
OUTPUT singleElArr[0]

DECLARE intArr : ARRAY[0:1] OF INTEGER
intArr[0] <- 1
OUTPUT intArr[0]


DECLARE ArrTwoD : ARRAY[1:5, 1:5] OF INTEGER
DECLARE ArrThreeD : ARRAY[1:5, 0:4, 2:6] OF INTEGER

FOR i <- 1 TO 5
    FOR j <- 1 TO 5
        ArrTwoD[i, j] <- i + j
        FOR k <- 2 TO 6
            ArrThreeD[i, j - 1, k] <- i + (j - 1) - k
        NEXT k
    NEXT j
NEXT i

FOR i <- 1 TO 5
    FOR j <- 1 TO 5
        OUTPUT "ArrTwoD[" & i & ", " & j & "]: " & ArrTwoD[i, j]
    NEXT j
NEXT i

FOR i <- 1 TO 5
    FOR j <- 0 TO 4
        FOR k <- 2 TO 6
            OUTPUT "ArrThreeD[" & i & ", " & j & ", " & k & "]: " & ArrThreeD[i, j, k]
        NEXT k
    NEXT j
NEXT i