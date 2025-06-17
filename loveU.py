import math
from turtle import *

def heart1(M):
    return 15 * math.sin(M) ** 3

def heart2(M):
    return 12 * math.cos(M) - 5 * math.cos(2 * M) - 2 * math.cos(3 * M) - math.cos(4 * M)

speed(0)  # Velocità massima
bgcolor("black")
color("red")
penup()

# Disegna subito il cuore completo
for i in range(1000):
    M = i / 100 * math.pi
    goto(heart1(M) * 18, heart2(M) * 18)
    pendown()

# Scrive il messaggio al centro del cuore
penup()
goto(-90, -10)  # Posizione centrale
color("white")
write("emma sei mia", align="left", font=("Arial", 16, "bold"))

done()
