from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

URL = "https://polarisfood-qa.wposs.com:8443/app_menu/"
USUARIO = "TU_USUARIO"
PASSWORD = "TU_PASSWORD"

driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    # ==============================
    # LOGIN
    # ==============================
    driver.get(URL)

    wait.until(
        EC.presence_of_element_located((By.ID, "id_sc_field_login"))
    ).send_keys(USUARIO)

    driver.find_element(
        By.ID, "id_sc_field_pswd"
    ).send_keys(PASSWORD + Keys.RETURN)

    wait.until(EC.url_changes(URL))
    print("✅ Login exitoso")

    time.sleep(2)

    # ==============================
    # CLICK EN CLIENTES
    # ==============================
    wait.until(
        EC.element_to_be_clickable((By.ID, "item_37"))
    ).click()

    print("✅ Click en Clientes")

    # ==============================
    # CAMBIAR AL IFRAME
    # ==============================
    wait.until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "app_menu_iframe"))
    )

    print("✅ Dentro del iframe app_menu_iframe")

    # ==============================
    # CLICK EN EDITAR
    # ==============================
    wait.until(
        EC.element_to_be_clickable((By.ID, "bedit"))
    ).click()

    print("✅ Click en Editar")

    # Esperar formulario
    wait.until(
        EC.presence_of_element_located((By.ID, "id_sc_field_customer_num_doc"))
    )

    print("✅ Formulario cargado")

    # ==============================
    # VALIDACIÓN
    # ==============================
    print("🔎 Validando que Número de documento NO sea editable...")

    try:
        readonly_span = driver.find_element(By.ID, "id_read_on_customer_num_doc")
        edit_span = driver.find_element(By.ID, "id_read_off_customer_num_doc")
        input_field = driver.find_element(By.ID, "id_sc_field_customer_num_doc")

        is_readonly_visible = readonly_span.is_displayed()
        is_edit_span_visible = edit_span.is_displayed()
        is_input_visible = input_field.is_displayed()

        if is_readonly_visible and not is_edit_span_visible and not is_input_visible:
            print("✅ PASÓ: El campo Número de documento NO es editable")
            print("📄 Valor mostrado:", readonly_span.text)
        else:
            print("❌ FALLÓ: El campo está en modo editable")

    except NoSuchElementException as e:
        print("❌ FALLÓ: No se encontraron todos los elementos esperados.")
        print("Detalle:", e)

except Exception as e:
    print("❌ Error general:", e)

finally:
    input("\nPresiona Enter para cerrar el navegador...")
    driver.quit()
