from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback
import time

URL = "https://polarisfood-qa.wposs.com:8443/app_menu/"
USUARIO = "Sonia"
PASSWORD = "710270"


# ==============================
# LOGIN
# ==============================
def login(driver, wait):
    print("🔐 Iniciando sesión...")
    driver.get(URL)

    wait.until(
        EC.presence_of_element_located((By.ID, "id_sc_field_login"))
    ).send_keys(USUARIO)

    driver.find_element(
        By.ID, "id_sc_field_pswd"
    ).send_keys(PASSWORD + Keys.RETURN)

    wait.until(
        EC.presence_of_element_located((By.ID, "item_36"))
    )

    print("✅ Login exitoso")


# ==============================
# VALIDAR MODULO MESAS
# ==============================
def validar_mesas(driver, wait):
    print("\n🟢 Validando módulo MESAS...")

    # Click módulo
    menu_mesas = wait.until(
        EC.element_to_be_clickable((By.ID, "item_87"))
    )
    driver.execute_script("arguments[0].click();", menu_mesas)

    # Verificar iframe
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])
        print("✔ Cambio a iframe realizado")

    # Esperar que aparezcan las salas
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tab"))
    )

    total_salas = len(driver.find_elements(By.CSS_SELECTOR, "div.tab"))
    print(f"✔ Salas activas encontradas: {total_salas}")

    if total_salas == 0:
        raise Exception("❌ No se visualizaron salas activas.")

    # 🔁 Iterar por índice para evitar stale
    for i in range(total_salas):

        # Rebuscar las salas en cada vuelta
        salas = driver.find_elements(By.CSS_SELECTOR, "div.tab")
        sala = salas[i]

        nombre = sala.find_element(By.CSS_SELECTOR, "span.name").text.strip()
        print(f"➡ Validando sala activa: {nombre}")

        driver.execute_script("arguments[0].click();", sala)

        # Esperar que cargue el botón volver (indica que entró a la sala)
        boton_volver = wait.until(
            EC.element_to_be_clickable((By.ID, "sc_volver_top"))
        )

        print(f"✅ Sala {nombre} cargada correctamente")

        # Click en volver
        driver.execute_script("arguments[0].click();", boton_volver)

        # Esperar que reaparezcan las salas antes de continuar
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tab"))
        )

    print("\n🎉 CASO DE PRUEBA VALIDADO CORRECTAMENTE")

# ==============================
# Validar que se visualice el nombre de la sala
# y la cantidad de mesas ocupadas en cada una.
# ==============================

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def validar_nombre_y_mesas_ocupadas(driver, wait):

    print("\n🟢 Validando nombre de sala y mesas ocupadas...")

    # Esperar que existan las salas
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tab"))
    )

    salas = driver.find_elements(By.CSS_SELECTOR, "div.tab")

    if not salas:
        raise Exception("❌ No se encontraron salas.")

    print(f"✔ Salas encontradas: {len(salas)}")

    for sala in salas:

        # Obtener nombre
        nombre = sala.find_element(
            By.CSS_SELECTOR, "span.name"
        ).text.strip()

        # Obtener texto de mesas ocupadas
        texto_ocupadas = sala.find_element(
            By.CSS_SELECTOR, "span.tables-occupy"
        ).text.strip()

        print(f"\n➡ Sala: {nombre}")
        print(f"   Texto mostrado: {texto_ocupadas}")

        # Validar que el nombre no esté vacío
        if not nombre:
            raise Exception("❌ Se encontró una sala sin nombre visible")

        # Validar que el texto no esté vacío
        if not texto_ocupadas:
            raise Exception(f"❌ La sala {nombre} no muestra cantidad de mesas ocupadas")

        # Extraer número de ocupadas
        match = re.search(r"\d+", texto_ocupadas)

        if not match:
            raise Exception(f"❌ No se pudo extraer número de mesas ocupadas en {nombre}")

        numero_ocupadas = int(match.group())

        if numero_ocupadas < 0:
            raise Exception(f"❌ Número inválido en sala {nombre}")

        print(f"   🔴 Mesas ocupadas detectadas: {numero_ocupadas}")
        print("   ✅ Información correcta")

    print("\n🎉 CASO DE PRUEBA VALIDADO CORRECTAMENTE")

# ===============================================
# Validar detalle de mesas en cada sala disponible
# ===============================================

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def validar_mesas_en_todas_las_salas(driver, wait):

    print("\n🟢 Validando mesas en todas las salas disponibles...")

    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tab"))
    )

    # Obtener lista de nombres primero
    salas_elementos = driver.find_elements(By.CSS_SELECTOR, "div.tab")
    nombres_salas = []

    for sala in salas_elementos:
        nombre = sala.find_element(By.CSS_SELECTOR, "span.name").text.strip()
        nombres_salas.append(nombre)

    print(f"✔ Salas encontradas: {len(nombres_salas)}")

    # Iterar por nombre (no por índice)
    for nombre_sala in nombres_salas:

        print(f"\n➡ Ingresando a sala: {nombre_sala}")

        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tab"))
        )

        salas = driver.find_elements(By.CSS_SELECTOR, "div.tab")

        sala_obj = None
        for sala in salas:
            nombre = sala.find_element(By.CSS_SELECTOR, "span.name").text.strip()
            if nombre == nombre_sala:
                sala_obj = sala
                break

        if not sala_obj:
            raise Exception(f"❌ No se encontró la sala {nombre_sala}")

        sala_obj.click()

        # Esperar que carguen las mesas
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card__inner"))
        )

        mesas = driver.find_elements(By.CSS_SELECTOR, "div.card__inner")

        if not mesas:
            raise Exception(f"❌ No se encontraron mesas en {nombre_sala}")

        print(f"   ✔ Mesas encontradas: {len(mesas)}")

        for index, mesa in enumerate(mesas, start=1):

            print(f"\n   🔎 Validando mesa #{index}")

            numero_mesa = mesa.find_element(By.CSS_SELECTOR, ".line1 .sp_vl").text.strip()
            asientos = mesa.find_element(By.CSS_SELECTOR, ".line2 .sp_vl").text.strip()
            hora_pedido = mesa.find_element(By.CSS_SELECTOR, ".line3 .sp_vl").text.strip()
            precio_total = mesa.find_element(By.CSS_SELECTOR, ".line5 .sp_vl").text.strip()

            print(f"      🪑 Mesa: {numero_mesa}")
            print(f"      👥 Asientos: {asientos}")
            print(f"      ⏰ Hora: {hora_pedido}")
            print(f"      💲 Total: {precio_total}")

            # =========================
            # VALIDACIONES FLEXIBLES
            # =========================

            # Número obligatorio y numérico
            if not numero_mesa:
                raise Exception(f"❌ Número de mesa no visible en {nombre_sala}")

            if not re.match(r"^\d+$", numero_mesa):
                raise Exception(f"❌ Número inválido en mesa {numero_mesa}")

            # Asientos debe contener al menos un número (ej: 4 o 4 / 4)
            if not re.search(r"\d+", asientos):
                raise Exception(f"❌ Asientos inválidos en mesa {numero_mesa}")

            # Hora solo se valida si existe (mesa con pedido)
            if hora_pedido:
                if not re.match(r"^\d{2}:\d{2}$", hora_pedido):
                    raise Exception(f"❌ Formato de hora inválido en mesa {numero_mesa}")

            # Precio solo se valida si existe
            if precio_total:
                if not re.search(r"\d", precio_total):
                    raise Exception(f"❌ Precio inválido en mesa {numero_mesa}")

            # Comentarios opcionales
            comentarios = mesa.find_elements(By.CSS_SELECTOR, ".line4 .sp_vl")

            if comentarios:
                texto_comentario = comentarios[0].text.strip()
                print(f"      📝 Comentario: {texto_comentario}")
            else:
                print("      📝 Sin comentarios")

            print("      ✅ Mesa validada correctamente")

        print(f"\n   ✅ Sala {nombre_sala} validada correctamente")

    print("\n🎉 TODAS LAS SALAS FUERON VALIDADAS CORRECTAMENTE")




# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)

    try:
        login(driver, wait)
        validar_mesas(driver, wait)
        validar_nombre_y_mesas_ocupadas(driver, wait)
        validar_mesas_en_todas_las_salas(driver, wait)

    except TimeoutException:
        print("⏰ Tiempo de espera agotado.")
        traceback.print_exc()

    except Exception as e:
        print(f"⚠ Error: {e}")
        traceback.print_exc()

    finally:
        input("\nPresiona Enter para cerrar el navegador...")
        driver.quit()
