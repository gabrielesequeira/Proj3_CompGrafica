#version 410

layout(location = 0) in vec4 coord;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 texcoord;  // Adicionar coordenadas de textura

uniform mat4 Mv;
uniform mat4 Mn;
uniform mat4 Mvp;

out vec3 vNormal;
out vec3 vEye;
out vec2 vTexcoord;  // Passar as coordenadas de textura para o fragment shader
out vec4 color;

void main(void) {
    vEye = vec3(Mv * coord);
    vNormal = normalize(vec3(Mn * vec4(normal, 0.0)));
    vTexcoord = texcoord;  // Passar coordenadas de textura adiante
    color = vec4(1.0, 1.0, 1.0, 1.0);  // Cor padrão
    gl_Position = Mvp * coord;
}
