#version 410

in vec4 color;
in vec3 vNormal;
in vec3 vEye;

uniform vec4 lpos;
uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform vec4 mamb;
uniform vec4 mdif;
uniform vec4 mspe;
uniform float mshi;

out vec4 fcolor;

void main(void) {
    vec3 lightDir;
    if (lpos.w == 0.0) {
        lightDir = normalize(vec3(lpos));
    } else {
        lightDir = normalize(vec3(lpos) - vEye);
    }

    vec3 N = normalize(vNormal);

    float NdotL = max(dot(N, lightDir), 0.0);
    vec4 diff = mdif * ldif * NdotL;

    vec4 spec = vec4(0.0);
    if (NdotL > 0.0) {
        vec3 viewDir = normalize(-vEye);       
        vec3 reflectDir = reflect(-lightDir, N); 
        float RdotV = max(dot(reflectDir, viewDir), 0.0);
        spec = (mspe * lspe * pow(RdotV, mshi)) * 0.5;
    }

    vec4 ambient = mamb * lamb;

    fcolor = ambient + diff + spec;

    fcolor *= color;
}
