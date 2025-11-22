#version 410 core

layout (location = 0) in vec4 coord; // igual ao vertex.glsl

uniform mat4 Mvp; // P * V * S * M

void main() {
    gl_Position = Mvp * coord;
}
