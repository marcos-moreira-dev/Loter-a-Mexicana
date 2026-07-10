# Lienzo detallado — Aplicación Python: **Lotería Mexicana**

## 1. Visión general

Aplicación de escritorio en Python inspirada en el juego tradicional de la **Lotería Mexicana**, diseñada como proyecto didáctico y lúdico con una arquitectura **MVC (Modelo–Vista–Controlador)** deliberadamente clásica, simple y comprensible.

El objetivo principal no es solo “hacer funcionar el juego”, sino construir una base limpia para estudiar:

- separación de responsabilidades
- modelado de dominio
- interfaz gráfica de escritorio
- manejo de estados de juego
- carga de recursos
- validación de reglas
- persistencia básica
- refactorización guiada por IA

La aplicación debe sentirse como un programa pequeño, bien estructurado, autocontenido y fácil de mantener.

---

## 2. Objetivos del proyecto

### 2.1 Objetivo principal
Construir una aplicación de escritorio en Python que permita jugar Lotería Mexicana de manera local, con interfaz amigable, reglas claras y arquitectura ordenada.

### 2.2 Objetivos técnicos

- aplicar **MVC clásico**
- reutilizar la lógica conceptual del proyecto previo en Java
- refactorizar el dominio para que quede más claro y mantenible
- dejar una base adecuada para pruebas unitarias
- trabajar con recursos gráficos de forma organizada
- documentar el proyecto como si fuera un producto serio, aunque sea lúdico

### 2.3 Objetivos personales de estudio

- practicar Python en un proyecto de escritorio real
- estudiar cómo pasar de una solución universitaria inicial a una solución mejor estructurada
- usar IA como apoyo para refactor, no como sustituto del criterio propio
- dejar un repositorio bonito para GitHub

---

## 3. Alcance funcional

La aplicación debe permitir, como mínimo:

- iniciar una partida
- generar o cargar cartones de lotería
- mostrar cartas del mazo una por una
- marcar cartas en el cartón
- verificar victoria
- reiniciar la partida
- mostrar historial de cartas cantadas
- manejar una o varias modalidades simples de juego

No se busca, en la primera versión:

- multijugador en red
- IA avanzada de oponentes
- animaciones complejas
- base de datos grande
- editor avanzado de cartas
- sonidos narrados profesionales

---

## 4. Estilo arquitectónico

## 4.1 Patrón elegido
**MVC (Modelo–Vista–Controlador)**

### Razón de elección
Porque es retro, claro, pedagógico y adecuado para un proyecto pequeño con interfaz y lógica separable.

### Interpretación práctica

- **Modelo**: reglas, entidades, estado del juego
- **Vista**: ventanas, paneles, tablero, cartas, botones, mensajes
- **Controlador**: coordina acciones del usuario, avanza la partida, actualiza la vista a partir del modelo

---

## 5. Dominio del juego

## 5.1 Conceptos centrales

### Carta
Unidad base del juego.

Contiene:
- identificador único
- nombre
- ruta de imagen
- texto descriptivo opcional

### Mazo
Colección de cartas disponibles en una partida.

Responsabilidades:
- almacenar cartas
- barajarlas
- entregar la siguiente carta
- informar si ya no quedan cartas
- permitir reinicio

### Cartón
Tablero del jugador con una selección de cartas.

Responsabilidades:
- contener una matriz o lista visual de cartas
- registrar cuáles fueron marcadas
- verificar estado completo según regla de victoria

### Jugador
Representa a la persona o entidad que participa.

Contiene:
- nombre
- cartón asignado
- estado de victoria
- puntaje opcional

### Partida
Entidad principal del dominio.

Contiene:
- mazo actual
- jugadores
- carta actual cantada
- historial de cartas cantadas
- estado de la partida
- reglas activas

### Regla de victoria
Define cuándo una partida se considera ganada.

Ejemplos:
- cartón completo
- fila completa (si se desea una modalidad simplificada)
- columna completa (opcional)
- patrón especial (muy opcional para el futuro)

---

## 6. Estados del sistema

La aplicación debe manejar estados explícitos.

## 6.1 Estados globales de la app

- inicio
- menú principal
- configuración
- partida en curso
- partida pausada
- resultado final
- ayuda / créditos

## 6.2 Estados de la partida

- no iniciada
- preparada
- en curso
- ganada
- finalizada
- reiniciada

## 6.3 Estado de una carta del cartón

- no marcada
- marcada
- resaltada temporalmente (si coincide con la carta actual)

---

## 7. Reglas funcionales del juego

## 7.1 Inicio de partida
Al iniciar una partida:

- se crea o reinicia el mazo
- se baraja el mazo
- se crean los cartones
- se limpia el historial
- se establece el estado “en curso”

## 7.2 Flujo de canto de cartas
Cada turno:

- el sistema obtiene la siguiente carta del mazo
- actualiza la carta actual visible
- agrega la carta al historial
- resalta coincidencias potenciales en el cartón
- permite marcar manualmente o automáticamente, según configuración

## 7.3 Marcado de cartas
El usuario puede marcar una carta solo si:

- esa carta está en su cartón
- la carta ya fue cantada

El sistema debe impedir marcado inválido.

## 7.4 Verificación de victoria
Cuando corresponda:

- el sistema verifica si el patrón requerido está completo
- si se cumple, se cambia el estado de la partida a “ganada”
- se muestra pantalla o diálogo de victoria

## 7.5 Fin de partida
La partida termina cuando:

- un jugador gana
- o el mazo se acaba
- o el usuario decide reiniciar/salir

---

## 8. Experiencia de usuario

## 8.1 Sensación buscada

- clara
- colorida pero no caótica
- ligeramente nostálgica
- muy entendible
- alegre, sin verse infantil en exceso

## 8.2 Principios visuales

- una carta actual grande y destacada
- cartón legible
- historial visible
- mensajes directos
- botones claros
- retroalimentación inmediata al marcar

## 8.3 Flujo ideal del usuario

1. abrir aplicación
2. entrar al menú principal
3. configurar partida si desea
4. iniciar juego
5. observar la carta actual
6. marcar cartas válidas
7. seguir historial
8. ganar o reiniciar

---

## 9. Pantallas y vistas

## 9.1 Ventana principal / Menú
Debe incluir:

- botón “Nueva partida”
- botón “Configuración”
- botón “Ayuda”
- botón “Créditos”
- botón “Salir”

## 9.2 Vista de partida
Debe incluir:

- carta actual mostrada en grande
- historial de cartas cantadas
- cartón del jugador
- botones de control
- estado textual de la partida
- indicador de victoria o progreso

### Controles sugeridos
- siguiente carta
- marcar carta
- reiniciar partida
- pausar
- volver al menú

## 9.3 Vista de configuración
Opciones sugeridas:

- nombre del jugador
- cantidad de jugadores locales (futuro opcional)
- modalidad de marcado: manual / automático
- velocidad de canto automático (si existiera)
- volumen (si hay audio)
- tema visual básico

## 9.4 Vista de ayuda
Debe explicar:

- qué es la Lotería Mexicana
- cómo jugar en esta aplicación
- qué significan los botones
- cómo se determina la victoria

## 9.5 Vista de resultado final
Debe mostrar:

- mensaje de victoria o derrota
- resumen de la partida
- tiempo transcurrido
- cantidad de cartas cantadas
- opción de reiniciar o volver al menú

---

## 10. Modelo de datos

## 10.1 Clase Carta
Atributos sugeridos:

- `id`
- `nombre`
- `imagen_path`
- `descripcion` (opcional)

## 10.2 Clase Mazo
Atributos sugeridos:

- `cartas`
- `cartas_restantes`
- `cartas_cantadas`

Métodos sugeridos:

- `barajar()`
- `siguiente_carta()`
- `reiniciar()`
- `esta_vacio()`

## 10.3 Clase CasillaCarton o CartaEnCarton
Atributos sugeridos:

- `carta`
- `marcada`

## 10.4 Clase Carton
Atributos sugeridos:

- `casillas`
- `filas`
- `columnas`

Métodos sugeridos:

- `marcar_carta(carta_id)`
- `contiene(carta_id)`
- `esta_completo()`
- `verificar_patron(...)`

## 10.5 Clase Jugador
Atributos sugeridos:

- `nombre`
- `carton`
- `ha_ganado`

## 10.6 Clase Partida
Atributos sugeridos:

- `jugadores`
- `mazo`
- `carta_actual`
- `historial`
- `estado`
- `modo_marcado`
- `regla_victoria`

Métodos sugeridos:

- `iniciar()`
- `avanzar_turno()`
- `marcar(...)`
- `verificar_ganador()`
- `reiniciar()`

---

## 11. Responsabilidades por capa MVC

## 11.1 Modelo
Responsable de:

- almacenar estado del juego
- validar reglas
- decidir si una acción es válida
- determinar victoria
- mantener integridad del dominio

No debe:

- dibujar widgets
- manejar eventos de botones directamente
- depender de detalles visuales

## 11.2 Vista
Responsable de:

- renderizar pantalla
- mostrar cartas, cartones y mensajes
- recolectar interacciones del usuario
- delegar eventos al controlador

No debe:

- decidir reglas del juego
- barajar cartas por su cuenta
- verificar victoria por sí sola

## 11.3 Controlador
Responsable de:

- recibir eventos de la vista
- invocar operaciones del modelo
- pedir a la vista que se actualice
- controlar transiciones de estado
- coordinar el flujo de la partida

---

## 12. Organización del proyecto

```text
loteria_mexicana/
  README.md
  pyproject.toml
  requirements.txt
  .gitignore
  docs/
    arquitectura.md
    roadmap.md
    reglas_del_juego.md
    decisiones/
  assets/
    cards/
    ui/
    sounds/
    fonts/
  src/
    main.py
    model/
      carta.py
      mazo.py
      carton.py
      jugador.py
      partida.py
      reglas.py
    view/
      app_window.py
      main_menu.py
      game_view.py
      settings_view.py
      help_view.py
      result_dialog.py
      widgets/
    controller/
      app_controller.py
      game_controller.py
    infrastructure/
      asset_loader.py
      config_manager.py
      persistence.py
      audio_player.py
    shared/
      constants.py
      enums.py
      errors.py
      utils.py
  tests/
    model/
    controller/
    integration/
```

---

## 13. Requerimientos no funcionales

## 13.1 Legibilidad
El código debe ser fácil de leer para alguien que quiera estudiar el proyecto.

## 13.2 Simplicidad
Evitar sobreingeniería. Si algo puede resolverse con una estructura clara y pequeña, no convertirlo en un framework casero.

## 13.3 Reutilización
Los componentes deben permitir crecer de forma ordenada.

## 13.4 Portabilidad
La aplicación debe poder ejecutarse localmente sin depender de servicios externos.

## 13.5 Trazabilidad didáctica
Debe ser evidente en el repositorio:

- qué parte es dominio
- qué parte es interfaz
- qué parte coordina el flujo

---

## 14. Persistencia

La primera versión puede trabajar sin base de datos compleja.

Persistencia sugerida:

- configuración en JSON
- progreso efímero en memoria
- posibilidad futura de guardar estadísticas o partidas simples

Se puede guardar:

- nombre del usuario
- preferencias visuales
- volumen
- modo de marcado
- historial de victorias básico

---

## 15. Recursos gráficos y multimedia

## 15.1 Cartas
Cada carta debe tener su imagen en un directorio ordenado.

Convención sugerida:

- nombre estable
- ID consistente
- formato uniforme
- resolución razonable

## 15.2 Sonido
Opcional en primera versión.

Posibles usos:

- sonido al cantar carta
- sonido al marcar
- sonido de victoria

## 15.3 Tipografía
Buscar una tipografía clara, con aire tradicional o festivo moderado.

---

## 16. Reglas de implementación

## 16.1 Buenas prácticas mínimas

- usar entorno virtual
- fijar dependencias
- documentar instalación y ejecución
- separar assets del código
- escribir README claro
- incluir estructura reproducible

## 16.2 Estilo de desarrollo

- primero hacer funcionar el dominio
- después conectar interfaz
- luego pulir interacción
- finalmente embellecer

## 16.3 Refactor progresivo
El código Java previo debe servir como referencia conceptual, no como molde rígido.

La migración ideal sería:

1. identificar entidades y reglas del Java original
2. modelarlas mejor en Python
3. separar vista y lógica
4. rehacer la interfaz con más claridad
5. escribir pruebas sobre el modelo

---

## 17. Casos de uso principales

## 17.1 Iniciar nueva partida
**Actor:** jugador

**Flujo:**
1. el jugador selecciona “Nueva partida”
2. el sistema crea mazo y cartón
3. el sistema muestra la vista del juego
4. la partida queda en estado “en curso”

## 17.2 Cantar siguiente carta
**Actor:** jugador / sistema

**Flujo:**
1. se solicita la siguiente carta
2. el mazo entrega una carta
3. la carta se muestra en pantalla
4. se agrega al historial
5. la vista se actualiza

## 17.3 Marcar carta válida
**Actor:** jugador

**Flujo:**
1. el jugador selecciona una carta del cartón
2. el sistema verifica si fue cantada
3. si es válida, la marca
4. si no es válida, muestra aviso

## 17.4 Verificar victoria
**Actor:** sistema

**Flujo:**
1. tras una marca o revisión manual, el sistema evalúa el cartón
2. si cumple la regla, declara ganador
3. muestra pantalla de resultado

## 17.5 Reiniciar partida
**Actor:** jugador

**Flujo:**
1. el jugador pulsa reiniciar
2. el sistema limpia estado
3. reconstruye mazo y cartón
4. regresa al estado inicial de partida

---

## 18. Reglas de validación

- no se puede marcar una carta no cantada
- no se puede avanzar turno si el mazo está vacío
- no se puede declarar victoria si el patrón no está completo
- no se debe duplicar una carta en el historial del mismo turno
- la carta actual debe ser consistente con la última carta cantada

---

## 19. Pruebas sugeridas

## 19.1 Pruebas del modelo

- barajado del mazo
- cantidad correcta de cartas
- avance correcto de cartas
- marcado válido
- marcado inválido
- detección de cartón completo
- reinicio de partida

## 19.2 Pruebas del controlador

- transición entre pantallas
- respuesta al iniciar partida
- actualización del historial
- manejo de eventos de victoria

## 19.3 Pruebas de integración

- flujo completo desde menú hasta victoria
- reinicio y nueva partida
- configuración persistida

---

## 20. Roadmap sugerido

## Versión 0.1

- estructura base del proyecto
- clases del dominio
- mazo funcional
- cartón simple
- flujo básico de partida en consola o UI mínima

## Versión 0.2

- interfaz de escritorio inicial
- carta actual visible
- cartón interactivo
- historial
- verificación de victoria

## Versión 0.3

- configuración
- ayuda
- resultados finales
- persistencia básica
- mejoras visuales

## Versión 0.4

- audio opcional
- estadísticas mínimas
- temas visuales
- refinamiento del UX

---

## 21. Riesgos o errores comunes a evitar

- mezclar lógica de juego con código de widgets
- dejar el controlador demasiado grande
- meter demasiadas reglas opcionales desde el inicio
- depender de nombres de archivos frágiles
- hacer la vista “bonita” antes de estabilizar el dominio
- intentar soportar demasiados modos de juego al principio

---

## 22. Criterios de éxito

El proyecto se considera bien encaminado si:

- el juego funciona de principio a fin
- la estructura MVC se entiende claramente
- el dominio puede probarse sin abrir la interfaz
- la vista es ordenada y agradable
- el repositorio se puede ejecutar sin dolor
- la documentación permite retomar el proyecto después

---

## 23. Frase oficial del proyecto

**Aplicación de escritorio en Python para jugar Lotería Mexicana, concebida como proyecto didáctico y lúdico con arquitectura MVC clásica, interfaz clara y dominio bien separado para fines de aprendizaje, refactorización y portafolio.**

---

## 24. Decisiones de diseño escritas en piedra

- el proyecto será en **Python**
- la arquitectura base será **MVC**
- el dominio del juego debe quedar claro antes de embellecer la UI
- el código Java previo servirá como referencia, no como prisión
- el proyecto debe sentirse pequeño pero serio
- la aplicación debe ser suficientemente simple para terminarse, pero suficientemente limpia para enseñarte algo valioso
