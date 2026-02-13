from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback

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
# VALIDACIÓN VISUAL
# ==============================
def validar_monitor_cocina(driver, wait):
    print("\n🔎 Navegando a Monitor de cocina...")

    wait.until(
        EC.element_to_be_clickable((By.ID, "item_36"))
    ).click()

    wait.until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "app_menu_iframe"))
    )

    print("✅ Dentro del Monitor de Cocina")
    print("\n🧪 Ejecutando validación visual")

    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-id-orden]"))
        )

        ordenes = driver.find_elements(By.CSS_SELECTOR, "[data-id-orden]")

        if len(ordenes) == 0:
            raise Exception("❌ No hay pedidos confirmados visibles.")

        print(f"✅ Pedidos encontrados: {len(ordenes)}")

        for orden in ordenes:
            pedido = orden.get_attribute("data-id-orden")
            mesa = orden.get_attribute("data-mesa")
            sala = orden.get_attribute("data-lugar-mesa")

            print("\n-----------------------------------")
            print(f"📦 Pedido: {pedido}")
            print(f"🪑 Mesa: {mesa}")
            print(f"🏢 Sala: {sala}")

            productos = orden.find_elements(By.CLASS_NAME, "item-orden")
            print(f"🧾 Productos: {len(productos)}")

            for producto in productos:
                nombre = producto.find_element(By.CLASS_NAME, "nombre").text
                estado = producto.find_element(By.CLASS_NAME, "estado").text

                print(f"   ✔ Producto: {nombre}")
                print(f"   🔄 Estado: {estado}")

        print("\n🎉 VALIDACIÓN VISUAL EXITOSA")

    except TimeoutException:
        raise Exception("❌ El monitor no muestra pedidos confirmados.")


# ==============================
# VALIDACIÓN CAMBIO DE ESTADOS
# ==============================
def validar_cambio_estados(driver, wait):
    print("\n🔄 Validando cambio de estados")

    # Re-obtener ordenes
    ordenes = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-id-orden]"))
    )
    if len(ordenes) == 0:
        raise Exception("❌ No hay pedidos para validar cambio de estado.")

    orden = ordenes[0]
    pedido = orden.get_attribute("data-id-orden")
    print(f"\n📦 Probando cambios en Pedido: {pedido}")

    # Secuencia de estados a probar
    secuencia_estados = [
        ("EN PREPARACIÓN", "preparacion"),
        ("REQUERIDO", "requerido"),
        ("LISTO", "listo")
    ]


    # ======================
    # CASO 2: Cambiar solo productos seleccionados
    # ======================
    print("\n🟡 CASO 2: Cambiar solo productos seleccionados")

    # Deseleccionar todos primero
    checkboxes = orden.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    for checkbox in checkboxes:
        if checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)

    # Seleccionar solo los primeros 2 productos
    seleccionados = checkboxes[:2]
    for checkbox in seleccionados:
        driver.execute_script("arguments[0].click();", checkbox)

    for texto_boton, clase_esperada in secuencia_estados:
        print(f"\n➡ Cambiando estado a: {texto_boton} (productos seleccionados)")

        boton = orden.find_element(By.XPATH, f".//button[contains(text(), '{texto_boton}')]")
        driver.execute_script("arguments[0].click();", boton)

        # Re-obtener elementos
        orden = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"[data-id-orden='{pedido}']"))
        )
        estados = orden.find_elements(By.CLASS_NAME, "estado")

    # ======================
    # CASO 1: Cambiar todos los productos
    # ======================
    print("\n🟢 CASO 1: Cambiar todos los productos a un estado")

    checkboxes = orden.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    for checkbox in checkboxes:
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)

    for texto_boton, clase_esperada in secuencia_estados:
        print(f"\n➡ Cambiando estado a: {texto_boton} (todos los productos)")

        boton = orden.find_element(By.XPATH, f".//button[contains(text(), '{texto_boton}')]")
        driver.execute_script("arguments[0].click();", boton)

        # Re-obtener orden y estados después del cambio de DOM
        orden = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"[data-id-orden='{pedido}']"))
        )
        estados = orden.find_elements(By.CLASS_NAME, "estado")

        for estado in estados:
            texto_actual = estado.text.strip()
            clase_actual = estado.get_attribute("class").lower()
            if clase_esperada not in clase_actual or texto_boton not in texto_actual:
                raise Exception(
                    f"❌ Error al actualizar todos los productos. Esperado: {texto_boton}/{clase_esperada} | Actual: {texto_actual}/{clase_actual}"
                )

        print(f"   ✔ Todos los productos cambiaron correctamente a: {texto_boton}")

    

        for i, estado in enumerate(estados):
            texto_actual = estado.text.strip()
            clase_actual = estado.get_attribute("class").lower()
            if i < len(seleccionados):  # productos seleccionados
                if clase_esperada not in clase_actual or texto_boton not in texto_actual:
                    raise Exception(
                        f"❌ Error en producto seleccionado {i+1}. Esperado: {texto_boton}/{clase_esperada} | Actual: {texto_actual}/{clase_actual}"
                    )
            else:  # productos no seleccionados no deben cambiar
                if texto_boton in texto_actual or clase_esperada in clase_actual:
                    raise Exception(f"❌ Producto no seleccionado cambió de estado! Producto {i+1}")

        print(f"   ✔ Cambio de estado aplicado correctamente a productos seleccionados: {texto_boton}")

    print("\n🎉 CAMBIO DE ESTADOS VALIDADO CORRECTAMENTE")



# ==============================
# MAIN
# ==============================
def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        login(driver, wait)
        validar_monitor_cocina(driver, wait)
        validar_cambio_estados(driver, wait)

        print("\n🏁 PRUEBA COMPLETA EXITOSA")

    except Exception:
        print("\n🚨 ERROR EN LA EJECUCIÓN:")
        traceback.print_exc()

    finally:
        input("\nPresiona Enter para cerrar el navegador...")
        driver.quit()


if __name__ == "__main__":
    main()
