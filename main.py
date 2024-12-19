import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import requests

class Ventana_inicio_sesion:
    def __init__(self,root):
        self.root = root
        self.root.title('Inicio de sesion - Sistema de AFIP')
        self.root.geometre("400x250")
        self.cuil = tk.StringVar()
        self.contraseña = tk.StringVar()
        self.crear_interfaz()
    

    def crear_interfaz(self):
        "sirve para crear la interfaz de inicio de sesión"
        ttk.Label(self.root , text="Inicio de Sesión" , font=("Arial", 16)).pack(pady=10)
        #cuil
        ttk.Label(self.root, text="CUIL:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.cuil, width=30).pack(pady=5)
        #contraseña
        ttk.Label(self.root, text="Contraseña:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.contraseña, width=30, show="*").pack(pady=5)
        #iniciar sesión 
        ttk.Button(self.root, text="Iniciar Sesión", command=self.iniciar_sesion).pack(pady=20)#botón que ejecuta la funcion iniciar_sesión
        return self.cuil

    def obtener_cuil(self):
        """Devuelve el CUIL ingresado, se utiliza en "ventanaPrincipal"""
        return self.cuil.get()
       
    def iniciar_sesion(self):
        """Realiza el inicio de sesión con múltiples pasos en el sistema AFIP."""
        driver = webdriver.Chrome(executable_path="/ruta/a/chromedriver")
        
        try:
            # ANTES DE TOD0 INICIO DE SESIÓN
            #SE VALIDA LA MANERA EN LA QUE INGRESARON LOS DATOS, SI HAY O NO CUIL, LO MISMO CON LA CONTRASEÑA 
            #SE VALIDAN LOS DATOS INGRESADOS CON LAS APIs de AFIP, SI EXISTEN O NO 

            print("Iniciando sesión...")

            # SE LLEVAN A CABO EN LA PÁGINA WEB DE AFIP UNA VEZ YA TOD0 VALIDADO
            driver.get("https://www.afip.gob.ar/")# va a la pagina de afip
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Iniciar Sesión"))# espera a que esté el texto "inciar sesión" y hace click
            ).click()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "F1:username")))# espera a que este el id f1:username
            driver.find_element(By.ID, "F1:username").send_keys(self.cuil) # envía a ese campo f1:username el CUIL ingresado previamente
            driver.find_element(By.ID, "F1:btnSiguiente").click()  #hace click en el botón con el id f1:btnsiguiente 

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "F1:password")))# espera a que este el id f1:password
            driver.find_element(By.ID, "F1:password").send_keys(self.contraseña)# envía a ese campo f1:password la contraseña ingresada previamente
            driver.find_element(By.ID, "F1:btnIngresar").click()  # Botón "Iniciar Sesión"

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Más utilizados')]")))#verifica que el incio fue correcto

            # PASOS A REALIZAR EN LA APLICACIÓN UNA VEZ YA TOD0 VALIDADO
            messagebox.showinfo("Inicio de Sesión exitoso")
            self.root.destroy()  # Cierra la ventana actual de inicio de sesión
            self.abrir_ventana_principal() # sirve para abrir la pestaña de poenr las empresas y eso
            return driver

        except Exception as e:
            print(f"Error durante el inicio de sesión: {e}")
            driver.quit()
            return None

    def abrir_ventana_seleccion(self,driver):
        ventana_seleccion = VentanaSeleccion(self.root, driver, self.obtener_cuil())
        # ventana_seleccion.title = ("Ventana principal")
        # ventana_seleccion.geometry("600x400")
        # ttk.Label(ventana_seleccion, text="Bienvenido al Sistema AFIP", font=("Arial", 16)).pack(pady=50)

class VentanaSeleccion():
    def __init__(self,root,driver,cuil):
        self.root = tk.Toplevel(root)#ventana principal
        self.driver = driver #pagina
        self.root.title("Bienvenido al Sistema AFIP", font=("Arial", 16)).pack(pady=50)
        self.root.geometry("600x400")
        #serivicios
        self.servicio = tk.StringVar()
        self.lista_servicios = []
        self.servicio_seleccionado = None#inicializa vacío pq aún no hay anda seleccionado
        #empresas
        self.empresa = tk.StringVar()
        
        self.cuil=cuil
        self.crear_interfaz()
    
    def crear_interfaz(self):

        #SERVICIOS 
    
        def filtrar_servicios(event,servicios_x_cuil):
            texto_servicio = entrada_servicio.get().lower()
            lista_servicios.delete(0, tk.END)
            for servicio in servicios_x_cuil:  # Usar la lista ya obtenida de la función obtener_servicios . Solo filtra entre los servicios que ese cuil tiene
                if texto_servicio in servicio.lower():
                    lista_servicios.insert(tk.END, servicio)
            
        
        def obtener_servicios(cuil):
            """Consulta la base de datos para obtener los servicios del usuario."""
            conexion = sqlite3.connect('mi_base_de_datos.db')  # Conéctate a tu base de datos
            cursor = conexion.cursor()

            # Consulta las opciones para el usuario específico
            consulta_a_db = "SELECT servicio FROM servicios WHERE usuario_id = ?"#reveer esto
            cursor.execute(consulta_a_db, (cuil,))
            servicios = [fila[0] for fila in cursor.fetchall()]  # Convierte el resultado a una lista

            conexion.close()#cierra la conexión con la base 
            return servicios

        def registrar_seleccion_servicio(event):
            servicio_seleccionado = lista_servicios.get(lista_servicios.curselection())
            print(f"Servicio seleccionado: {servicio_seleccionado}")
            self.servicio_seleccionado = servicio_seleccionado#se asigna el valor de la selección al atributo servicio_selccionado para poder implementarlo luego


        ttk.Label(self.root, text="Seleccionar servicio y empresa", font= ("Arial",16)).pack(pady=10)#ver que parametros solicita ttk.Label
        #servicio
        servicios_x_cuil= self.obtener_servicios(self.cuil)
        ttk.Label(self.root, text="Servicio:").pack(pady=5)
        entrada_servicio = ttk.Entry(self.root, width=30)
        entrada_servicio.pack(pady=5) 
        entrada_servicio.bind("<KeyRelease>", lambda event: filtrar_servicios(servicios_x_cuil))
        """
        Bind --> sirve para relación una función cuando ocurra cierto evento, en este caso relaciona filtrar_Servicios con keyrelease (cuando se deja de presionar una tecla)
        lambda event --> sirve para que la fx no se ejecute directamente, sino que solo cuando ocurra el evento, si no existe lambda la fx se ejecuta automáticamente sin esperar a que ocurra el evento. Lambda viene a ser una fx anonima que toma como parametros event:... 
        """
        lista_servicios = tk.Listbox(self.root, width=30, height=5)# listbox es un elemento de tkinter, es una lista con la q los usuarios pueden interactuar. Self.root indica la ventana principal
        lista_servicios.pack(pady=5)#pack es para posicionar el contendor dentro de la ventana, pady es como el padding
        lista_servicios.bind("<<ListboxSelect>>", registrar_seleccion_servicio)
        
        
        #empresa (en función del servicio elegido)
        
        
        def obtener_empresas(usuario_id,servicio_seleccionado):
            """Consulta la base de datos para obtener las empresas asociadas al usuario."""
            conexion = sqlite3.connect('mi_base_de_datos.db')  # Conexión a la base de datos
            cursor = conexion.cursor()

            
            consulta_a_db = """
            SELECT nombre_empresa 
            FROM empresas 
            WHERE usuario_id = ? , servicio_selecionado = ?
            """# Consulta las empresas asociadas al usuario
            cursor.execute(consulta_a_db, (usuario_id,servicio_seleccionado))
            empresas = [fila[0] for fila in cursor.fetchall()]
            """
            cursor.fetchall --> recupera todos los resultados de la consulta y hace una lista de tuplas, cada tupla tendrá solo nombre_empresa
            fila[0] --> como cada valor de la lista es una tupla, con fila[0] indicamos que accedemos al valor 0 (y único) de la tupla
            empresas --> será igual a una lista que albergará en sus posiciones el nombre de cada empresa
            """

            conexion.close()
            return empresas
        
        
        
        ttk.Label(self.root, text="Empresa:").pack(pady=5)
        ttk.Entry(self.root,  width=30, show="*").pack(pady=5)#esto no tiene que ser textvariable pq van a seleccioanr de una lista desplegable de la cual van a poder ir escribiendo
        
        
        #me faltan dos selecciones mas para llegar a la parte de poner fecha_inicio y fecha_fin
        


#EMPRESAS
def obtener_empresas(usuario_id):
    """Consulta la base de datos para obtener las empresas asociadas al usuario."""


    conexion = sqlite3.connect('mi_base_de_datos.db')  # Conexión a la base de datos
    cursor = conexion.cursor()

    
    consulta_a_db = "SELECT nombre_empresa FROM empresas WHERE usuario_id = ?"# Consulta las empresas asociadas al usuario
    cursor.execute(consulta_a_db, (usuario_id,))
    empresas = [fila[0] for fila in cursor.fetchall()]  # Convierte el resultado a una lista

    conexion.close()
    return empresas

def seleccionar_empresa(empresas,opciones):
    """Permite al usuario seleccionar una empresa desde una lista filtrable."""
    def filtrar(event):
        """Filtra la lista en base al texto ingresado."""
        texto = entrada.get().lower()
        lista.delete(0, tk.END)
        for empresa in empresas:
            if texto in empresa.lower():
                lista.insert(tk.END, empresa)

    def seleccionar(event):
        """Obtiene la empresa seleccionada."""
        seleccion = lista.get(lista.curselection())
        print(f"Empresa seleccionada: {seleccion}")
        opciones.append(seleccion)
        ventana.destroy()  # Cierra la ventana
        return seleccion

    ventana = tk.Toplevel()  # Crear ventana
    ventana.title("Seleccionar Empresa")

    entrada = ttk.Entry(ventana, width=40)# Campo de entrada
    entrada.pack(pady=5)
    entrada.bind("<KeyRelease>", filtrar)  # Filtrar mientras escribe

    # Lista desplegable
    lista = tk.Listbox(ventana, width=40, height=10)
    lista.pack(pady=5)

    # Llenar la lista con todas las empresas al inicio
    for empresa in empresas:
        lista.insert(tk.END, empresa)

    lista.bind("<<ListboxSelect>>", seleccionar)  # Seleccionar una empresa

    ventana.mainloop()


def ingresar_parametros():
    """Solicita los parámetros necesarios para la consulta."""
    
    print("\nIngrese los parámetros para la consulta:")

    # Fecha de inicio (obligatoria)
    fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ")

    # Fecha de fin (obligatoria)
    fecha_fin = input("Fecha de fin (YYYY-MM-DD): ")

    # COE (opcional)
    coe = input("COE (opcional, presione Enter para omitir): ")

    # CUIT Emisor (opcional)
    cuit_emisor = input("CUIT Emisor (opcional, presione Enter para omitir): ")

    # Devuelve los parámetros con los opcionales en None si no se ingresan
    return fecha_inicio, fecha_fin, coe or None, cuit_emisor or None

def descargar_pdfs(driver, parametros, opciones):
    """
    Realiza la navegación por las páginas basándose en las opciones seleccionadas
    y descarga los PDFs en la ruta final.
    
    parametros: tuple -> Contiene (fecha_inicio, fecha_fin, coe, cuit_emisor)
    opciones: list -> Lista de opciones seleccionadas por el usuario en cada nivel.
    """
    fecha_inicio, fecha_fin, coe, cuit_emisor = parametros

    try:
        print("\nIniciando la navegación para descargar los PDFs...")

        # Paso 1: Navegar por cada nivel según las opciones seleccionadas
        for nivel, opcion in enumerate(opciones):
            print(f"Accediendo a la opción {nivel + 1}: {opcion}")

            # Encontrar y hacer clic en la opción actual
            # (Reemplaza este XPath por el identificador adecuado para tu caso)
            elemento_opcion = driver.find_element(By.XPATH, f"//a[contains(text(), '{opcion}')]")
            elemento_opcion.click()

            # Esperar que la página cargue antes de continuar al siguiente nivel
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Título de la Página')]"))
            )
        
        # Paso 2: Establecer los filtros basados en los parámetros
        print("Aplicando filtros...")
        # Ingresa las fechas en los campos correspondientes
        campo_fecha_inicio = driver.find_element(By.NAME, "fechaStr")
        campo_fecha_inicio.send_keys(fecha_inicio)

        campo_fecha_fin = driver.find_element(By.NAME, "fechaHastaStr")
        campo_fecha_fin.send_keys(fecha_fin)

        # Si se proporciona, ingresa el COE
        if coe:
            campo_coe = driver.find_element(By.NAME, "codOperacionStr")
            campo_coe.send_keys(coe)

        # Si se proporciona, ingresa el CUIT emisor
        if cuit_emisor:
            campo_cuit_emisor = driver.find_element(By.NAME, "cuitStr")
            campo_cuit_emisor.send_keys(cuit_emisor)

        # Aplicar los filtros (por ejemplo, hacer clic en el botón de búsqueda)
        boton_buscar = driver.find_element(By.XPATH, "//input[@value= 'btnBuscar']")
        boton_buscar.click()

        # Esperar que aparezcan los resultados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME , "liquidacionForm"))
        )

        # Paso 3: Buscar y descargar los PDFs
        print("Buscando PDFs para descargar...")
        enlaces_pdf = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")

        if not enlaces_pdf:
            print("No se encontraron PDFs disponibles.")
        else:
            for enlace in enlaces_pdf:
                url_pdf = enlace.get_attribute("href")
                print(f"Descargando: {url_pdf}")

                # Descargar el PDF usando requests
                response = requests.get(url_pdf, stream=True)
                nombre_archivo = url_pdf.split("/")[-1]

                with open(nombre_archivo, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)

                print(f"Archivo descargado: {nombre_archivo}")

        print("Descarga completada.")
    
    except Exception as e:
        print(f"Error durante la descarga: {e}")



    
def main():
    opciones = []

    print("=== Descargador de PDFs AFIP ===")
    root = tk.TK()#tk.TK sirve para crear una ventana raíz principal independientede las demás ventanas, capaz de albergar nuevos widgets y demás . 
    app = Ventana_inicio_sesion(root)
    # Inicio de sesión
        # driver = iniciar_sesion(usuario, contraseña)
        # if not driver:
        #     print("No se pudo iniciar sesión. Verifique sus credenciales.")
        #     return
    usuario_id = "123"

    ## SERVICIOS
    servicios = obtener_servicios(usuario_id)
    if not servicios:
        print ("No se encontraron servicios para este usuario")
    else:
        seleccionar_servicio(servicios)
    
    #EMPRESAS
    empresas = seleccionar_empresa(usuario_id)
    
    if not empresas:
        print("No se encontraron empresas para este usuario.")
    else:
        seleccionar_empresa(empresas)

    # Seleccionar opciones adicionales
    # opcion = seleccionar_opciones()
    # print(f"Opción seleccionada: {opcion}")

    # Ingresar parámetros de consulta
    parametros = ingresar_parametros()
    print(f"Parámetros ingresados: {parametros}")

    # Descargar PDFs
    descargar_pdfs(driver, opciones,parametros)

    # Cerrar el navegador
    driver.quit()

if __name__ == "__main__":
    main()
