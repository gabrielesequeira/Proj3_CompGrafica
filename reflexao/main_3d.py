import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import numpy as np
from camera3d import *
from light import *
from shader import *
from material import *
from transform import *
from node import *
from scene import *
# Importação alterada: Usando Cube em vez de Sphere
from cube import * # Certifique-se de que o módulo cube.py esteja disponível e defina uma classe Cube

# Posição da câmera (ligeiramente ajustada para um novo ângulo)
viewer_pos = glm.vec3(3.0, 4.0, 5.0) 

def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    win = glfw.create_window(800, 600, "Reflexão Planar com Stencil e Cubo", None, None) # Aumentei o tamanho da janela
    if not win:
        glfw.terminate()
        return

    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)
    glfw.swap_interval(1)

    print("OpenGL version: ", glGetString(GL_VERSION))
    initialize(win)

    while not glfw.window_should_close(win):
        display(win)
        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

def initialize(win):
    global camera, scene, shader, plane_shader, plane_vao, plane_vbo

    # Nova cor de fundo: Cinza claro (0.8, 0.8, 0.8, 1.0)
    glClearColor(0.8, 0.8, 0.8, 1.0) 
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_STENCIL_TEST)

    camera = Camera3D(viewer_pos[0], viewer_pos[1], viewer_pos[2])
    arcball = camera.CreateArcball()
    arcball.Attach(win)

    light = Light(viewer_pos[0], viewer_pos[1], viewer_pos[2], 1.0, "camera")
    
    # Novo material: Verde Esmeralda (0.1, 0.8, 0.5)
    emerald_green = Material(0.1, 0.8, 0.5) 

    shader = Shader(light, "camera")
    shader.AttachVertexShader("shaders/vertex.glsl")
    shader.AttachFragmentShader("shaders/fragment.glsl")
    shader.Link()

    plane_shader = Shader()
    plane_shader.AttachVertexShader("shaders/plane_vertex.glsl")
    plane_shader.AttachFragmentShader("shaders/plane_fragment.glsl")
    plane_shader.Link()

    transform = Transform()
    # Ajustei a escala e a posição do cubo
    transform.Scale(0.5, 0.5, 0.5) 
    transform.Translate(-1.0, 0.5, 0.0) 
    
    # Objeto alterado: De Sphere para Cube
    cube = Cube() 

    root = Node(shader, nodes=[
        Node(None, transform, [emerald_green], [cube])
    ])
    scene = Scene(root)

    # Ajustei o tamanho do plano para ser um pouco maior
    plane_vertices = np.array([
        -8.0, 0.0, -8.0,
         8.0, 0.0, -8.0,
         8.0, 0.0,  8.0,
        -8.0, 0.0,  8.0
    ], dtype=np.float32)

    plane_vao = glGenVertexArrays(1)
    plane_vbo = glGenBuffers(1)

    glBindVertexArray(plane_vao)
    glBindBuffer(GL_ARRAY_BUFFER, plane_vbo)
    glBufferData(GL_ARRAY_BUFFER, plane_vertices.nbytes, plane_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

def display(win):
    global scene, camera

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    # 1. Desenhar o refletor no stencil (desativa escrita no buffer de cor/profundidade)
    glEnable(GL_STENCIL_TEST)
    glStencilFunc(GL_NEVER, 1, 0xFF)
    glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
    glDepthMask(GL_FALSE) # Não escreve no buffer de profundidade
    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE) # Não escreve no buffer de cor
    render_plane()
    glDepthMask(GL_TRUE)
    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    # 2. Renderizar cena refletida
    glEnable(GL_STENCIL_TEST)
    glStencilFunc(GL_EQUAL, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
    glEnable(GL_DEPTH_TEST) # Habilitar teste de profundidade para a cena refletida
    render_reflected_scene()
    glDisable(GL_STENCIL_TEST)

    # 3. Renderizar a cena original (objeto acima do plano)
    render_scene()

    # 4. Renderizar o plano refletor com blending/transparência
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Aqui, a cor do plano (com transparência) deve ser definida no seu 'plane_fragment.glsl'
    # Ex: vec4(0.3, 0.5, 0.9, 0.5); // Azul claro e 50% transparente
    render_plane()
    glDisable(GL_BLEND)

def render_plane():
    plane_shader.UseProgram()

    model_matrix = glm.mat4(1.0)
    vp_matrix = camera.GetProjMatrix() * camera.GetViewMatrix()
    mvp_matrix = vp_matrix * model_matrix
    plane_shader.SetUniform("Mvp", mvp_matrix)

    glDisable(GL_CULL_FACE)
    glBindVertexArray(plane_vao)
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
    glBindVertexArray(0)
    glEnable(GL_CULL_FACE)

def render_reflected_scene():
    global scene

    # Matriz de reflexão no plano Y=0
    reflection_matrix = glm.mat4(1.0)
    reflection_matrix[1][1] = -1.0  # Inverte a coordenada Y

    # Inverter a orientação das faces para a reflexão (para que o culling funcione corretamente)
    glFrontFace(GL_CW)

    # Renderizar a cena refletida com a matriz de reflexão
    scene.Render(camera, model_matrix=reflection_matrix)

    # Restaurar a orientação das faces
    glFrontFace(GL_CCW)


def render_scene():
    scene.Render(camera)

def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)

if __name__ == "__main__":
    main()