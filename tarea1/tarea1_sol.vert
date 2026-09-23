#version 330

in vec3 position;

uniform mat4 u_transform = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec3 fragPos;

void main() {
    fragPos = vec3( position );
    gl_Position = u_projection * u_view * u_transform * vec4(position, 1.0f);
}
