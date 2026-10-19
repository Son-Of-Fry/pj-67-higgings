-- Re-alineación e importación exacta de proyectos en Huggins
BEGIN TRANSACTION;

-- 1. Re-alinear proyectos existentes para liberar IDs 1, 2, 3, 4
UPDATE tasks SET project_id = 99 WHERE project_id = 4;
UPDATE columns SET project_id = 99 WHERE project_id = 4;
UPDATE sprints SET project_id = 99 WHERE project_id = 4;
UPDATE project_docs SET project_id = 99 WHERE project_id = 4;
UPDATE bitacora_entries SET project_id = 99 WHERE project_id = 4;
UPDATE project_updates SET project_id = 99 WHERE project_id = 4;
UPDATE projects SET id = 99, name = 'hojademaiz' WHERE id = 4;

UPDATE tasks SET project_id = 65 WHERE project_id = 3;
UPDATE columns SET project_id = 65 WHERE project_id = 3;
UPDATE sprints SET project_id = 65 WHERE project_id = 3;
UPDATE project_docs SET project_id = 65 WHERE project_id = 3;
UPDATE bitacora_entries SET project_id = 65 WHERE project_id = 3;
UPDATE project_updates SET project_id = 65 WHERE project_id = 3;
UPDATE projects SET id = 65, name = 'Retail MLOps', theme = 'Machine Learning E2E (Pricing)', difficulty = 5, axis = 'E2E / MLOps' WHERE id = 3;

UPDATE tasks SET project_id = 67 WHERE project_id = 2;
UPDATE columns SET project_id = 67 WHERE project_id = 2;
UPDATE sprints SET project_id = 67 WHERE project_id = 2;
UPDATE project_docs SET project_id = 67 WHERE project_id = 2;
UPDATE bitacora_entries SET project_id = 67 WHERE project_id = 2;
UPDATE project_updates SET project_id = 67 WHERE project_id = 2;
UPDATE projects SET id = 67, name = 'Platform', theme = 'Orquestación IA', difficulty = 4, axis = 'Plataforma / MCP' WHERE id = 2;

UPDATE tasks SET project_id = 0 WHERE project_id = 1;
UPDATE columns SET project_id = 0 WHERE project_id = 1;
UPDATE sprints SET project_id = 0 WHERE project_id = 1;
UPDATE project_docs SET project_id = 0 WHERE project_id = 1;
UPDATE bitacora_entries SET project_id = 0 WHERE project_id = 1;
UPDATE project_updates SET project_id = 0 WHERE project_id = 1;
UPDATE projects SET id = 0, name = 'Tutorial' WHERE id = 1;

-- Proyecto 1: Contagio financiero y fugas de liquidez
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (1, 'Contagio financiero y fugas de liquidez', 'Modelado de cópulas arquimedianas y grafos de red para dependencia de cola.', '', '# PJ-01 — Contagio financiero y fugas de liquidez

> **Eje:** Abierto | **Tema:** Riesgo de Crédito | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo identificar nodos de riesgo sistémico en carteras minoristas antes del default masivo?

## 2. Metodología y Enfoque Técnico
Modelado de cópulas arquimedianas y grafos de red para dependencia de cola.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Riesgo de Crédito', 'Abierto', 'Planeación', '{"catalog_id": 1, "pregunta_general": "\u00bfC\u00f3mo identificar nodos de riesgo sist\u00e9mico en carteras minoristas antes del default masivo?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(1, 'Por Hacer', 1), (1, 'En Progreso', 2), (1, 'En Revisión', 3), (1, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(1, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 2: Colusión paramétrica en reclamaciones
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (2, 'Colusión paramétrica en reclamaciones', 'PageRank inverso y análisis topológico en grafos multipartitos (paciente-médico-clínica).', '', '# PJ-02 — Colusión paramétrica en reclamaciones

> **Eje:** Abierto | **Tema:** Seguros de Salud | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo detectar fraude distribuido que evade umbrales de auditoría estándar?

## 2. Metodología y Enfoque Técnico
PageRank inverso y análisis topológico en grafos multipartitos (paciente-médico-clínica).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Seguros de Salud', 'Abierto', 'Planeación', '{"catalog_id": 2, "pregunta_general": "\u00bfC\u00f3mo detectar fraude distribuido que evade umbrales de auditor\u00eda est\u00e1ndar?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(2, 'Por Hacer', 1), (2, 'En Progreso', 2), (2, 'En Revisión', 3), (2, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(2, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 3: Riesgo de interrupción por variables estocásticas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (3, 'Riesgo de interrupción por variables estocásticas', 'Simulación Monte Carlo + Cadenas de Markov de tiempo continuo (CTMC).', '', '# PJ-03 — Riesgo de interrupción por variables estocásticas

> **Eje:** Abierto | **Tema:** Supply Chain | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo optimizar inventarios ante disrupciones climáticas o aduaneras asimétricas?

## 2. Metodología y Enfoque Técnico
Simulación Monte Carlo + Cadenas de Markov de tiempo continuo (CTMC).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Supply Chain', 'Abierto', 'Planeación', '{"catalog_id": 3, "pregunta_general": "\u00bfC\u00f3mo optimizar inventarios ante disrupciones clim\u00e1ticas o aduaneras asim\u00e9tricas?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(3, 'Por Hacer', 1), (3, 'En Progreso', 2), (3, 'En Revisión', 3), (3, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(3, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 4: Elasticidad de precios bajo hiperinflación
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (4, 'Elasticidad de precios bajo hiperinflación', 'Inferencia causal (Control Sintético/Bosques Causales) y optimización no lineal.', '', '# PJ-04 — Elasticidad de precios bajo hiperinflación

> **Eje:** Abierto | **Tema:** Retail / Pricing | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo aislar el ruido macroeconómico para calcular la verdadera elasticidad de demanda?

## 2. Metodología y Enfoque Técnico
Inferencia causal (Control Sintético/Bosques Causales) y optimización no lineal.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Microservicio consumido por front-end. Recibe ID producto/stock, consulta caché (Redis) y devuelve precio optimizado al instante.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Retail / Pricing', 'Abierto', 'Planeación', '{"catalog_id": 4, "pregunta_general": "\u00bfC\u00f3mo aislar el ruido macroecon\u00f3mico para calcular la verdadera elasticidad de demanda?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Microservicio consumido por front-end. Recibe ID producto/stock, consulta cach\u00e9 (Redis) y devuelve precio optimizado al instante."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(4, 'Por Hacer', 1), (4, 'En Progreso', 2), (4, 'En Revisión', 3), (4, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(4, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 5: Actualización dinámica del riesgo de longevidad
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (5, 'Actualización dinámica del riesgo de longevidad', 'Modelo Lee-Carter con procesos de difusión con saltos (Merton).', '', '# PJ-05 — Actualización dinámica del riesgo de longevidad

> **Eje:** Abierto | **Tema:** Pensiones / Vida | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo recalibrar reservas matemáticas ante cambios demográficos abruptos post-pandemia?

## 2. Metodología y Enfoque Técnico
Modelo Lee-Carter con procesos de difusión con saltos (Merton).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Pensiones / Vida', 'Abierto', 'Planeación', '{"catalog_id": 5, "pregunta_general": "\u00bfC\u00f3mo recalibrar reservas matem\u00e1ticas ante cambios demogr\u00e1ficos abruptos post-pandemia?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(5, 'Por Hacer', 1), (5, 'En Progreso', 2), (5, 'En Revisión', 3), (5, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(5, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 6: Ingeniería inversa de la sonrisa de volatilidad
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (6, 'Ingeniería inversa de la sonrisa de volatilidad', 'Calibración Heston/difusión de saltos por mínimos cuadrados no lineales vs Black-Scholes.', '', '# PJ-06 — Ingeniería inversa de la sonrisa de volatilidad

> **Eje:** Inverso | **Tema:** Derivados Financieros | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Por qué el modelo clásico falla y cómo deducir la volatilidad real del mercado?

## 2. Metodología y Enfoque Técnico
Calibración Heston/difusión de saltos por mínimos cuadrados no lineales vs Black-Scholes.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Derivados Financieros', 'Inverso', 'Planeación', '{"catalog_id": 6, "pregunta_general": "\u00bfPor qu\u00e9 el modelo cl\u00e1sico falla y c\u00f3mo deducir la volatilidad real del mercado?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(6, 'Por Hacer', 1), (6, 'En Progreso', 2), (6, 'En Revisión', 3), (6, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(6, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 7: Supuestos frágiles en reservas de siniestros
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (7, 'Supuestos frágiles en reservas de siniestros', 'GLM sobredisperso (Poisson/Gamma) y bootstrapping de residuales en triángulos run-off.', '', '# PJ-07 — Supuestos frágiles en reservas de siniestros

> **Eje:** Inverso | **Tema:** Reservas de Seguros | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿En qué escenarios colapsa el método Chain-Ladder y cómo medir ese error?

## 2. Metodología y Enfoque Técnico
GLM sobredisperso (Poisson/Gamma) y bootstrapping de residuales en triángulos run-off.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Reservas de Seguros', 'Inverso', 'Planeación', '{"catalog_id": 7, "pregunta_general": "\u00bfEn qu\u00e9 escenarios colapsa el m\u00e9todo Chain-Ladder y c\u00f3mo medir ese error?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(7, 'Por Hacer', 1), (7, 'En Progreso', 2), (7, 'En Revisión', 3), (7, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(7, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 8: Identificación de funciones de costo ocultas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (8, 'Identificación de funciones de costo ocultas', 'Aprendizaje por Refuerzo Inverso (IRL) o regresión convexa sobre datos GPS.', '', '# PJ-08 — Identificación de funciones de costo ocultas

> **Eje:** Inverso | **Tema:** Logística / Routing | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Qué función matemática optimizan realmente los conductores al desviarse del VRP teórico?

## 2. Metodología y Enfoque Técnico
Aprendizaje por Refuerzo Inverso (IRL) o regresión convexa sobre datos GPS.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Logística / Routing', 'Inverso', 'Planeación', '{"catalog_id": 8, "pregunta_general": "\u00bfQu\u00e9 funci\u00f3n matem\u00e1tica optimizan realmente los conductores al desviarse del VRP te\u00f3rico?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(8, 'Por Hacer', 1), (8, 'En Progreso', 2), (8, 'En Revisión', 3), (8, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(8, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 9: Probabilidad de default neutral al riesgo
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (9, 'Probabilidad de default neutral al riesgo', 'Modelo estructural de Merton resolviendo sistemas de ecuaciones no lineales.', '', '# PJ-09 — Probabilidad de default neutral al riesgo

> **Eje:** Inverso | **Tema:** Riesgo Corporativo | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo extraer la probabilidad de default diaria implícita en los spreads de bonos?

## 2. Metodología y Enfoque Técnico
Modelo estructural de Merton resolviendo sistemas de ecuaciones no lineales.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Riesgo Corporativo', 'Inverso', 'Planeación', '{"catalog_id": 9, "pregunta_general": "\u00bfC\u00f3mo extraer la probabilidad de default diaria impl\u00edcita en los spreads de bonos?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(9, 'Por Hacer', 1), (9, 'En Progreso', 2), (9, 'En Revisión', 3), (9, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(9, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 10: Límites topológicos de optimización de Markowitz
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (10, 'Límites topológicos de optimización de Markowitz', 'SVD de la matriz de covarianza y regularización (Shrinkage Ledoit-Wolf / L1-L2).', '', '# PJ-10 — Límites topológicos de optimización de Markowitz

> **Eje:** Inverso | **Tema:** Asset Management | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Por qué la frontera eficiente genera pesos inestables fuera de muestra y cómo estabilizarlo?

## 2. Metodología y Enfoque Técnico
SVD de la matriz de covarianza y regularización (Shrinkage Ledoit-Wolf / L1-L2).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Asset Management', 'Inverso', 'Planeación', '{"catalog_id": 10, "pregunta_general": "\u00bfPor qu\u00e9 la frontera eficiente genera pesos inestables fuera de muestra y c\u00f3mo estabilizarlo?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(10, 'Por Hacer', 1), (10, 'En Progreso', 2), (10, 'En Revisión', 3), (10, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(10, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 11: Optimización de Subastas Multi-Atributo
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (11, 'Optimización de Subastas Multi-Atributo', 'Diseño de mecanismos y teoría de juegos cooperativos.', '', '# PJ-11 — Optimización de Subastas Multi-Atributo

> **Eje:** Abierto | **Tema:** Microeconomía | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo diseñar un mecanismo de subasta que maximice ingresos considerando calidad y tiempo, no solo precio?

## 2. Metodología y Enfoque Técnico
Diseño de mecanismos y teoría de juegos cooperativos.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Microeconomía', 'Abierto', 'Planeación', '{"catalog_id": 11, "pregunta_general": "\u00bfC\u00f3mo dise\u00f1ar un mecanismo de subasta que maximice ingresos considerando calidad y tiempo, no solo precio?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(11, 'Por Hacer', 1), (11, 'En Progreso', 2), (11, 'En Revisión', 3), (11, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(11, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 12: Tarificación Telemática Dinámica (PAYD)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (12, 'Tarificación Telemática Dinámica (PAYD)', 'Modelos de riesgos competitivos (Survival Analysis) sobre datos telemáticos de alta frecuencia.', '', '# PJ-12 — Tarificación Telemática Dinámica (PAYD)

> **Eje:** Abierto | **Tema:** Seguros de Auto | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo estructurar primas justas en tiempo real basadas en telemetría sin sobrerrepresentar el ruido?

## 2. Metodología y Enfoque Técnico
Modelos de riesgos competitivos (Survival Analysis) sobre datos telemáticos de alta frecuencia.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Microservicio de ingesta alta (Kafka/Kinesis). Procesa ráfagas de telemetría (GPS/Acelerómetro) y actualiza riesgo de póliza en tiempo real.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Seguros de Auto', 'Abierto', 'Planeación', '{"catalog_id": 12, "pregunta_general": "\u00bfC\u00f3mo estructurar primas justas en tiempo real basadas en telemetr\u00eda sin sobrerrepresentar el ruido?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Microservicio de ingesta alta (Kafka/Kinesis). Procesa r\u00e1fagas de telemetr\u00eda (GPS/Aceler\u00f3metro) y actualiza riesgo de p\u00f3liza en tiempo real."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(12, 'Por Hacer', 1), (12, 'En Progreso', 2), (12, 'En Revisión', 3), (12, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(12, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 13: Nowcasting de Inflación Subyacente
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (13, 'Nowcasting de Inflación Subyacente', 'Modelos dinámicos de factores (DFM) y filtros de Kalman aplicados a series de alta dimensionalidad.', '', '# PJ-13 — Nowcasting de Inflación Subyacente

> **Eje:** Abierto | **Tema:** Macroeconomía | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo predecir la inflación a muy corto plazo utilizando datos alternativos (web scraping, movilidad)?

## 2. Metodología y Enfoque Técnico
Modelos dinámicos de factores (DFM) y filtros de Kalman aplicados a series de alta dimensionalidad.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Macroeconomía', 'Abierto', 'Planeación', '{"catalog_id": 13, "pregunta_general": "\u00bfC\u00f3mo predecir la inflaci\u00f3n a muy corto plazo utilizando datos alternativos (web scraping, movilidad)?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(13, 'Por Hacer', 1), (13, 'En Progreso', 2), (13, 'En Revisión', 3), (13, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(13, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 14: Asignación Dinámica de Flotillas Híbridas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (14, 'Asignación Dinámica de Flotillas Híbridas', 'Procesos de decisión de Markov (MDP) con restricciones de capacidad en tiempo real.', '', '# PJ-14 — Asignación Dinámica de Flotillas Híbridas

> **Eje:** Abierto | **Tema:** Logística / Última Milla | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo enrutar simultáneamente vehículos propios y crowdsourced ante demanda estocástica?

## 2. Metodología y Enfoque Técnico
Procesos de decisión de Markov (MDP) con restricciones de capacidad en tiempo real.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Logística / Última Milla', 'Abierto', 'Planeación', '{"catalog_id": 14, "pregunta_general": "\u00bfC\u00f3mo enrutar simult\u00e1neamente veh\u00edculos propios y crowdsourced ante demanda estoc\u00e1stica?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(14, 'Por Hacer', 1), (14, 'En Progreso', 2), (14, 'En Revisión', 3), (14, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(14, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 15: Rebalanceo Óptimo bajo Costos de Transacción
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (15, 'Rebalanceo Óptimo bajo Costos de Transacción', 'Control estocástico impulsivo y optimización de fronteras de no-intervención.', '', '# PJ-15 — Rebalanceo Óptimo bajo Costos de Transacción

> **Eje:** Abierto | **Tema:** Finanzas Cuantitativas | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cuál es la frecuencia óptima para rebalancear un portafolio cuando los costos diluyen el alfa?

## 2. Metodología y Enfoque Técnico
Control estocástico impulsivo y optimización de fronteras de no-intervención.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Finanzas Cuantitativas', 'Abierto', 'Planeación', '{"catalog_id": 15, "pregunta_general": "\u00bfCu\u00e1l es la frecuencia \u00f3ptima para rebalancear un portafolio cuando los costos diluyen el alfa?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(15, 'Por Hacer', 1), (15, 'En Progreso', 2), (15, 'En Revisión', 3), (15, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(15, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 16: Riesgo Espacial en Bonos Catastróficos (CAT Bonds)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (16, 'Riesgo Espacial en Bonos Catastróficos (CAT Bonds)', 'Teoría del Valor Extremo (EVT) bivariada y cópulas espaciales.', '', '# PJ-16 — Riesgo Espacial en Bonos Catastróficos (CAT Bonds)

> **Eje:** Abierto | **Tema:** Seguros Catastróficos | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo modelar la dependencia espacial extrema para estructurar un bono paramétrico contra huracanes?

## 2. Metodología y Enfoque Técnico
Teoría del Valor Extremo (EVT) bivariada y cópulas espaciales.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Seguros Catastróficos', 'Abierto', 'Planeación', '{"catalog_id": 16, "pregunta_general": "\u00bfC\u00f3mo modelar la dependencia espacial extrema para estructurar un bono param\u00e9trico contra huracanes?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(16, 'Por Hacer', 1), (16, 'En Progreso', 2), (16, 'En Revisión', 3), (16, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(16, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 17: Deducción de Aversión a la Pérdida
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (17, 'Deducción de Aversión a la Pérdida', 'Estimación paramétrica de la función de valor de la Teoría Prospectiva a partir de microdatos de trading.', '', '# PJ-17 — Deducción de Aversión a la Pérdida

> **Eje:** Inverso | **Tema:** Economía del Comportamiento | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuál es la verdadera asimetría entre ganancias y pérdidas implícita en el trading minorista?

## 2. Metodología y Enfoque Técnico
Estimación paramétrica de la función de valor de la Teoría Prospectiva a partir de microdatos de trading.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Economía del Comportamiento', 'Inverso', 'Planeación', '{"catalog_id": 17, "pregunta_general": "\u00bfCu\u00e1l es la verdadera asimetr\u00eda entre ganancias y p\u00e9rdidas impl\u00edcita en el trading minorista?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(17, 'Por Hacer', 1), (17, 'En Progreso', 2), (17, 'En Revisión', 3), (17, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(17, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 18: Ingeniería Inversa del WACC y Prima de Riesgo
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (18, 'Ingeniería Inversa del WACC y Prima de Riesgo', 'Revertir el modelo de flujos de caja descontados (DCF) usando el histórico de CAPEX aprobado para deducir la tasa de descuento implícita y aversión al riesgo gerencial.', '', '# PJ-18 — Ingeniería Inversa del WACC y Prima de Riesgo

> **Eje:** Inverso | **Tema:** Finanzas Corporativas | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Qué tasa de retorno mínima exigen realmente los directivos al aprobar proyectos de inversión?

## 2. Metodología y Enfoque Técnico
Revertir el modelo de flujos de caja descontados (DCF) usando el histórico de CAPEX aprobado para deducir la tasa de descuento implícita y aversión al riesgo gerencial.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Finanzas Corporativas', 'Inverso', 'Planeación', '{"catalog_id": 18, "pregunta_general": "\u00bfQu\u00e9 tasa de retorno m\u00ednima exigen realmente los directivos al aprobar proyectos de inversi\u00f3n?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(18, 'Por Hacer', 1), (18, 'En Progreso', 2), (18, 'En Revisión', 3), (18, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(18, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 19: Decaimiento No Lineal de Perecederos
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (19, 'Decaimiento No Lineal de Perecederos', 'Estimación de la ecuación de Arrhenius invertida desde datos de mermas e historial de temperatura.', '', '# PJ-19 — Decaimiento No Lineal de Perecederos

> **Eje:** Inverso | **Tema:** Logística de Frío | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuál es el verdadero límite de tiempo térmico (Shelf-life) antes de la pérdida de valor comercial?

## 2. Metodología y Enfoque Técnico
Estimación de la ecuación de Arrhenius invertida desde datos de mermas e historial de temperatura.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Logística de Frío', 'Inverso', 'Planeación', '{"catalog_id": 19, "pregunta_general": "\u00bfCu\u00e1l es el verdadero l\u00edmite de tiempo t\u00e9rmico (Shelf-life) antes de la p\u00e9rdida de valor comercial?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(19, 'Por Hacer', 1), (19, 'En Progreso', 2), (19, 'En Revisión', 3), (19, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(19, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 20: Identidad Causal vs Correlación Espuria
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (20, 'Identidad Causal vs Correlación Espuria', 'Regresión en Discontinuidad (RDD) espacial e Inferencia Causal aplicada a datos municipales.', '', '# PJ-20 — Identidad Causal vs Correlación Espuria

> **Eje:** Inverso | **Tema:** Econometría | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo aislar el impacto de una política fiscal cuando existen múltiples factores de confusión simultáneos?

## 2. Metodología y Enfoque Técnico
Regresión en Discontinuidad (RDD) espacial e Inferencia Causal aplicada a datos municipales.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Econometría', 'Inverso', 'Planeación', '{"catalog_id": 20, "pregunta_general": "\u00bfC\u00f3mo aislar el impacto de una pol\u00edtica fiscal cuando existen m\u00faltiples factores de confusi\u00f3n simult\u00e1neos?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(20, 'Por Hacer', 1), (20, 'En Progreso', 2), (20, 'En Revisión', 3), (20, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(20, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 21: Optimización de Tratados de Reaseguro No Proporcional
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (21, 'Optimización de Tratados de Reaseguro No Proporcional', 'Simulación de procesos de riesgo compuestos (Ruin Theory) con funciones de utilidad severas.', '', '# PJ-21 — Optimización de Tratados de Reaseguro No Proporcional

> **Eje:** Abierto | **Tema:** Reaseguro | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cuál es el punto de retención óptimo (deducible) para maximizar la rentabilidad ajustada al riesgo (RAROC)?

## 2. Metodología y Enfoque Técnico
Simulación de procesos de riesgo compuestos (Ruin Theory) con funciones de utilidad severas.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Reaseguro', 'Abierto', 'Planeación', '{"catalog_id": 21, "pregunta_general": "\u00bfCu\u00e1l es el punto de retenci\u00f3n \u00f3ptimo (deducible) para maximizar la rentabilidad ajustada al riesgo (RAROC)?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(21, 'Por Hacer', 1), (21, 'En Progreso', 2), (21, 'En Revisión', 3), (21, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(21, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 22: Detección de Burbujas Especulativas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (22, 'Detección de Burbujas Especulativas', 'Modelos LPPLS (Log-Periodic Power Law Singularity) aplicados a series temporales financieras.', '', '# PJ-22 — Detección de Burbujas Especulativas

> **Eje:** Abierto | **Tema:** Finanzas de Comportamiento | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo identificar el crecimiento supra-exponencial previo al colapso en activos ilíquidos?

## 2. Metodología y Enfoque Técnico
Modelos LPPLS (Log-Periodic Power Law Singularity) aplicados a series temporales financieras.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Finanzas de Comportamiento', 'Abierto', 'Planeación', '{"catalog_id": 22, "pregunta_general": "\u00bfC\u00f3mo identificar el crecimiento supra-exponencial previo al colapso en activos il\u00edquidos?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(22, 'Por Hacer', 1), (22, 'En Progreso', 2), (22, 'En Revisión', 3), (22, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(22, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 23: Cuantificación de Fraude Interno
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (23, 'Cuantificación de Fraude Interno', 'Ajuste de distribuciones de cola pesada (Pareto Generalizada) usando picos sobre el umbral (POT).', '', '# PJ-23 — Cuantificación de Fraude Interno

> **Eje:** Abierto | **Tema:** Riesgo Operacional | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo modelar la distribución de severidad para eventos extremos y raros (Low Frequency, High Severity)?

## 2. Metodología y Enfoque Técnico
Ajuste de distribuciones de cola pesada (Pareto Generalizada) usando picos sobre el umbral (POT).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Riesgo Operacional', 'Abierto', 'Planeación', '{"catalog_id": 23, "pregunta_general": "\u00bfC\u00f3mo modelar la distribuci\u00f3n de severidad para eventos extremos y raros (Low Frequency, High Severity)?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(23, 'Por Hacer', 1), (23, 'En Progreso', 2), (23, 'En Revisión', 3), (23, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(23, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 24: Modelado Transaccional No Contractual (Buy Till You Die)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (24, 'Modelado Transaccional No Contractual (Buy Till You Die)', 'Implementación algorítmica de modelos Pareto/NBD o BG/NBD calibrados por máxima verosimilitud.', '', '# PJ-24 — Modelado Transaccional No Contractual (Buy Till You Die)

> **Eje:** Abierto | **Tema:** Ventas / Churn | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo predecir el Customer Lifetime Value (CLV) cuando el cliente no avisa explícitamente que cancelará?

## 2. Metodología y Enfoque Técnico
Implementación algorítmica de modelos Pareto/NBD o BG/NBD calibrados por máxima verosimilitud.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Ventas / Churn', 'Abierto', 'Planeación', '{"catalog_id": 24, "pregunta_general": "\u00bfC\u00f3mo predecir el Customer Lifetime Value (CLV) cuando el cliente no avisa expl\u00edcitamente que cancelar\u00e1?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(24, 'Por Hacer', 1), (24, 'En Progreso', 2), (24, 'En Revisión', 3), (24, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(24, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 25: Deducción de Costos de Ruptura (Stockout)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (25, 'Deducción de Costos de Ruptura (Stockout)', 'Resolver el problema de Newsvendor a la inversa utilizando niveles de inventario históricos para inferir penalizaciones.', '', '# PJ-25 — Deducción de Costos de Ruptura (Stockout)

> **Eje:** Inverso | **Tema:** Logística de Inventarios | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuál es el costo implícito real que la empresa le asigna a perder una venta frente a mantener inventario?

## 2. Metodología y Enfoque Técnico
Resolver el problema de Newsvendor a la inversa utilizando niveles de inventario históricos para inferir penalizaciones.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Logística de Inventarios', 'Inverso', 'Planeación', '{"catalog_id": 25, "pregunta_general": "\u00bfCu\u00e1l es el costo impl\u00edcito real que la empresa le asigna a perder una venta frente a mantener inventario?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(25, 'Por Hacer', 1), (25, 'En Progreso', 2), (25, 'En Revisión', 3), (25, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(25, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 26: Extracción de Lapsation Risk
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (26, 'Extracción de Lapsation Risk', 'Modelos de duración (Cox Proportional Hazards) con covariables dependientes del tiempo macroeconómicas.', '', '# PJ-26 — Extracción de Lapsation Risk

> **Eje:** Inverso | **Tema:** Seguros de Vida | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Qué factores empíricos provocan la cancelación masiva de pólizas de vida (efecto de tipo de interés vs shock de liquidez)?

## 2. Metodología y Enfoque Técnico
Modelos de duración (Cox Proportional Hazards) con covariables dependientes del tiempo macroeconómicas.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Seguros de Vida', 'Inverso', 'Planeación', '{"catalog_id": 26, "pregunta_general": "\u00bfQu\u00e9 factores emp\u00edricos provocan la cancelaci\u00f3n masiva de p\u00f3lizas de vida (efecto de tipo de inter\u00e9s vs shock de liquidez)?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(26, 'Por Hacer', 1), (26, 'En Progreso', 2), (26, 'En Revisión', 3), (26, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(26, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 27: Descomposición del VaR Histórico
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (27, 'Descomposición del VaR Histórico', 'Pruebas de backtesting (Kupiec/Christoffersen) para demostrar la falla empírica de la normalidad en retornos.', '', '# PJ-27 — Descomposición del VaR Histórico

> **Eje:** Inverso | **Tema:** Riesgo de Mercado | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Por qué el Value at Risk subestima sistemáticamente el riesgo en regímenes de alta volatilidad?

## 2. Metodología y Enfoque Técnico
Pruebas de backtesting (Kupiec/Christoffersen) para demostrar la falla empírica de la normalidad en retornos.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Riesgo de Mercado', 'Inverso', 'Planeación', '{"catalog_id": 27, "pregunta_general": "\u00bfPor qu\u00e9 el Value at Risk subestima sistem\u00e1ticamente el riesgo en reg\u00edmenes de alta volatilidad?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(27, 'Por Hacer', 1), (27, 'En Progreso', 2), (27, 'En Revisión', 3), (27, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(27, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 28: Asignación de Líneas de Crédito Dinámicas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (28, 'Asignación de Líneas de Crédito Dinámicas', 'Aprendizaje por refuerzo (Q-Learning o Bandidos Multibrazo) bajo restricciones de riesgo (CVaR).', '', '# PJ-28 — Asignación de Líneas de Crédito Dinámicas

> **Eje:** Abierto | **Tema:** Banca Minorista | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo ajustar límites de crédito para maximizar el margen de interés neto limitando la exposición al default?

## 2. Metodología y Enfoque Técnico
Aprendizaje por refuerzo (Q-Learning o Bandidos Multibrazo) bajo restricciones de riesgo (CVaR).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Banca Minorista', 'Abierto', 'Planeación', '{"catalog_id": 28, "pregunta_general": "\u00bfC\u00f3mo ajustar l\u00edmites de cr\u00e9dito para maximizar el margen de inter\u00e9s neto limitando la exposici\u00f3n al default?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(28, 'Por Hacer', 1), (28, 'En Progreso', 2), (28, 'En Revisión', 3), (28, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(28, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 29: Tarificación Algorítmica con Restricciones de Equidad
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (29, 'Tarificación Algorítmica con Restricciones de Equidad', 'Optimización penalizada integrando métricas de Fairness (Equalized Odds/Demographic Parity) en la función objetivo.', '', '# PJ-29 — Tarificación Algorítmica con Restricciones de Equidad

> **Eje:** Abierto | **Tema:** Pricing de Servicios | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo asegurar que un algoritmo de precios dinámicos no penalice desproporcionadamente a grupos demográficos protegidos?

## 2. Metodología y Enfoque Técnico
Optimización penalizada integrando métricas de Fairness (Equalized Odds/Demographic Parity) en la función objetivo.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Microservicio consumido por front-end. Recibe ID producto/stock, consulta caché (Redis) y devuelve precio optimizado al instante.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Pricing de Servicios', 'Abierto', 'Planeación', '{"catalog_id": 29, "pregunta_general": "\u00bfC\u00f3mo asegurar que un algoritmo de precios din\u00e1micos no penalice desproporcionadamente a grupos demogr\u00e1ficos protegidos?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Microservicio consumido por front-end. Recibe ID producto/stock, consulta cach\u00e9 (Redis) y devuelve precio optimizado al instante."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(29, 'Por Hacer', 1), (29, 'En Progreso', 2), (29, 'En Revisión', 3), (29, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(29, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 30: Impacto de Externalidades en Bienes Raíces
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (30, 'Impacto de Externalidades en Bienes Raíces', 'Modelos de precios hedónicos espaciales controlando por autocorrelación topológica (Spatial Lag Models).', '', '# PJ-30 — Impacto de Externalidades en Bienes Raíces

> **Eje:** Inverso | **Tema:** Economía Urbana | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuánto del precio de la vivienda está puramente explicado por la proximidad a nodos de transporte o criminalidad?

## 2. Metodología y Enfoque Técnico
Modelos de precios hedónicos espaciales controlando por autocorrelación topológica (Spatial Lag Models).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Economía Urbana', 'Inverso', 'Planeación', '{"catalog_id": 30, "pregunta_general": "\u00bfCu\u00e1nto del precio de la vivienda est\u00e1 puramente explicado por la proximidad a nodos de transporte o criminalidad?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(30, 'Por Hacer', 1), (30, 'En Progreso', 2), (30, 'En Revisión', 3), (30, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(30, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 31: Motor RAG NIF (Normas de Información Financiera)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (31, 'Motor RAG NIF (Normas de Información Financiera)', 'Procesamiento del compendio de las NIF. Chunking semántico avanzado que preserve la jerarquía de párrafos. Base de datos vectorial para responder consultas de tratamiento contable específico.', '', '# PJ-31 — Motor RAG NIF (Normas de Información Financiera)

> **Eje:** Abierto | **Tema:** Contabilidad y Regulación (NIF) | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo extraer criterios contables exactos de un texto masivo con referencias cruzadas jerárquicas?

## 2. Metodología y Enfoque Técnico
Procesamiento del compendio de las NIF. Chunking semántico avanzado que preserve la jerarquía de párrafos. Base de datos vectorial para responder consultas de tratamiento contable específico.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Media (APIs o Inferencia Batch)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Contabilidad y Regulación (NIF)', 'Abierto', 'Planeación', '{"catalog_id": 31, "pregunta_general": "\u00bfC\u00f3mo extraer criterios contables exactos de un texto masivo con referencias cruzadas jer\u00e1rquicas?", "despliegue": "Media (APIs o Inferencia Batch)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(31, 'Por Hacer', 1), (31, 'En Progreso', 2), (31, 'En Revisión', 3), (31, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(31, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 32: Agente mRAG en Vivo: Auditoría de Planograma y Stock
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (32, 'Agente mRAG en Vivo: Auditoría de Planograma y Stock', 'Captura de video en tiempo real. Extracción de frames y procesamiento multimodal (Vision LLM / SigLIP) para comparar el estante físico contra el planograma y detectar faltantes o etiquetas erróneas.', '', '# PJ-32 — Agente mRAG en Vivo: Auditoría de Planograma y Stock

> **Eje:** Abierto | **Tema:** Retail / Computer Vision | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo identificar quiebres de inventario o discrepancias de precios en tiempo real mediante cámara?

## 2. Metodología y Enfoque Técnico
Captura de video en tiempo real. Extracción de frames y procesamiento multimodal (Vision LLM / SigLIP) para comparar el estante físico contra el planograma y detectar faltantes o etiquetas erróneas.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Retail / Computer Vision', 'Abierto', 'Planeación', '{"catalog_id": 32, "pregunta_general": "\u00bfC\u00f3mo identificar quiebres de inventario o discrepancias de precios en tiempo real mediante c\u00e1mara?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(32, 'Por Hacer', 1), (32, 'En Progreso', 2), (32, 'En Revisión', 3), (32, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(32, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 33: Descomposición Algorítmica de Unit Economics
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (33, 'Descomposición Algorítmica de Unit Economics', 'Regresión de panel sobre estados de resultados agregados y logs transaccionales para deducir el Costo de Adquisición (CAC) y LTV ocultos, superando limitaciones de contabilidad tradicional.', '', '# PJ-33 — Descomposición Algorítmica de Unit Economics

> **Eje:** Inverso | **Tema:** Análisis Empresarial | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuál es el margen de contribución real por transacción si los costos fijos se asignan dinámicamente?

## 2. Metodología y Enfoque Técnico
Regresión de panel sobre estados de resultados agregados y logs transaccionales para deducir el Costo de Adquisición (CAC) y LTV ocultos, superando limitaciones de contabilidad tradicional.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Análisis Empresarial', 'Inverso', 'Planeación', '{"catalog_id": 33, "pregunta_general": "\u00bfCu\u00e1l es el margen de contribuci\u00f3n real por transacci\u00f3n si los costos fijos se asignan din\u00e1micamente?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(33, 'Por Hacer', 1), (33, 'En Progreso', 2), (33, 'En Revisión', 3), (33, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(33, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 34: Previsión de Demanda Dinámica (Filtro de Kalman)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (34, 'Previsión de Demanda Dinámica (Filtro de Kalman)', 'Contexto conocido: Predecir ventas. Reto: En lugar de usar ARIMA/Prophet de caja negra, derivar y programar las ecuaciones de actualización de estado (Filtro de Kalman o Holt-Winters) a mano.', '', '# PJ-34 — Previsión de Demanda Dinámica (Filtro de Kalman)

> **Eje:** Inverso | **Tema:** Retail / Inventarios | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo adapta un modelo de series temporales la tendencia ante shocks de demanda súbitos?

## 2. Metodología y Enfoque Técnico
Contexto conocido: Predecir ventas. Reto: En lugar de usar ARIMA/Prophet de caja negra, derivar y programar las ecuaciones de actualización de estado (Filtro de Kalman o Holt-Winters) a mano.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Microservicio stateful. Actualiza vector de estado y varianza en memoria por cada evento de venta, sin reentrenamiento masivo batch.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Retail / Inventarios', 'Inverso', 'Planeación', '{"catalog_id": 34, "pregunta_general": "\u00bfC\u00f3mo adapta un modelo de series temporales la tendencia ante shocks de demanda s\u00fabitos?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Microservicio stateful. Actualiza vector de estado y varianza en memoria por cada evento de venta, sin reentrenamiento masivo batch."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(34, 'Por Hacer', 1), (34, 'En Progreso', 2), (34, 'En Revisión', 3), (34, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(34, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 35: Deserción Marginal Algorítmica
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (35, 'Deserción Marginal Algorítmica', 'Contexto conocido: Predicción de churn. Reto: Resolver el problema de clasificación binaria programando el algoritmo de optimización (Descenso de Gradiente o Newton-Raphson) desde cero para Regresión Logística.', '', '# PJ-35 — Deserción Marginal Algorítmica

> **Eje:** Inverso | **Tema:** Ventas / Churn | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo cambian exactamente los log-odds de abandono por cada iteración del algoritmo de optimización?

## 2. Metodología y Enfoque Técnico
Contexto conocido: Predicción de churn. Reto: Resolver el problema de clasificación binaria programando el algoritmo de optimización (Descenso de Gradiente o Newton-Raphson) desde cero para Regresión Logística.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Ventas / Churn', 'Inverso', 'Planeación', '{"catalog_id": 35, "pregunta_general": "\u00bfC\u00f3mo cambian exactamente los log-odds de abandono por cada iteraci\u00f3n del algoritmo de optimizaci\u00f3n?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(35, 'Por Hacer', 1), (35, 'En Progreso', 2), (35, 'En Revisión', 3), (35, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(35, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 36: Elasticidad Precio y Multiplicadores de Lagrange
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (36, 'Elasticidad Precio y Multiplicadores de Lagrange', 'Contexto conocido: La optimización de precios. Reto: Plantear el modelo de optimización convexa y resolver analíticamente los multiplicadores de Lagrange antes de delegarlo a un solver numérico.', '', '# PJ-36 — Elasticidad Precio y Multiplicadores de Lagrange

> **Eje:** Inverso | **Tema:** Retail / Pricing | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cuál es el precio óptimo teórico que maximiza el ingreso sujeto a restricciones estrictas de inventario?

## 2. Metodología y Enfoque Técnico
Contexto conocido: La optimización de precios. Reto: Plantear el modelo de optimización convexa y resolver analíticamente los multiplicadores de Lagrange antes de delegarlo a un solver numérico.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Microservicio consumido por front-end. Recibe ID producto/stock, consulta caché (Redis) y devuelve precio optimizado al instante.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Retail / Pricing', 'Inverso', 'Planeación', '{"catalog_id": 36, "pregunta_general": "\u00bfCu\u00e1l es el precio \u00f3ptimo te\u00f3rico que maximiza el ingreso sujeto a restricciones estrictas de inventario?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Microservicio consumido por front-end. Recibe ID producto/stock, consulta cach\u00e9 (Redis) y devuelve precio optimizado al instante."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(36, 'Por Hacer', 1), (36, 'En Progreso', 2), (36, 'En Revisión', 3), (36, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(36, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 37: Enrutamiento de Fuerza de Ventas (MILP)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (37, 'Enrutamiento de Fuerza de Ventas (MILP)', 'Contexto conocido: Asignación de rutas (TSP/VRP). Reto: Formular el problema como Programación Lineal Entera Mixta (MILP), definiendo el álgebra de las restricciones de conservación de flujo.', '', '# PJ-37 — Enrutamiento de Fuerza de Ventas (MILP)

> **Eje:** Inverso | **Tema:** Ventas / Operaciones | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo se formulan matemáticamente las restricciones espaciales para evitar rutas subóptimas heurísticas?

## 2. Metodología y Enfoque Técnico
Contexto conocido: Asignación de rutas (TSP/VRP). Reto: Formular el problema como Programación Lineal Entera Mixta (MILP), definiendo el álgebra de las restricciones de conservación de flujo.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Event-driven (RabbitMQ/Celery). API recibe solicitud, encola tarea pesada del solver MILP; un worker en contenedor dedicado devuelve la ruta asíncronamente.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Ventas / Operaciones', 'Inverso', 'Planeación', '{"catalog_id": 37, "pregunta_general": "\u00bfC\u00f3mo se formulan matem\u00e1ticamente las restricciones espaciales para evitar rutas sub\u00f3ptimas heur\u00edsticas?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Event-driven (RabbitMQ/Celery). API recibe solicitud, encola tarea pesada del solver MILP; un worker en contenedor dedicado devuelve la ruta as\u00edncronamente."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(37, 'Por Hacer', 1), (37, 'En Progreso', 2), (37, 'En Revisión', 3), (37, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(37, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 38: Tasador Automatizado (Web Scraping + ML)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (38, 'Tasador Automatizado (Web Scraping + ML)', 'Pipeline de recolección de datos automatizado (Selenium/Scrapy) de portales inmobiliarios y modelo de ensamble (XGBoost/LightGBM) para estimar precios.', '', '# PJ-38 — Tasador Automatizado (Web Scraping + ML)

> **Eje:** Abierto | **Tema:** Bienes Raíces / Pricing | **Dificultad:** ★★☆☆☆

---

## 1. Pregunta Central de Negocio
¿Cuál es el valor justo de mercado de una propiedad basado en la oferta actual?

## 2. Metodología y Enfoque Técnico
Pipeline de recolección de datos automatizado (Selenium/Scrapy) de portales inmobiliarios y modelo de ensamble (XGBoost/LightGBM) para estimar precios.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 2, 'Bienes Raíces / Pricing', 'Abierto', 'Planeación', '{"catalog_id": 38, "pregunta_general": "\u00bfCu\u00e1l es el valor justo de mercado de una propiedad basado en la oferta actual?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(38, 'Por Hacer', 1), (38, 'En Progreso', 2), (38, 'En Revisión', 3), (38, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(38, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 39: Segmentación Dinámica RFM
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (39, 'Segmentación Dinámica RFM', 'Análisis Recency, Frequency, Monetary. Clustering particional (K-Means) automatizado en un pipeline diario para disparar campañas de retención.', '', '# PJ-39 — Segmentación Dinámica RFM

> **Eje:** Abierto | **Tema:** Marketing / Ventas | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Quiénes son los clientes VIP y quiénes están en riesgo de deserción hoy?

## 2. Metodología y Enfoque Técnico
Análisis Recency, Frequency, Monetary. Clustering particional (K-Means) automatizado en un pipeline diario para disparar campañas de retención.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Marketing / Ventas', 'Abierto', 'Planeación', '{"catalog_id": 39, "pregunta_general": "\u00bfQui\u00e9nes son los clientes VIP y qui\u00e9nes est\u00e1n en riesgo de deserci\u00f3n hoy?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(39, 'Por Hacer', 1), (39, 'En Progreso', 2), (39, 'En Revisión', 3), (39, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(39, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 40: Valuación Estocástica con Opciones Reales
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (40, 'Valuación Estocástica con Opciones Reales', 'Simulación Monte Carlo sobre variables operativas y modelado con árboles binomiales para cuantificar la flexibilidad estratégica (opción de abandonar o expandir) ante volatilidad.', '', '# PJ-40 — Valuación Estocástica con Opciones Reales

> **Eje:** Abierto | **Tema:** Viabilidad Financiera | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Bajo qué escenarios operativos un modelo de negocio aparentemente rentable destruye valor a largo plazo?

## 2. Metodología y Enfoque Técnico
Simulación Monte Carlo sobre variables operativas y modelado con árboles binomiales para cuantificar la flexibilidad estratégica (opción de abandonar o expandir) ante volatilidad.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Viabilidad Financiera', 'Abierto', 'Planeación', '{"catalog_id": 40, "pregunta_general": "\u00bfBajo qu\u00e9 escenarios operativos un modelo de negocio aparentemente rentable destruye valor a largo plazo?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(40, 'Por Hacer', 1), (40, 'En Progreso', 2), (40, 'En Revisión', 3), (40, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(40, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 41: Scorecard de Crédito Tradicional (WoE/IV)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (41, 'Scorecard de Crédito Tradicional (WoE/IV)', 'Desarrollo de un modelo de score crediticio normativo. Transformación de variables por Weight of Evidence (WoE) y selección por Information Value (IV) en Regresión Logística.', '', '# PJ-41 — Scorecard de Crédito Tradicional (WoE/IV)

> **Eje:** Inverso | **Tema:** Riesgo Crediticio | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo explicar matemáticamente el rechazo de un crédito a un regulador sin usar modelos de caja negra?

## 2. Metodología y Enfoque Técnico
Desarrollo de un modelo de score crediticio normativo. Transformación de variables por Weight of Evidence (WoE) y selección por Information Value (IV) en Regresión Logística.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** API REST stateless. Recibe payload JSON (transaccional/demográfico), devuelve dictamen crediticio en milisegundos. Integración directa con core bancario.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Riesgo Crediticio', 'Inverso', 'Planeación', '{"catalog_id": 41, "pregunta_general": "\u00bfC\u00f3mo explicar matem\u00e1ticamente el rechazo de un cr\u00e9dito a un regulador sin usar modelos de caja negra?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "API REST stateless. Recibe payload JSON (transaccional/demogr\u00e1fico), devuelve dictamen crediticio en milisegundos. Integraci\u00f3n directa con core bancario."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(41, 'Por Hacer', 1), (41, 'En Progreso', 2), (41, 'En Revisión', 3), (41, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(41, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 42: Dashboard de Telemetría Financiera
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (42, 'Dashboard de Telemetría Financiera', 'ETL automatizado conectado a APIs públicas o bases SQL, visualizado mediante Streamlit o Dash, enfocado en indicadores actuariales y financieros.', '', '# PJ-42 — Dashboard de Telemetría Financiera

> **Eje:** Abierto | **Tema:** Inteligencia de Negocios | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo consolidar flujos de caja y proyecciones de ventas en una sola interfaz interactiva?

## 2. Metodología y Enfoque Técnico
ETL automatizado conectado a APIs públicas o bases SQL, visualizado mediante Streamlit o Dash, enfocado en indicadores actuariales y financieros.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Inteligencia de Negocios', 'Abierto', 'Planeación', '{"catalog_id": 42, "pregunta_general": "\u00bfC\u00f3mo consolidar flujos de caja y proyecciones de ventas en una sola interfaz interactiva?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(42, 'Por Hacer', 1), (42, 'En Progreso', 2), (42, 'En Revisión', 3), (42, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(42, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 43: Detección de Fraude Topológico en Redes de Pago
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (43, 'Detección de Fraude Topológico en Redes de Pago', 'Implementación de Redes Neuronales de Grafos Temporales (TGN) sobre bases de pagos distribuidos para capturar patrones estructurales evadidos por modelos tabulares.', '', '# PJ-43 — Detección de Fraude Topológico en Redes de Pago

> **Eje:** Abierto | **Tema:** Riesgo Transaccional (GNN) | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo identificar anillos de lavado de dinero estructurando secuencias de pagos como grafos dinámicos?

## 2. Metodología y Enfoque Técnico
Implementación de Redes Neuronales de Grafos Temporales (TGN) sobre bases de pagos distribuidos para capturar patrones estructurales evadidos por modelos tabulares.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Servicio gRPC de latencia ultra baja. Intercepta transacción, extrae subgrafo (Neo4j) y ejecuta inferencia GNN para bloqueo pre-compensación.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Riesgo Transaccional (GNN)', 'Abierto', 'Planeación', '{"catalog_id": 43, "pregunta_general": "\u00bfC\u00f3mo identificar anillos de lavado de dinero estructurando secuencias de pagos como grafos din\u00e1micos?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Servicio gRPC de latencia ultra baja. Intercepta transacci\u00f3n, extrae subgrafo (Neo4j) y ejecuta inferencia GNN para bloqueo pre-compensaci\u00f3n."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(43, 'Por Hacer', 1), (43, 'En Progreso', 2), (43, 'En Revisión', 3), (43, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(43, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 44: Continued Pre-training para Lenguaje Bancario
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (44, 'Continued Pre-training para Lenguaje Bancario', 'Ejecución de Supervised Fine-Tuning (SFT) y Parameter-Efficient Fine-Tuning (LoRA) sobre un LLM open-source utilizando corpus de Basilea y manuales de riesgo.', '', '# PJ-44 — Continued Pre-training para Lenguaje Bancario

> **Eje:** Abierto | **Tema:** NLP Financiero (LLM) | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo adaptar un modelo fundacional para que comprenda el argot de riesgo crediticio y normativas bancarias?

## 2. Metodología y Enfoque Técnico
Ejecución de Supervised Fine-Tuning (SFT) y Parameter-Efficient Fine-Tuning (LoRA) sobre un LLM open-source utilizando corpus de Basilea y manuales de riesgo.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Media (APIs o Inferencia Batch)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'NLP Financiero (LLM)', 'Abierto', 'Planeación', '{"catalog_id": 44, "pregunta_general": "\u00bfC\u00f3mo adaptar un modelo fundacional para que comprenda el argot de riesgo crediticio y normativas bancarias?", "despliegue": "Media (APIs o Inferencia Batch)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(44, 'Por Hacer', 1), (44, 'En Progreso', 2), (44, 'En Revisión', 3), (44, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(44, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 45: Ingeniería Inversa de Atención en Transformers Financieros
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (45, 'Ingeniería Inversa de Atención en Transformers Financieros', 'Extraer y mapear analíticamente los tensores de atención de un Transformer entrenado en secuencias de gastos (Behavioral Scoring) para extraer reglas crediticias interpretables.', '', '# PJ-45 — Ingeniería Inversa de Atención en Transformers Financieros

> **Eje:** Inverso | **Tema:** Scoring Secuencial | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Qué patrones transaccionales empujan exactamente los pesos de atención hacia el rechazo de crédito?

## 2. Metodología y Enfoque Técnico
Extraer y mapear analíticamente los tensores de atención de un Transformer entrenado en secuencias de gastos (Behavioral Scoring) para extraer reglas crediticias interpretables.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** API REST stateless. Recibe payload JSON (transaccional/demográfico), devuelve dictamen crediticio en milisegundos. Integración directa con core bancario.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Scoring Secuencial', 'Inverso', 'Planeación', '{"catalog_id": 45, "pregunta_general": "\u00bfQu\u00e9 patrones transaccionales empujan exactamente los pesos de atenci\u00f3n hacia el rechazo de cr\u00e9dito?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "API REST stateless. Recibe payload JSON (transaccional/demogr\u00e1fico), devuelve dictamen crediticio en milisegundos. Integraci\u00f3n directa con core bancario."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(45, 'Por Hacer', 1), (45, 'En Progreso', 2), (45, 'En Revisión', 3), (45, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(45, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 46: Vulnerabilidad del Tokenizer en Estados Financieros
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (46, 'Vulnerabilidad del Tokenizer en Estados Financieros', 'Análisis algebraico de la dispersión del subword-tokenization (BPE) en matrices numéricas. Desarrollo de una estrategia de tokenización estructurada para alineación estricta de dígitos.', '', '# PJ-46 — Vulnerabilidad del Tokenizer en Estados Financieros

> **Eje:** Inverso | **Tema:** Arquitectura LLM | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Por qué los LLMs fallan catastróficamente al hacer inferencia matemática sobre series temporales y balances?

## 2. Metodología y Enfoque Técnico
Análisis algebraico de la dispersión del subword-tokenization (BPE) en matrices numéricas. Desarrollo de una estrategia de tokenización estructurada para alineación estricta de dígitos.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Arquitectura LLM', 'Inverso', 'Planeación', '{"catalog_id": 46, "pregunta_general": "\u00bfPor qu\u00e9 los LLMs fallan catastr\u00f3ficamente al hacer inferencia matem\u00e1tica sobre series temporales y balances?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(46, 'Por Hacer', 1), (46, 'En Progreso', 2), (46, 'En Revisión', 3), (46, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(46, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 47: Simulación de Shocks de Liquidez con Agentes
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (47, 'Simulación de Shocks de Liquidez con Agentes', 'Despliegue de múltiples agentes LLM independientes actuando como nodos interbancarios, optimizando funciones de utilidad no lineales en un entorno de mercado simulado.', '', '# PJ-47 — Simulación de Shocks de Liquidez con Agentes

> **Eje:** Abierto | **Tema:** Sistemas Multi-Agente (LLM) | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo modelar el contagio cuando instituciones interactúan bajo diferentes aversiones al riesgo y límites de capital?

## 2. Metodología y Enfoque Técnico
Despliegue de múltiples agentes LLM independientes actuando como nodos interbancarios, optimizando funciones de utilidad no lineales en un entorno de mercado simulado.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Sistemas Multi-Agente (LLM)', 'Abierto', 'Planeación', '{"catalog_id": 47, "pregunta_general": "\u00bfC\u00f3mo modelar el contagio cuando instituciones interact\u00faan bajo diferentes aversiones al riesgo y l\u00edmites de capital?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(47, 'Por Hacer', 1), (47, 'En Progreso', 2), (47, 'En Revisión', 3), (47, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(47, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 48: Detección de Colusión Financiera mediante Homología Persistente
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (48, 'Detección de Colusión Financiera mediante Homología Persistente', 'Aplicación de topología algebraica (TDA) para encontrar anillos de lavado invariantes a deformaciones continuas de los datos, sustituyendo el clustering clásico.', '', '# PJ-48 — Detección de Colusión Financiera mediante Homología Persistente

> **Eje:** Inverso | **Tema:** Matemáticas Avanzadas (Topología) | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo detectar estructuras de fraude multidimensionales ocultas en nubes de puntos de transacciones?

## 2. Metodología y Enfoque Técnico
Aplicación de topología algebraica (TDA) para encontrar anillos de lavado invariantes a deformaciones continuas de los datos, sustituyendo el clustering clásico.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Matemáticas Avanzadas (Topología)', 'Inverso', 'Planeación', '{"catalog_id": 48, "pregunta_general": "\u00bfC\u00f3mo detectar estructuras de fraude multidimensionales ocultas en nubes de puntos de transacciones?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(48, 'Por Hacer', 1), (48, 'En Progreso', 2), (48, 'En Revisión', 3), (48, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(48, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 49: Decodificación de Regímenes de Volatilidad Latente (Viterbi)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (49, 'Decodificación de Regímenes de Volatilidad Latente (Viterbi)', 'Programación algorítmica desde cero de Expectation-Maximization (Baum-Welch) y el Filtro de Viterbi para descubrir regímenes financieros ocultos.', '', '# PJ-49 — Decodificación de Regímenes de Volatilidad Latente (Viterbi)

> **Eje:** Inverso | **Tema:** Modelado Probabilístico (HMM) | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo reconstruir la secuencia más probable de estados del mercado a partir de retornos diarios?

## 2. Metodología y Enfoque Técnico
Programación algorítmica desde cero de Expectation-Maximization (Baum-Welch) y el Filtro de Viterbi para descubrir regímenes financieros ocultos.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Modelado Probabilístico (HMM)', 'Inverso', 'Planeación', '{"catalog_id": 49, "pregunta_general": "\u00bfC\u00f3mo reconstruir la secuencia m\u00e1s probable de estados del mercado a partir de retornos diarios?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(49, 'Por Hacer', 1), (49, 'En Progreso', 2), (49, 'En Revisión', 3), (49, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(49, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 50: Frontera entre Ruido Estocástico y Caos Determinista
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (50, 'Frontera entre Ruido Estocástico y Caos Determinista', 'Extracción del exponente de Lyapunov y la dimensión de correlación sobre series de alta frecuencia para comprobar predictibilidad a corto plazo.', '', '# PJ-50 — Frontera entre Ruido Estocástico y Caos Determinista

> **Eje:** Inverso | **Tema:** Matemáticas Financieras | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Tienen los retornos intradiarios una estructura fractal oculta antes de colapsar en entropía?

## 2. Metodología y Enfoque Técnico
Extracción del exponente de Lyapunov y la dimensión de correlación sobre series de alta frecuencia para comprobar predictibilidad a corto plazo.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Matemáticas Financieras', 'Inverso', 'Planeación', '{"catalog_id": 50, "pregunta_general": "\u00bfTienen los retornos intradiarios una estructura fractal oculta antes de colapsar en entrop\u00eda?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(50, 'Por Hacer', 1), (50, 'En Progreso', 2), (50, 'En Revisión', 3), (50, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(50, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 51: Ingeniería Inversa de la Retropropagación Vectorial
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (51, 'Ingeniería Inversa de la Retropropagación Vectorial', 'Derivación analítica del Jacobiano de una capa de red profunda y programación de la multiplicación tensorial en C++/NumPy sin autograd.', '', '# PJ-51 — Ingeniería Inversa de la Retropropagación Vectorial

> **Eje:** Inverso | **Tema:** Arquitectura de Redes | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo opera exactamente el gradiente en una capa de atención (Transformer)?

## 2. Metodología y Enfoque Técnico
Derivación analítica del Jacobiano de una capa de red profunda y programación de la multiplicación tensorial en C++/NumPy sin autograd.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Arquitectura de Redes', 'Inverso', 'Planeación', '{"catalog_id": 51, "pregunta_general": "\u00bfC\u00f3mo opera exactamente el gradiente en una capa de atenci\u00f3n (Transformer)?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(51, 'Por Hacer', 1), (51, 'En Progreso', 2), (51, 'En Revisión', 3), (51, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(51, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 52: Optimización Secuencial con Bandidos Multibrazo (MAB)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (52, 'Optimización Secuencial con Bandidos Multibrazo (MAB)', 'Desarrollo de un motor de Muestreo de Thompson con actualización dinámica de distribuciones Beta/Dirichlet conjugadas.', '', '# PJ-52 — Optimización Secuencial con Bandidos Multibrazo (MAB)

> **Eje:** Abierto | **Tema:** Investigación de Operaciones | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo maximizar conversiones sin esperar el tamaño de muestra de un A/B testing frecuentista?

## 2. Metodología y Enfoque Técnico
Desarrollo de un motor de Muestreo de Thompson con actualización dinámica de distribuciones Beta/Dirichlet conjugadas.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** API stateful. Mantiene hiperparámetros en Redis, re-enruta tráfico de usuarios en tiempo real maximizando conversiones.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Investigación de Operaciones', 'Abierto', 'Planeación', '{"catalog_id": 52, "pregunta_general": "\u00bfC\u00f3mo maximizar conversiones sin esperar el tama\u00f1o de muestra de un A/B testing frecuentista?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "API stateful. Mantiene hiperpar\u00e1metros en Redis, re-enruta tr\u00e1fico de usuarios en tiempo real maximizando conversiones."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(52, 'Por Hacer', 1), (52, 'En Progreso', 2), (52, 'En Revisión', 3), (52, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(52, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 53: Optimización de Portafolios con QAOA
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (53, 'Optimización de Portafolios con QAOA', 'Programación del Quantum Approximate Optimization Algorithm (QAOA) en Qiskit sobre restricciones reales de un portafolio de inversión.', '', '# PJ-53 — Optimización de Portafolios con QAOA

> **Eje:** Abierto | **Tema:** Computación Cuántica | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo resolver restricciones de cardinalidad NP-Hard superando los solvers clásicos?

## 2. Metodología y Enfoque Técnico
Programación del Quantum Approximate Optimization Algorithm (QAOA) en Qiskit sobre restricciones reales de un portafolio de inversión.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Computación Cuántica', 'Abierto', 'Planeación', '{"catalog_id": 53, "pregunta_general": "\u00bfC\u00f3mo resolver restricciones de cardinalidad NP-Hard superando los solvers cl\u00e1sicos?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(53, 'Por Hacer', 1), (53, 'En Progreso', 2), (53, 'En Revisión', 3), (53, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(53, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 54: Vulnerabilidad Criptográfica Financiera
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (54, 'Vulnerabilidad Criptográfica Financiera', 'Implementación del algoritmo de Grover sobre un simulador de ruido cuántico evaluando la degradación de seguridad en funciones hash.', '', '# PJ-54 — Vulnerabilidad Criptográfica Financiera

> **Eje:** Inverso | **Tema:** Computación Cuántica | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cuánta entropía real reduce un ataque cuántico en hashes de transacciones financieras?

## 2. Metodología y Enfoque Técnico
Implementación del algoritmo de Grover sobre un simulador de ruido cuántico evaluando la degradación de seguridad en funciones hash.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Computación Cuántica', 'Inverso', 'Planeación', '{"catalog_id": 54, "pregunta_general": "\u00bfCu\u00e1nta entrop\u00eda real reduce un ataque cu\u00e1ntico en hashes de transacciones financieras?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(54, 'Por Hacer', 1), (54, 'En Progreso', 2), (54, 'En Revisión', 3), (54, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(54, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 55: Trazabilidad de Modelos Estocásticos (DVC + MLflow)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (55, 'Trazabilidad de Modelos Estocásticos (DVC + MLflow)', 'Construcción de un pipeline CI/CD funcional que versiona datos de siniestros (DVC) y registra la convergencia de simulaciones paramétricas (MLflow).', '', '# PJ-55 — Trazabilidad de Modelos Estocásticos (DVC + MLflow)

> **Eje:** Abierto | **Tema:** MLOps / Arquitectura | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo gestionar mutaciones en datasets masivos de siniestros garantizando reproducibilidad actuarial?

## 2. Metodología y Enfoque Técnico
Construcción de un pipeline CI/CD funcional que versiona datos de siniestros (DVC) y registra la convergencia de simulaciones paramétricas (MLflow).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Pipeline CI/CD continuo orquestado en contenedores para reentrenamiento batch automatizado.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'MLOps / Arquitectura', 'Abierto', 'Planeación', '{"catalog_id": 55, "pregunta_general": "\u00bfC\u00f3mo gestionar mutaciones en datasets masivos de siniestros garantizando reproducibilidad actuarial?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Pipeline CI/CD continuo orquestado en contenedores para reentrenamiento batch automatizado."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(55, 'Por Hacer', 1), (55, 'En Progreso', 2), (55, 'En Revisión', 3), (55, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(55, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 56: Orquestación de Inferencia Actuarial en Tiempo Real
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (56, 'Orquestación de Inferencia Actuarial en Tiempo Real', 'Empaquetado y despliegue de un modelo actuarial en un clúster Kubernetes local (Minikube), evaluando estrés de carga y latencia.', '', '# PJ-56 — Orquestación de Inferencia Actuarial en Tiempo Real

> **Eje:** Abierto | **Tema:** MLOps / Arquitectura | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo autoescalar un motor de tarificación (pricing) ante picos repentinos de peticiones?

## 2. Metodología y Enfoque Técnico
Empaquetado y despliegue de un modelo actuarial en un clúster Kubernetes local (Minikube), evaluando estrés de carga y latencia.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Clúster orquestado. Expone la API y configura HPA (Horizontal Pod Autoscaler) para balancear picos transaccionales.

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'MLOps / Arquitectura', 'Abierto', 'Planeación', '{"catalog_id": 56, "pregunta_general": "\u00bfC\u00f3mo autoescalar un motor de tarificaci\u00f3n (pricing) ante picos repentinos de peticiones?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Cl\u00faster orquestado. Expone la API y configura HPA (Horizontal Pod Autoscaler) para balancear picos transaccionales."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(56, 'Por Hacer', 1), (56, 'En Progreso', 2), (56, 'En Revisión', 3), (56, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(56, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 57: Control Óptimo de Inventarios (MDP)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (57, 'Control Óptimo de Inventarios (MDP)', 'Formulación de Ecuaciones de Bellman para cadenas de suministro y resolución del Procesos de Decisión de Markov (MDP) por iteración de políticas.', '', '# PJ-57 — Control Óptimo de Inventarios (MDP)

> **Eje:** Abierto | **Tema:** Investigación de Operaciones | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuál es la política óptima matemática de reabastecimiento bajo una demanda puramente estocástica?

## 2. Metodología y Enfoque Técnico
Formulación de Ecuaciones de Bellman para cadenas de suministro y resolución del Procesos de Decisión de Markov (MDP) por iteración de políticas.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Investigación de Operaciones', 'Abierto', 'Planeación', '{"catalog_id": 57, "pregunta_general": "\u00bfCu\u00e1l es la pol\u00edtica \u00f3ptima matem\u00e1tica de reabastecimiento bajo una demanda puramente estoc\u00e1stica?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(57, 'Por Hacer', 1), (57, 'En Progreso', 2), (57, 'En Revisión', 3), (57, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(57, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 58: Calibración Evolutiva de Volatilidad
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (58, 'Calibración Evolutiva de Volatilidad', 'Implementación del algoritmo evolutivo multiobjetivo NSGA-II para calibrar modelos dinámicos locales (ej. SABR).', '', '# PJ-58 — Calibración Evolutiva de Volatilidad

> **Eje:** Abierto | **Tema:** Matemáticas Financieras | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo ajustar la superficie de volatilidad minimizando el error y maximizando la suavidad paramétrica al mismo tiempo?

## 2. Metodología y Enfoque Técnico
Implementación del algoritmo evolutivo multiobjetivo NSGA-II para calibrar modelos dinámicos locales (ej. SABR).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Matemáticas Financieras', 'Abierto', 'Planeación', '{"catalog_id": 58, "pregunta_general": "\u00bfC\u00f3mo ajustar la superficie de volatilidad minimizando el error y maximizando la suavidad param\u00e9trica al mismo tiempo?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(58, 'Por Hacer', 1), (58, 'En Progreso', 2), (58, 'En Revisión', 3), (58, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(58, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 59: Operador de Koopman en Series Temporales
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (59, 'Operador de Koopman en Series Temporales', 'Descomposición espectral basada en datos (Dynamic Mode Decomposition - DMD) para modelar dinámicas en espacios de dimensionalidad superior.', '', '# PJ-59 — Operador de Koopman en Series Temporales

> **Eje:** Abierto | **Tema:** Matemáticas Avanzadas | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo linealizar dinámicas financieras altamente no lineales para predecir futuros retornos?

## 2. Metodología y Enfoque Técnico
Descomposición espectral basada en datos (Dynamic Mode Decomposition - DMD) para modelar dinámicas en espacios de dimensionalidad superior.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Matemáticas Avanzadas', 'Abierto', 'Planeación', '{"catalog_id": 59, "pregunta_general": "\u00bfC\u00f3mo linealizar din\u00e1micas financieras altamente no lineales para predecir futuros retornos?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(59, 'Por Hacer', 1), (59, 'En Progreso', 2), (59, 'En Revisión', 3), (59, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(59, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 60: Arbitraje Estadístico por Cointegración
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (60, 'Arbitraje Estadístico por Cointegración', 'Desarrollo de una estrategia de Pairs Trading aplicando pruebas matemáticas rigurosas de cointegración fraccional sobre series temporales HFT.', '', '# PJ-60 — Arbitraje Estadístico por Cointegración

> **Eje:** Abierto | **Tema:** Estadística Avanzada | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo confirmar la reversión a la media entre dos activos descartando correlaciones espurias?

## 2. Metodología y Enfoque Técnico
Desarrollo de una estrategia de Pairs Trading aplicando pruebas matemáticas rigurosas de cointegración fraccional sobre series temporales HFT.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Estadística Avanzada', 'Abierto', 'Planeación', '{"catalog_id": 60, "pregunta_general": "\u00bfC\u00f3mo confirmar la reversi\u00f3n a la media entre dos activos descartando correlaciones espurias?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(60, 'Por Hacer', 1), (60, 'En Progreso', 2), (60, 'En Revisión', 3), (60, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(60, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 61: Equilibrio de Nash en Mercados de Subastas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (61, 'Equilibrio de Nash en Mercados de Subastas', 'Simulación de un entorno multi-agente donde actores institucionales calibran pujas para evitar la Maldición del Ganador.', '', '# PJ-61 — Equilibrio de Nash en Mercados de Subastas

> **Eje:** Inverso | **Tema:** Teoría de Juegos | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cuáles son las estrategias dominantes al pujar bonos institucionales bajo información asimétrica?

## 2. Metodología y Enfoque Técnico
Simulación de un entorno multi-agente donde actores institucionales calibran pujas para evitar la Maldición del Ganador.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Teoría de Juegos', 'Inverso', 'Planeación', '{"catalog_id": 61, "pregunta_general": "\u00bfCu\u00e1les son las estrategias dominantes al pujar bonos institucionales bajo informaci\u00f3n asim\u00e9trica?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(61, 'Por Hacer', 1), (61, 'En Progreso', 2), (61, 'En Revisión', 3), (61, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(61, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 62: Dinámica de Población bajo Shocks Epidemiológicos
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (62, 'Dinámica de Población bajo Shocks Epidemiológicos', 'Integración de sistemas de ecuaciones diferenciales epidemiológicas (SIR extendido) interactuando dinámicamente con tablas de decremento múltiple.', '', '# PJ-62 — Dinámica de Población bajo Shocks Epidemiológicos

> **Eje:** Abierto | **Tema:** Modelado Actuarial | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo estresar matemáticamente las reservas matemáticas de vida ante pandemias u olas de calor letales?

## 2. Metodología y Enfoque Técnico
Integración de sistemas de ecuaciones diferenciales epidemiológicas (SIR extendido) interactuando dinámicamente con tablas de decremento múltiple.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Modelado Actuarial', 'Abierto', 'Planeación', '{"catalog_id": 62, "pregunta_general": "\u00bfC\u00f3mo estresar matem\u00e1ticamente las reservas matem\u00e1ticas de vida ante pandemias u olas de calor letales?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(62, 'Por Hacer', 1), (62, 'En Progreso', 2), (62, 'En Revisión', 3), (62, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(62, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 63: Atribución Causal en Riesgos Climáticos
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (63, 'Atribución Causal en Riesgos Climáticos', 'Implementación de inferencia causal estructural bayesiana sobre grafos acíclicos dirigidos (DAGs) de reclamaciones por sequía.', '', '# PJ-63 — Atribución Causal en Riesgos Climáticos

> **Eje:** Inverso | **Tema:** Estadística Avanzada | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Qué proporción de los siniestros agrícolas es puramente atribuible al shock térmico aislando subsidios y mercado?

## 2. Metodología y Enfoque Técnico
Implementación de inferencia causal estructural bayesiana sobre grafos acíclicos dirigidos (DAGs) de reclamaciones por sequía.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Estadística Avanzada', 'Inverso', 'Planeación', '{"catalog_id": 63, "pregunta_general": "\u00bfQu\u00e9 proporci\u00f3n de los siniestros agr\u00edcolas es puramente atribuible al shock t\u00e9rmico aislando subsidios y mercado?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(63, 'Por Hacer', 1), (63, 'En Progreso', 2), (63, 'En Revisión', 3), (63, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(63, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 64: Supervivencia Penalizada en Seguros Médicos
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (64, 'Supervivencia Penalizada en Seguros Médicos', 'Modificación analítica de los modelos de riesgos proporcionales (Cox Proportional Hazards) introduciendo penalización matricial L1/L2 (Lasso/Ridge).', '', '# PJ-64 — Supervivencia Penalizada en Seguros Médicos

> **Eje:** Abierto | **Tema:** Estadística Avanzada | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo seleccionar variables predictivas críticas en historiales clínicos de alta dimensionalidad (p > n)?

## 2. Metodología y Enfoque Técnico
Modificación analítica de los modelos de riesgos proporcionales (Cox Proportional Hazards) introduciendo penalización matricial L1/L2 (Lasso/Ridge).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts/Notebooks)
- **Escalabilidad:** Local/Batch (No aplica microservicio)

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Estadística Avanzada', 'Abierto', 'Planeación', '{"catalog_id": 64, "pregunta_general": "\u00bfC\u00f3mo seleccionar variables predictivas cr\u00edticas en historiales cl\u00ednicos de alta dimensionalidad (p > n)?", "despliegue": "Baja (Scripts/Notebooks)", "escalabilidad": "Local/Batch (No aplica microservicio)"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(64, 'Por Hacer', 1), (64, 'En Progreso', 2), (64, 'En Revisión', 3), (64, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(64, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 66: Agente Híbrido de Inteligencia Operativa (Text-to-SQL + RAG)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (66, 'Agente Híbrido de Inteligencia Operativa (Text-to-SQL + RAG)', 'Enrutamiento semántico con lógica ReAct. Text-to-SQL y RAG documental con Cross-Encoder (Reranking). Evaluación cuantitativa del contexto utilizando RAGAS.', '', '# PJ-66 — Agente Híbrido de Inteligencia Operativa (Text-to-SQL + RAG)

> **Eje:** Abierto | **Tema:** IA Generativa (Agentes Multimodales) | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo orquestar consultas estructuradas (SQL) y no estructuradas (PDFs) en un solo punto erradicando alucinaciones?

## 2. Metodología y Enfoque Técnico
Enrutamiento semántico con lógica ReAct. Text-to-SQL y RAG documental con Cross-Encoder (Reranking). Evaluación cuantitativa del contexto utilizando RAGAS.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (Contenedores/Cloud Run)
- **Escalabilidad:** Arquitectura cliente-servidor basada en MCP (Model Context Protocol).

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'IA Generativa (Agentes Multimodales)', 'Abierto', 'Planeación', '{"catalog_id": 66, "pregunta_general": "\u00bfC\u00f3mo orquestar consultas estructuradas (SQL) y no estructuradas (PDFs) en un solo punto erradicando alucinaciones?", "despliegue": "Alta (Contenedores/Cloud Run)", "escalabilidad": "Arquitectura cliente-servidor basada en MCP (Model Context Protocol)."}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(66, 'Por Hacer', 1), (66, 'En Progreso', 2), (66, 'En Revisión', 3), (66, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(66, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 68: Artcraft
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (68, 'Artcraft', 'Creación de una versión personal para entorno empresarial orientada a la optimización de prompts y flujos de IA.', '', '# PJ-68 — Artcraft

> **Eje:** Abierto | **Tema:** LLMOps | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo optimizar el flujo de trabajo de IA para entornos corporativos restringidos?

## 2. Metodología y Enfoque Técnico
Creación de una versión personal para entorno empresarial orientada a la optimización de prompts y flujos de IA.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Media (Cloud)
- **Escalabilidad:** Local / API Rest

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'LLMOps', 'Abierto', 'Planeación', '{"catalog_id": 68, "pregunta_general": "\u00bfC\u00f3mo optimizar el flujo de trabajo de IA para entornos corporativos restringidos?", "despliegue": "Media (Cloud)", "escalabilidad": "Local / API Rest"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(68, 'Por Hacer', 1), (68, 'En Progreso', 2), (68, 'En Revisión', 3), (68, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(68, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 69: Block Blast Predatorio
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (69, 'Block Blast Predatorio', 'Análisis de comportamiento predictivo (Gradient Boosting) para identificar y exponer patrones de diseño predatorio en el juego.', '', '# PJ-69 — Block Blast Predatorio

> **Eje:** Backlog | **Tema:** Machine Learning | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Existen patrones algorítmicos diseñados para maximizar la retención del usuario forzando microtransacciones?

## 2. Metodología y Enfoque Técnico
Análisis de comportamiento predictivo (Gradient Boosting) para identificar y exponer patrones de diseño predatorio en el juego.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Notebooks)
- **Escalabilidad:** Local / Batch

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Machine Learning', 'Backlog', 'Planeación', '{"catalog_id": 69, "pregunta_general": "\u00bfExisten patrones algor\u00edtmicos dise\u00f1ados para maximizar la retenci\u00f3n del usuario forzando microtransacciones?", "despliegue": "Baja (Notebooks)", "escalabilidad": "Local / Batch"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(69, 'Por Hacer', 1), (69, 'En Progreso', 2), (69, 'En Revisión', 3), (69, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(69, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 70: Godot Forge AI
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (70, 'Godot Forge AI', 'IA asistente integrada en Godot mediante RAG con acceso a documentación oficial; asiste en GDScript de forma iterativa.', '', '# PJ-70 — Godot Forge AI

> **Eje:** Forja | **Tema:** RAG / Game Dev | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Cómo integrar asistencia de código IA contextualizada dentro de un motor gráfico?

## 2. Metodología y Enfoque Técnico
IA asistente integrada en Godot mediante RAG con acceso a documentación oficial; asiste en GDScript de forma iterativa.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Media (Integración API)
- **Escalabilidad:** API Externa / Plugin

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'RAG / Game Dev', 'Forja', 'Planeación', '{"catalog_id": 70, "pregunta_general": "\u00bfC\u00f3mo integrar asistencia de c\u00f3digo IA contextualizada dentro de un motor gr\u00e1fico?", "despliegue": "Media (Integraci\u00f3n API)", "escalabilidad": "API Externa / Plugin"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(70, 'Por Hacer', 1), (70, 'En Progreso', 2), (70, 'En Revisión', 3), (70, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(70, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 71: Telemetría de mi Cloud (Datoide)
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (71, 'Telemetría de mi Cloud (Datoide)', 'Sistema de observabilidad y monitoreo de latencia/rendimiento para la arquitectura Flat-File CMS de Datoide.', '', '# PJ-71 — Telemetría de mi Cloud (Datoide)

> **Eje:** Backlog | **Tema:** Observabilidad | **Dificultad:** ★★★☆☆

---

## 1. Pregunta Central de Negocio
¿Cómo monitorear el rendimiento en una arquitectura sin base de datos (Flat-File CMS)?

## 2. Metodología y Enfoque Técnico
Sistema de observabilidad y monitoreo de latencia/rendimiento para la arquitectura Flat-File CMS de Datoide.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Media (Hostinger)
- **Escalabilidad:** Scripts / Logs

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 3, 'Observabilidad', 'Backlog', 'Planeación', '{"catalog_id": 71, "pregunta_general": "\u00bfC\u00f3mo monitorear el rendimiento en una arquitectura sin base de datos (Flat-File CMS)?", "despliegue": "Media (Hostinger)", "escalabilidad": "Scripts / Logs"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(71, 'Por Hacer', 1), (71, 'En Progreso', 2), (71, 'En Revisión', 3), (71, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(71, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 72: Casino Free
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (72, 'Casino Free', 'Desarrollo de un simulador de casino gratuito diseñado como herramienta terapéutica para mitigar y analizar la ludopatía.', '', '# PJ-72 — Casino Free

> **Eje:** Backlog | **Tema:** Simulación / Ética | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Puede un simulador de apuestas sin valor monetario reducir los impulsos de la ludopatía?

## 2. Metodología y Enfoque Técnico
Desarrollo de un simulador de casino gratuito diseñado como herramienta terapéutica para mitigar y analizar la ludopatía.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (App/Web)
- **Escalabilidad:** Web / Móvil

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Simulación / Ética', 'Backlog', 'Planeación', '{"catalog_id": 72, "pregunta_general": "\u00bfPuede un simulador de apuestas sin valor monetario reducir los impulsos de la ludopat\u00eda?", "despliegue": "Alta (App/Web)", "escalabilidad": "Web / M\u00f3vil"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(72, 'Por Hacer', 1), (72, 'En Progreso', 2), (72, 'En Revisión', 3), (72, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(72, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 73: Pricing de Materias Primas
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (73, 'Pricing de Materias Primas', 'Modelo predictivo de series de tiempo para optimizar el inventario y prever fluctuaciones de precios en la industria del acero.', '', '# PJ-73 — Pricing de Materias Primas

> **Eje:** Backlog | **Tema:** Series de Tiempo | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo saber cuándo ordenar nueva materia prima para una industria de acero?

## 2. Metodología y Enfoque Técnico
Modelo predictivo de series de tiempo para optimizar el inventario y prever fluctuaciones de precios en la industria del acero.

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Baja (Scripts)
- **Escalabilidad:** Local / Batch

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'Series de Tiempo', 'Backlog', 'Planeación', '{"catalog_id": 73, "pregunta_general": "\u00bfC\u00f3mo saber cu\u00e1ndo ordenar nueva materia prima para una industria de acero?", "despliegue": "Baja (Scripts)", "escalabilidad": "Local / Batch"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(73, 'Por Hacer', 1), (73, 'En Progreso', 2), (73, 'En Revisión', 3), (73, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(73, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 74: Terraform
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (74, 'Terraform', 'Plantillas de Infraestructura como Código (IaC) para estandarizar y automatizar despliegues en Google Cloud (aplicable a Higgings).', '', '# PJ-74 — Terraform

> **Eje:** Backlog | **Tema:** DevOps / IaC | **Dificultad:** ★★★★☆

---

## 1. Pregunta Central de Negocio
¿Cómo estandarizar y automatizar la infraestructura en la nube para un proyecto de IA?

## 2. Metodología y Enfoque Técnico
Plantillas de Infraestructura como Código (IaC) para estandarizar y automatizar despliegues en Google Cloud (aplicable a Higgings).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Alta (GCP)
- **Escalabilidad:** Cloud Run / IAM

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 4, 'DevOps / IaC', 'Backlog', 'Planeación', '{"catalog_id": 74, "pregunta_general": "\u00bfC\u00f3mo estandarizar y automatizar la infraestructura en la nube para un proyecto de IA?", "despliegue": "Alta (GCP)", "escalabilidad": "Cloud Run / IAM"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(74, 'Por Hacer', 1), (74, 'En Progreso', 2), (74, 'En Revisión', 3), (74, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(74, 'Sprint 1', 'Sprint inicial', 'active', 10);

-- Proyecto 75: Generación 3D Paramétrica
INSERT INTO projects (id, name, description, github_url, readme_markdown, difficulty, theme, axis, status, extra_data, created_at, updated_at)
VALUES (75, 'Generación 3D Paramétrica', 'Motor para generar modelos 3D y planos específicos (posible extensión de Artcraft orientada a diseño de productos físicos).', '', '# PJ-75 — Generación 3D Paramétrica

> **Eje:** Backlog | **Tema:** Diseño Paramétrico | **Dificultad:** ★★★★★

---

## 1. Pregunta Central de Negocio
¿Es posible generar planos y modelos 3D listos para manufactura a partir de inputs de texto?

## 2. Metodología y Enfoque Técnico
Motor para generar modelos 3D y planos específicos (posible extensión de Artcraft orientada a diseño de productos físicos).

## 3. Arquitectura y Despliegue
- **Nivel de Despliegue:** Media (Scripts 3D)
- **Escalabilidad:** Local / Motor Gráfico

---
*Documento autogenerado en Huggins Platform desde catálogo maestro.*
', 5, 'Diseño Paramétrico', 'Backlog', 'Planeación', '{"catalog_id": 75, "pregunta_general": "\u00bfEs posible generar planos y modelos 3D listos para manufactura a partir de inputs de texto?", "despliegue": "Media (Scripts 3D)", "escalabilidad": "Local / Motor Gr\u00e1fico"}', '2026-10-18 20:00:00', '2026-10-18 20:00:00');
INSERT INTO columns (project_id, title, position) VALUES 
(75, 'Por Hacer', 1), (75, 'En Progreso', 2), (75, 'En Revisión', 3), (75, 'Terminado', 4);
INSERT INTO sprints (project_id, name, goal, status, target_points) VALUES 
(75, 'Sprint 1', 'Sprint inicial', 'active', 10);

COMMIT;