#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_texcoord_0;

out vec2 uv_0;
out float brightness;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform float in_brightness;

void main() {
    uv_0 = in_texcoord_0;
    brightness = in_brightness;
    gl_Position = m_proj * m_view * m_model * vec4(in_position.xy, in_position.z, 1.0);
}