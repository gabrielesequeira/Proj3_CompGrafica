#version 410

in vec3 fragNormal; 
in vec3 fragEye;    

out vec4 color;

void main() {
    vec3 uniformColor = vec3(0.0, 1.0, 0.0); 

    vec3 ambient = vec3(0.0, 0.6, 0.0);

    color = vec4(ambient, 1.0);
}
