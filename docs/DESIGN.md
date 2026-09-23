# Model Royale — diseño del juego

Battle royale de **avatares de IA**. Las personas no pelean: inscriben un avatar, le escriben una estrategia, y el modelo compite en un torneo de dilemas a dos jugadas.

Este servicio **no despliega modelos**. Los avatares son fichas de configuración que apuntan a endpoints que ya existen (OpenShift AI, vLLM, cualquier API compatible con OpenAI). GitOps publica solo el juego (API, web, base de datos).

## Piezas

| Pieza | Quién la opera | Dónde vive |
| --- | --- | --- |
| Avatares (Granite, Llama, GLM, Kimi…) | Admin del juego, mantenedor | Registro en la API: URL + `model` + temperatura |
| InferenceServices / vLLM | Plataforma / OpenShift AI | Otro namespace, otro GitOps |
| Juego, tablero, motor de batallas | Este repo | Namespace `model-royale` |
| Estrategia del jugador | Cada jugador | Prompt extra, editable fuera de combate |

## Por qué A / B (y no un chat libre)

Un combate libre es difícil de juzgar con justicia. Un juego de dos acciones, con matriz de pagos **parametrizable**, da:

- Resultados comparables entre parejas.
- Drama de espectador (traición, cooperación, racha).
- Espacio real para que el prompt del jugador importe: tit-for-tat, siempre cooperar, explotar, grim trigger.

Matriz por defecto (**Royale**), la que pediste:

|  | Oponente A | Oponente B |
| --- | --- | --- |
| **Tú A** | −2 / −2 | +5 / 0 |
| **Tú B** | 0 / +5 | +2 / +2 |

No es un Dilema del Prisionero clásico (ahí el sucesor de mutua defección debería ser peor que que te exploten). Esta matriz tiene dos equilibrios puros asimétricos: uno “explota” y el otro “aguanta”. El torneo premia quién lee mejor al rival a lo largo de varias rondas.

El admin puede cambiar la matriz por evento, con presets: Royale, Dilema del Prisionero, Gallina, Caza del ciervo.

## Qué ve cada modelo (la decisión de diseño)

Hay tres modos, configurables **antes de cada evento**:

1. **Ciego** — no ven historial ni la jugada actual. Puro one-shot. Útil para medir el sesgo del prompt, aburrido como espectáculo.
2. **Historial (recomendado, default)** — simultáneos: nadie ve la jugada de *esta* ronda, pero sí las anteriores del combate. Es un dilema iterado. Tit-for-tat, perdón, castigo, faroleo… el prompt del jugador tiene trabajo de verdad, y el tablero se entiende.
3. **Abierto** — el segundo en mover ve la jugada actual del primero (el primero se sortea cada ronda). Más “paneo de estrategia”, menos justo: el segundo tiene información extra. Sirve como modalidad especial, no como default.

Recomendación: **historial**. Es el punto dulce entre justicia y juego de estrategias. El modo abierto queda como experimento de taller.

## Modelo juez

Los modelos no siempre devuelven JSON limpio. El juez es **otro avatar opcional** (otra ficha del mantenedor, otro endpoint):

1. Se intenta parsear `{"move":"A"|"B","rationale":"..."}`.
2. Si falla y hay juez, se le pide extraer la jugada.
3. Si sigue fallando, política del evento: tratar como A, como B, o 0 puntos y marcar inválida.

El juez **no decide quién merece ganar**. Solo normaliza la acción. El marcador sale de la matriz.

Si el admin no asigna juez, el parser local basta para demos y para modelos bien educados por el system prompt.

## Capas de prompt (lo que ve el jugador)

Tres capas, visibles y honestas:

1. **Personalidad del avatar** — la escribe el admin (tono, idioma, límites). El jugador la ve, no la edita.
2. **Reglas del evento** — system prompt del juego: matriz, rondas, formato de respuesta. El jugador la ve, no la edita.
3. **Estrategia del jugador** — instrucciones extra. Editable **siempre que ese jugador no esté en un combate running**.

Varios jugadores pueden elegir el mismo avatar (mismo modelo). Gana quien escribió mejor la capa 3.

## Formatos de torneo

Configurables al crear el evento:

- **Todos contra todos** — cada pareja juega un combate de N rondas. Ranking por puntos totales, luego combates ganados.
- **Grupos** — se arman grupos de tamaño K, liga interna, avanzan los M mejores de cada grupo a eliminación directa.
- **Eliminación directa** — cuadro. Impares reciben bye. Empate en un combate: más puntos; si sigue, menos jugadas inválidas; si sigue, el de menor seed (quien se inscribió antes).

Un **combate** = N rondas (3 o 5, o las que ponga el admin) entre dos jugadores. Un jugador solo está en un combate a la vez, para que el lock del prompt sea obvio.

## Roles de UI

- **Jugador** — web mobile: inscribirse, elegir avatar, escribir estrategia, ver el tablero.
- **Tablero** — dashboard centralizado (proyector o móvil): inscritos, quién avanza, combates en vivo, resultados.
- **Admin** — web de escritorio, responsive: avatares (endpoints), eventos (formato, matriz, revelado, juez), abrir inscripciones, iniciar, seguir el vivo.

## Runtime

- API FastAPI + SQLAlchemy (SQLite local, Postgres en cluster).
- Web React (Vite), tema oscuro tipo consola OpenShift + paleta Red Hat.
- Inferencia: cliente HTTP compatible con OpenAI (`/v1/chat/completions`) contra la URL del avatar.
- Si el avatar no tiene URL, o `MOCK_INFERENCE=true`, el motor usa un jugador sintético que **sí respeta palabras clave de la estrategia** (`siempre A`, `siempre B`, `tit for tat`, `grim`, etc.). Así el taller funciona antes de tener InferenceServices.

Cuando tengas cluster, el mismo manifiesto de ArgoCD publica el juego. Los modelos siguen en su propio GitOps.
