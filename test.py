opciones = ["1"]
op = input("elegi 1:hola , 2:chau: ")

def agregar(op):
    def asd(op):
        if op == "1":
            opciones.append("hola")
        
        elif op == "2":
            opciones.append("chau")
        else:
            return None
    
agregar(op)
print(opciones)