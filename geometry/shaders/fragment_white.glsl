#version 410

in vec3 fragNormal; // Recebido do Geometry Shader (não usado aqui)
in vec3 fragEye;    // Recebido do Geometry Shader (não usado aqui)

out vec4 color;

void main() {
    color = vec4(1.0, 1.0, 1.0, 1.0); // Branco sólido
}