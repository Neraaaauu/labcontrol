# Guion de la demostración en vivo — LabControl

**Duración:** 5 a 7 minutos · **Participan los dos** (la guía lo exige)

---

## ✅ Antes de empezar (10 min antes)

1. Abre la terminal en la carpeta del proyecto y activa el entorno: `source .venv/bin/activate`
2. Reinicia los datos de prueba: borra `instance/labcontrol.db` y corre `./run.sh`
3. Abre `http://127.0.0.1:5000` en el navegador.
4. Ten una **segunda terminal** lista en la carpeta del proyecto (para pruebas y rendimiento).
5. Mac: si sale "403 Forbidden", apaga el **Receptor AirPlay** (ver README).

> 💡 Ten este guion impreso o en otra pantalla.

---

## 🎬 La demo, paso a paso

| # | Quién | Qué hace en pantalla | Qué dice (idea, no de memoria) | Tiempo |
| :-: | :-- | :-- | :-- | :-: |
| 1 | **Gareth** | Inicia sesión como `recepcion` / `recepcion123` | "Entramos como recepción, uno de los 4 roles." | 0:30 |
| 2 | **Gareth** | `Pacientes → Registrar Paciente`. Escribe CURP inventada y C.P. `22000` | "Al poner el código postal, la **API externa** llena estado, municipio y colonias. Si la API falla, hay respaldo y se puede escribir a mano." | 1:00 |
| 3 | **Gareth** | Guarda. *(Opcional: intenta guardar la misma CURP otra vez para mostrar el mensaje de error)* | "Valida la CURP y no deja duplicados." | 0:30 |
| 4 | **Gareth** | En la ficha: `Nueva Orden de Estudio`, marca 2 estudios, confirma | "El total se calcula solo y se genera un folio único." | 0:45 |
| 5 | **Gareth** | Pulsa **Marcar Muestra Recibida** | "La orden avanza. El sistema no deja completarla si no hay muestra." | 0:20 |
| 6 | **Adrián** | Cierra sesión. Entra como `quimico` / `quimico123`. Abre la orden, **Iniciar Análisis** y captura resultados | "Ahora el químico: un rol distinto, con otras acciones." | 0:45 |
| 7 | **Adrián** | Cierra sesión. Entra como `doctor` / `doctor123`. Escribe el dictamen y firma | "El médico firma y la orden queda Completada." | 0:30 |
| 8 | **Adrián** | Cierra sesión. En la página de inicio escribe el folio de la orden | "El paciente consulta sus resultados con el folio, sin cuenta." | 0:30 |
| 9 | **Adrián** | En la terminal: `python3 -m pytest -v` | "17 pruebas, todas pasan. En 5 comprobamos que fallan si quitamos la regla." | 0:30 |
| 10 | **Gareth** | En la terminal: `python3 scripts/benchmark_performance.py` | "Medimos la consulta de una orden: antes 5 consultas, ahora 1 con JOIN e índices; unas 2.5–3 veces más rápida." | 0:30 |

**Total ≈ 6 minutos**

---

## 🆘 Si algo sale mal

| Pasa esto | Hagan esto |
| :-- | :-- |
| La API de C.P. no llena nada (sin internet) | Usen `22000` o `22400`: están en el respaldo. Díganlo como ventaja: "por eso pusimos respaldo". |
| No recuerdan el folio | Usen el folio demo `ORD-2026-1001`. |
| Se traba el servidor | `Ctrl + C` y otra vez `./run.sh`. |
| El profe pregunta algo del código | Respiren. Abran `app.py` y busquen la ruta (`Cmd + F`). Expliquen con sus palabras qué hace. |

---

## ❓ Preguntas probables del profe (y una respuesta corta)

- **¿Por qué Flask?** Es ligero, en Python y fácil de entender para un MVP.
- **¿Qué pasa si la API externa falla?** Tiene 2.5 s de espera; si no responde, usa un respaldo local y el formulario sigue editable.
- **¿Qué hizo la IA y qué hicieron ustedes?** Claude ayudó a programar y documentar; nosotros corrimos las pruebas, probamos el flujo con los 4 roles y comprobamos que las pruebas detectan errores.
- **¿Cómo mejoraron el rendimiento?** Juntamos 5 consultas en 1 con JOIN y agregamos índices a las columnas que se buscan.
- **¿Qué roles hay?** Admin, recepción, químico y médico (la guía pedía 2).
