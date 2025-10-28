#version 410

layout(location = 0) in vec4 coord;
layout(location = 1) in vec3 normal;
layout(location = 3) in vec2 texcoord;

uniform mat4 Mv; 
uniform mat4 Mn; 
uniform mat4 Mvp;

out vec3 vNormal;
out vec3 vEye;
out vec2 vTexcoord; 

void main (void) 
{
  vEye = vec3(Mv * coord);
  vNormal = normalize(vec3(Mn * vec4(normal, 0.0)));
  vTexcoord = texcoord; 
  gl_Position = Mvp * coord; 
}