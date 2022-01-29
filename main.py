#!/bin/python

from random import randint

class Celda:
    def __init__(self, posicion: (int, int), esMina: bool = False, minasAlrededor: int = 0, visible: bool = False):
        self.posicion = posicion
        self.esMina = esMina
        self.minasAlrededor = minasAlrededor
        self.visible = visible
        self.tieneBandera = False

    def setMinas(self, minas: int) -> None:
        self.minasAlrededor = minas

    def toggleBandera(self) -> None:
        self.tieneBandera = not self.tieneBandera

    def setVisible(self, visible: bool) -> None:
        self.visible = visible

class Tablero:
    def __init__(self, filas: int, columnas: int, minas: int):
        self.filas = filas
        self.columnas = columnas
        self.minas = minas
        self.celdas = None
        self.banderas = 0
        self.visibles = 0
        self.explotado = None

    def setVisibilidad(self, fila: int, columna: int, visibilidad: bool = True) -> None:
        celda = self.celdas[fila][columna]
        if visibilidad and not celda.visible:
            self.visibles += 1
        celda.setVisible(visibilidad)

    def toggleBandera(self, fila: int, columna: int) -> None:
        celda = self.celdas[fila][columna]
        if celda.visible:
            return

        if celda.tieneBandera:
            celda.tieneBandera = False
            self.banderas -= 1
        else:
            celda.tieneBandera = True
            self.banderas += 1

def submatriz(tablero: Tablero, fila: int, columna: int) -> (int, int, int, int):
    inicio_fila = fila - 1 if fila > 0 else fila
    inicio_columna = columna - 1 if columna > 0 else columna
    fin_fila = fila + 1 if fila < len(tablero.celdas)-1 else fila
    fin_columna = columna + 1 if columna < len(tablero.celdas[0])-1 else columna

    return inicio_fila, inicio_columna, fin_fila, fin_columna

def minas_alrededor(tablero: Tablero, fila: int, columna: int) -> int:
    inicio_fila, inicio_columna, fin_fila, fin_columna = submatriz(tablero, fila, columna)

    minas = 0
    for i in range(inicio_fila, fin_fila+1):
        for j in range(inicio_columna, fin_columna+1):
            if tablero.celdas[i][j].esMina:
                minas += 1
    return minas

def banderas_alrededor(tablero: Tablero, fila: int, columna: int) -> int:
    inicio_fila, inicio_columna, fin_fila, fin_columna = submatriz(tablero, fila, columna)

    banderas = 0
    for i in range(inicio_fila, fin_fila+1):
        for j in range(inicio_columna, fin_columna+1):
            if tablero.celdas[i][j].tieneBandera:
                banderas += 1

    return banderas

def inicializar_juego(filas: int, columnas: int, minas: int) -> Tablero:
    posicionesMinas = []
    for i in range(minas):
        ocupada = True
        while ocupada:
            posicion = (randint(0, filas-1), randint(0, columnas-1))
            ocupada = posicion in posicionesMinas
        posicionesMinas += [posicion]

    tablero = Tablero(filas, columnas, minas)
    tablero.celdas = []
    for i in range(filas):
        tablero.celdas += [[]]
        for j in range(columnas):
            if (i, j) in posicionesMinas:
                tablero.celdas[i] += [Celda((i, j), True)]
            else:
                tablero.celdas[i] += [Celda((i, j))]

    for i in range(filas):
        for j in range(columnas):
            tablero.celdas[i][j].setMinas(minas_alrededor(tablero, i, j))

    return tablero

def expandir_cero(tablero: Tablero, fila: int, columna: int) -> None:
    if tablero.celdas[fila][columna].minasAlrededor != 0:
        return

    inicio_fila, inicio_columna, fin_fila, fin_columna = submatriz(tablero, fila, columna)

    for i in range(inicio_fila, fin_fila+1):
        for j in range(inicio_columna, fin_columna+1):
            if not tablero.celdas[i][j].visible:
                tablero.setVisibilidad(i, j)
                if tablero.celdas[i][j].minasAlrededor == 0:
                    expandir_cero(tablero, i, j)

def expandir_visible(tablero: Tablero, fila: int, columna: int) -> bool:
    if tablero.celdas[fila][columna].minasAlrededor != banderas_alrededor(tablero, fila, columna):
        return True

    inicio_fila, inicio_columna, fin_fila, fin_columna = submatriz(tablero, fila, columna)

    success = True
    for i in range(inicio_fila, fin_fila+1):
        for j in range(inicio_columna, fin_columna+1):
            celda = tablero.celdas[i][j]
            if not celda.visible and not celda.tieneBandera:
                tablero.setVisibilidad(i, j)
                expandir_cero(tablero, i, j)
                if celda.esMina:
                    tablero.explotado = celda
                    succes = False

    return success

def mostrar_ayuda() -> None:
    print("Esta es la ayuda")

def imprimir_tablero(tablero: Tablero, mostrarMinas: bool = False) -> None:
    print("   ", end = "")
    for i in range(len(tablero.celdas[0])):
        print(" {columna:0>2} ".format(columna = i), end = "")
    print("")

    for i, fila in enumerate(tablero.celdas):
        print("{}: ".format(i), end = "")
        for celda in fila:
            valor = " " + str(celda.minasAlrededor)
            if celda.tieneBandera:
                valor = "🚩"
            elif celda == tablero.explotado:
                valor = "💥"
            elif celda.esMina and mostrarMinas:
                valor = "💣"
            elif not celda.visible:
                valor = "🟫"
            elif celda.minasAlrededor == 0:
                valor = "  "
            print("[{}]".format(valor), end = "")
        print("")
    print("Minas restantes: {}".format(tablero.minas - tablero.banderas))

def realizar_jugada(tablero: Tablero) -> int:
    movimiento = input("Movimiento (f al principio para bandera): ")

    if movimiento == "help":
        mostrar_ayuda()
        return 0
    elif movimiento == "quit" or movimiento == "exit":
        return -2

    bandera = False
    if movimiento[0] == "f":
        bandera = True
        movimiento = movimiento[1:]

    try:
        fila, columna = movimiento.split(",")
        fila, columna = int(fila), int(columna)
        celda = tablero.celdas[fila][columna]
    except:
        print("Entrada inválida.")
        return 0

    if bandera:
        tablero.toggleBandera(fila, columna)
        return 0

    if celda.tieneBandera:
        return 0

    if celda.visible and not expandir_visible(tablero, fila, columna):
            return -1

    expandir_cero(tablero, fila, columna)
    tablero.setVisibilidad(fila, columna)

    if celda.esMina and not bandera:
        tablero.explotado = celda
        return -1

    if tablero.visibles + tablero.banderas == tablero.filas * tablero.columnas:
        return 1

    return 0

if __name__ == "__main__":
    estado = 0
    tablero = inicializar_juego(10, 20, 15)

    while estado == 0:
        imprimir_tablero(tablero)
        estado = realizar_jugada(tablero)

    if estado == -1:
        imprimir_tablero(tablero, True)
        print("Perdiste :(")
    elif estado == 1:
        imprimir_tablero(tablero)
        print("Ganaste :D")
    elif estado == -2:
        print("Saliendo...")
