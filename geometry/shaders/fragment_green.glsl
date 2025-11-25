#version 410

in vec3 fragNormal; // Normal do fragmento recebida do Geometry Shader
in vec3 fragEye;    // Posição do fragmento em relação ao olho

out vec4 color;

void main() {
    // Cor uniforme: A mesma em toda a esfera
    vec3 uniformColor = vec3(0.0, 1.0, 0.0); 

    // Aplica apenas o componente ambiente uniformemente
    vec3 ambient = vec3(0.0, 0.6, 0.0);

    // Resultado final da cor (uniforme para frente e atrás)
    color = vec4(ambient, 1.0);
}
