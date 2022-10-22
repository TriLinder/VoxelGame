#version 330
// Fragment shader runs once for each pixel in the triangles.
// We are drawing two triangles here creating a quad.
// In values are interpolated between the vertices.
// Sampler reading from a texture channel 0
uniform sampler2D surface;
// The pixel we are writing to the screen
out vec4 f_color;
// Interpolated texture coordinates
in vec2 uv;

void main() {
    // Simply look up the color from the texture
    f_color = texture(surface, vec2(uv.x, uv.y * -1));
    //f_color = vec3(1, 1, 0);
}