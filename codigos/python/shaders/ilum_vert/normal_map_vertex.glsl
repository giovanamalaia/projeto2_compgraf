#version 410 core

layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aTangent;
layout (location = 3) in vec2 aTexCoord;
layout (location = 4) in vec3 aBitangent;

uniform mat4 Mv;
uniform mat4 Mn;
uniform mat4 Mvp;
uniform vec4 lpos; 

out vec2 vTexCoord;
out vec3 vTangentLightPos;  
out vec3 vTangentViewPos;  
out vec3 vTangentFragPos;   

void main()
{
    vec3 vFragPos_view = vec3(Mv * vec4(aPosition, 1.0));
    
    vec3 N_view = normalize(vec3(Mn * vec4(aNormal, 0.0)));
    vec3 T_view = normalize(vec3(Mn * vec4(aTangent, 0.0)));
    vec3 B_view = normalize(cross(N_view, T_view)); // Recalcula B

    vec3 vViewPos_view = vec3(0.0, 0.0, 0.0);
    
    mat3 TBN = transpose(mat3(T_view, B_view, N_view));

    vTangentFragPos  = TBN * vFragPos_view;
    vTangentLightPos = TBN * vec3(lpos);
    vTangentViewPos  = TBN * vViewPos_view;

    vTexCoord = aTexCoord;
    gl_Position = Mvp * vec4(aPosition, 1.0); 
}