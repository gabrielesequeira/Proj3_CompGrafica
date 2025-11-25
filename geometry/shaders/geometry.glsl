#version 410

layout(triangles) in;                       // Entrada: Triângulos
layout(triangle_strip, max_vertices = 6) out; // Saída: Triângulos

in vec3 vNormal[]; // Recebido do Vertex Shader
in vec3 vEye[];    // Recebido do Vertex Shader

out vec3 fragNormal; // Saída para o Fragment Shader
out vec3 fragEye;    // Saída para o Fragment Shader

void main() {
    for (int i = 0; i < 3; i++) {
        gl_Position = gl_in[i].gl_Position; // Posição do vértice
        fragNormal = vNormal[i];           // Passa a normal para o Fragment Shader
        fragEye = vEye[i];                 // Passa a posição para o Fragment Shader
        EmitVertex();
    }
    EndPrimitive();
}
