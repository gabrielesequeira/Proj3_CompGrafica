#version 410

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

uniform mat4 Mvp;   // Matriz de Transformação
uniform mat4 Model; // Matriz do modelo (para calcular normais no espaço do mundo)

out vec3 vNormal;   // Saída para o próximo estágio
out vec3 vEye;      // Saída para o próximo estágio

void main() {
    vNormal = normalize(mat3(transpose(inverse(Model))) * normal); // Normais ajustadas para o espaço do mundo
    vEye = vec3(Model * vec4(position, 1.0));                     // Envia posição no espaço do mundo
    gl_Position = Mvp * vec4(position, 1.0);                     // Transforma a posição
}
