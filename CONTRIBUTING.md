# Contribuir al currículo abierto

Este repositorio es la fuente de conocimiento de [llmengineerclub.com](https://llmengineerclub.com).
Una contribución aprobada y fusionada puede convertirse en una lección, laboratorio, ejemplo,
corrección o actualización visible en la plataforma.

## Qué recibe reconocimiento

La web conserva la procedencia mediante la PR fusionada:

- **Creó**: añadió una unidad nueva y sustantiva.
- **Mejoró**: corrigió o amplió material existente con impacto educativo.
- **Revisó**: aprobó técnicamente el cambio con una revisión argumentada.
- **Mantuvo**: actualizó modelos, SDKs, certificaciones o enlaces oficiales.

Se muestra el nombre público, usuario, avatar y enlace al perfil de GitHub, junto con el número y
enlace de la PR. No se atribuye autoría por número de líneas ni se premia el volumen de PRs.

## Antes de abrir una PR

1. Explica el problema educativo que resuelves y a quién bloquea.
2. Enlaza fuentes primarias: documentación oficial, paper o estándar.
3. Mantén los modelos y APIs configurables; no fijes un modelo antiguo como default.
4. Si añades un lab, incluye modo offline o mock siempre que sea razonable.
5. Cubre camino feliz y al menos un error relevante.
6. Nunca incluyas claves, prompts privados, datos personales ni output de clientes.
7. Ejecuta las validaciones indicadas en el README.

Una PR que añada una carpeta `soluciones`, un solucionario completo o una implementación
marcada como respuesta oficial se rechaza automáticamente. Sí son bienvenidos los tests,
rúbricas, pistas graduales y criterios verificables que permitan aprender sin publicar la
respuesta.

### Propuestas para el Club Quiz

Puedes aportar un objetivo evaluable, un escenario base, la dificultad, fuentes y un análisis de
ambigüedad. No publiques una pregunta que ya esté activa ni su combinación exacta de enunciado,
opciones, clave y explicación. Tras el merge, el equipo editorial genera una variante privada,
conserva la atribución de la PR y la somete a revisión antes de incorporarla a D1. Las preguntas
retiradas sí pueden publicarse después como práctica abierta.

El contrato completo está en [`docs/club-quiz-contributions.md`](docs/club-quiz-contributions.md).

## Estructura

- Teoría: `modulo-NN-*/teoria/NN-titulo.md`.
- Laboratorios: `modulo-NN-*/labs/NN_nombre.py`.
- Datos pequeños y ficticios: `modulo-NN-*/labs/data/`.
- Ejercicios y criterios de aceptación: `ejercicios.md`. Las soluciones completas viven
  en un repositorio privado y **no se aceptan** en este repositorio público.
- Certificaciones: `certificaciones/<codigo>/`. Los enunciados y distractores son públicos; no
  añadas una hoja de respuestas. La clave razonada se coordina con el mantenedor fuera de la PR.
- Club Quiz: aporta blueprints públicos siguiendo `docs/club-quiz-contributions.md`; el banco activo
  y sus respuestas nunca se añaden a este repositorio.
- Metadatos de la ruta: `course.json`.
- Traducciones inglesas: `translations/en/<misma-ruta>`, con el manifiesto de hashes
  regenerado mediante `node scripts/translate-content.mjs --path <ruta>`.

Si traduces manualmente, edita la ruta equivalente en `translations/en/` y registra su integridad:

```bash
node scripts/record-human-translation.mjs --path modulo-02-prompt-engineering/README.md
```

No necesitas instalar ni usar el modelo local de traducción para contribuir. El CI comprueba que
código, enlaces, estructura Markdown y AST de los labs sigan siendo equivalentes.

La plataforma genera títulos, rutas y tiempos de lectura a partir de estas convenciones. Renombrar
un archivo publicado cambia su URL: hazlo solo cuando el beneficio compense y descríbelo en la PR.

## Actualizaciones de modelos y certificaciones

Una actualización debe incluir:

- Identificador exacto o nombre oficial.
- Estado: vigente, legacy o histórico.
- Fecha de comprobación.
- URL oficial que sustenta el cambio.
- Impacto sobre labs, datasets y preguntas; cualquier cambio de clave razonada se coordina con el
  mantenedor fuera del historial público.

Los cambios automáticos solo pueden abrir PRs. Una persona experta debe interpretarlos antes del
merge.

## Código ejecutable

El CI de una PR pública nunca recibe secretos. El código contribuido se prueba con mocks y datos
ficticios. Las herramientas que vayan a formar parte del producto web requieren revisión adicional
`trusted-tool`; ningún fragmento del curso se ejecuta directamente en Cloudflare.

## Licencia y publicación

Al contribuir confirmas que puedes aportar el material y aceptas que se publique bajo las licencias
de [LICENSE.md](LICENSE.md), incluida su aparición en llmengineerclub.com con atribución permanente
a tu PR y perfil público de GitHub.
