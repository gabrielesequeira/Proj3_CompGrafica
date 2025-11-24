#version 410 core

layout (location = 0) in vec4 coord; // usar vec4 para ser consistente com o resto

uniform mat4 Mvp;

void main() {
    gl_Position = Mvp * coord;
}
