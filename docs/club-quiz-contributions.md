# Contribuir al Club Quiz sin publicar sus respuestas

El Club Quiz convierte parte del currículo abierto en una evaluación competitiva. El conocimiento,
los objetivos y la discusión técnica permanecen públicos; el banco de una edición activa no.

## Qué puedes aportar en una PR

- El objetivo de aprendizaje y el dominio que se quiere medir.
- Un escenario o blueprint que describa la decisión profesional, sin convertirlo en la pregunta
  exacta que verá la persona participante.
- Dificultad esperada y tiempo de referencia razonable.
- Fuentes primarias actuales que sustentan la respuesta.
- Riesgos de ambigüedad y conceptos erróneos que deberían detectar los distractores.
- Criterios de retirada o actualización cuando cambie un modelo, SDK, servicio o estándar.

Una propuesta útil permite que otra persona experta construya y audite una variante equivalente;
no necesita incluir el solucionario.

## Qué nunca debe entrar en el repositorio público

- El enunciado exacto de una pregunta activa.
- Su conjunto exacto de opciones o su orden.
- La clave, explicación editorial o mapeo de respuestas.
- Seeds, exportaciones D1 o migraciones del banco competitivo.
- Umbrales internos de moderación, credenciales OAuth o claves de firma.

El CI público no recibe estos materiales ni secretos. Si una PR los incluye accidentalmente, se
retirarán antes del merge; no basta con borrarlos en un commit posterior si ya se publicaron.

## Del merge a la edición activa

1. La PR pública fija el objetivo, las fuentes y la procedencia.
2. El mantenedor crea en el repositorio privado un escenario bilingüe nuevo y remapea las opciones.
3. Una revisión técnica comprueba actualidad, equivalencia ES/EN, dificultad, distractores y una
   única respuesta defendible.
4. Las validaciones impiden que el enunciado activo o su clave aparezcan en el artefacto estático.
5. La pregunta revisada entra en una edición D1 con versión de banco y hash de contenido.
6. Al retirarse, puede publicarse como práctica con corrección razonada.

El proceso no garantiza que toda propuesta se convierta en pregunta activa: primero debe superar
la revisión editorial y equilibrar el pool por dominio y dificultad.

## Atribución permanente

La plataforma conserva el autor y el enlace de la PR que originó el objetivo. También puede
reconocer revisiones técnicas sustantivas. La prueba firmada de cada intento identifica la edición,
la versión del banco, el SHA del currículo y las personas revisoras, pero nunca revela preguntas ni
respuestas activas.

La atribución no depende de ganar el ranking y no se concede por volumen de cambios. Se reconoce
una aportación educativa verificable, con el nombre y perfil públicos que GitHub proporciona para
la PR fusionada.

## Privacidad de quien participa

El reto oficial usa una passkey seudónima para limitar repeticiones sin exigir nombre, email ni
perfil social. La web no usa cookies ni guarda una huella propia, IP o `User-Agent` en su base de
datos. Una comprobación anti-bot procesa señales transitorias antes de usar la passkey. El resultado
queda privado por defecto y, solo después de completar el reto, la persona puede vincular un perfil;
el ranking lo muestra únicamente con consentimiento expreso y moderación aprobada.
