#version 330 core

// ===== COMPLETAR: Defina los valores de entrada y de salida =====

// ================================================================
in vec3 fragPos;
in vec3 fragNormal;
out vec4 outColor;


// La siguiente función se le entrega hecha y no debe modificarla :)
// computeDirectionalLight: calcula el aporte de una luz direccional
// en función de la normal.
// Este aporte permite observar los desniveles del terreno
vec3 computeDirectionalLight(vec3 normal) {
    // dirección de la luz
    vec3 direction = vec3(1, 1, 0);
    // colores de la luz
    vec3 ambient = vec3(0.3, 0.3, 0.3);
    vec3 diffuse = vec3(0.3, 0.3, 0.3);

    // color de la superficie
    vec3 color = vec3(118 / 255.0, 209 / 255.0, 79.0 / 255.0);

    // calculo componente ambiente
    vec3 ambientT = ambient * color;

    // calculo componente difuso
    float diff = max(dot(normal, direction), 0.0);
    vec3 diffuseT = diffuse * (diff * color);

    return (ambientT + diffuseT);
}

// Programa pricipal
void main()
{
    // La normal suele crecer de más, producto de la interpolación entre puntos
    // Por ello, se normaliza
    vec3 normal = normalize(fragNormal);

    // Partimos con el aporte de la luz direccional
    vec3 finalColor = computeDirectionalLight(normal);

    // Logica de la nieve
    // snowFactor será un valor entre 0.0 y 1.0 que determina que tanta nieve hay a esa altura
    // snowHeight será el inicio de la nieve
    // blendZone determina un area de la nieve que será el área de transición
    // donde si fragPos.y - snowHeight = blendZone, entonces el factor es 1.0
    // si fragPos.y - snowHeight = blendZone/2.0, entonces el factor es 0.5
    // si fragPos.y - snowHeight = 0.0, entonces el factor es 0.0
    float snowHeight = 1.0;
    float blendZone = 0.2;
    float snowFactor = clamp((fragPos.y - snowHeight) / blendZone, 0.0, 1.0);

    // Aquí dada la interpolación lineal entre finalColor y vec3(1.0),
    // Entrega el valor para t = snowFactor
    // Es decir, para snowFactor = 0.0 -> finalColor
    //           para snowFactor = 1.0 -> vec3(1.0)
    // y todo entremedio
    finalColor = mix(finalColor, vec3(1.0), snowFactor);

    // Finalmente se agrega la transparencia, que no se utiliza en esta ocasión
    outColor = vec4(finalColor, 1.0);
}
