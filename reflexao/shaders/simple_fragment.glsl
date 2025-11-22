#version 410 core

out vec4 fragColor;

void main() {
    // Cor da sombra: Cinza escuro
    fragColor = vec4(0.1, 0.1, 0.1, 1.0); 
}#version 410 core

out vec4 fragColor;

void main() {
    // Cor da sombra: Cinza escuro com alpha para blending
    fragColor = vec4(0.05, 0.05, 0.05, 0.6);
}
