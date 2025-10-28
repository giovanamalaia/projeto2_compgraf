#version 410

layout(location = 0) in vec4 coord;
layout(location = 1) in vec3 normal;

uniform mat4 Mv;
uniform mat4 Mn;
uniform mat4 Mvp;

out vec3 vNormal;
out vec3 vEye;
out vec4 color;

void main(void) {
    vEye = vec3(Mv * coord);
    vNormal = normalize(vec3(Mn * vec4(normal, 0.0)));
    color = vec4(1.0, 1.0, 1.0, 1.0);
    gl_Position = Mvp * coord;
}
