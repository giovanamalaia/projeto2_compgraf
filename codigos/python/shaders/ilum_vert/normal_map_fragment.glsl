#version 410 core

in vec2 vTexCoord;
in vec3 vTangentLightPos;
in vec3 vTangentViewPos;
in vec3 vTangentFragPos;

uniform sampler2D uTexture;   
uniform sampler2D uNormalMap; 

uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform vec4 mamb;
uniform vec4 mdif;
uniform vec4 mspe;
uniform float mshi;     

out vec4 fcolor; 

void main()
{
    vec3 normal_tangent = texture(uNormalMap, vTexCoord).rgb;
    normal_tangent = normalize(normal_tangent * 2.0 - 1.0);

    vec4 texColor = texture(uTexture, vTexCoord);

    vec3 lightDir_tangent = normalize(vTangentLightPos - vTangentFragPos);
    vec3 viewDir_tangent = normalize(vTangentViewPos - vTangentFragPos);
    vec3 halfwayDir_tangent = normalize(lightDir_tangent + viewDir_tangent);

    vec4 ambient = mamb * lamb;
    
    float diff_factor = max(dot(normal_tangent, lightDir_tangent), 0.0);
    vec4 diffuse = mdif * ldif * diff_factor;

    float spec_factor = pow(max(dot(normal_tangent, halfwayDir_tangent), 0.0), mshi);
    vec4 specular = mspe * lspe * spec_factor;

    vec4 lighting = (ambient + diffuse) * texColor + specular;
    
    fcolor = vec4(lighting.rgb, 1.0);
}