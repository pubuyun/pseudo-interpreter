DECLARE arr : ARRAY[1:10] OF REAL
DECLARE arr2 : ARRAY[-99 : -90] OF INTEGER

FOR i <- 1 TO 10
    arr[i] <- RANDOM() * 50
    arr2[i - 100] <- arr[i]
NEXT i


FOR i <- 0 TO 9
    OUTPUT arr[i + 1]
    OUTPUT arr2[i - 99]
NEXT i

DECLARE singleElArr : ARRAY[0:0] OF STRING

singleElArr[0] <- "hello"
OUTPUT singleElArr[0]

DECLARE intArr : ARRAY[0:1] OF INTEGER
intArr[0] <- 1
OUTPUT intArr[0]


DECLARE Arr2D : ARRAY[1:5, 1:5] OF INTEGER
DECLARE Arr3D : ARRAY[1:5, 0:4, 2:6] OF INTEGER

FOR i <- 1 TO 5
    FOR j <- 1 TO 5
        Arr2D[i, j] <- i + j
        FOR k <- 2 TO 6
            Arr3D[i, j-1, k] <- i + (j-1) - k
        NEXT k
    NEXT j
NEXT i

FOR i <- 1 TO 5
    FOR j <- 1 TO 5
        OUTPUT "Arr2D[" & i & ", " & j & "]: " & Arr2D[i, j]
    NEXT j
NEXT i

FOR i <- 1 TO 5
    FOR j <- 0 TO 4
        FOR k <- 2 TO 6
            OUTPUT "Arr3D[" & i & ", " & j & ", " & k & "]: " & Arr3D[i, j, k]
        NEXT k
    NEXT j
NEXT i