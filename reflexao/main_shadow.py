import glfw
from OpenGL.GL import *
import glm
import numpy as np
import ctypes

# Importações do seu projeto (assumo que estão implementadas)
# Certifique-se de que todas estas classes (Camera3D, Light, Shader, etc.) estão disponíveis
from camera3d import *
from light import *
from shader import *
from material import *
from transform import *
from node import *
from scene import *
from cube import *
from state import *

# Posição da câmera e da luz
viewer_pos = glm.vec3(3.0, 4.0, 5.0)
light_pos = glm.vec3(5.0, 10.0, 5.0)  # Posição da luz para iluminação (não afeta a projeção ortogonal da sombra)

# Globais
camera = None
scene = None
shader = None
shadow_shader = None
plane_shader = None
plane_vao = None
plane_vbo = None

def main_shadows():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    win = glfw.create_window(800, 600, "Sombras Planares com Cubo", None, None)
    if not win:
        glfw.terminate()
        return

    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)
    glfw.swap_interval(1)

    print("OpenGL version: ", glGetString(GL_VERSION).decode())

    initialize_shadows(win)

    while not glfw.window_should_close(win):
        display_shadows(win)
        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

def initialize_shadows(win):
    global camera, scene, shader, shadow_shader, plane_shader, plane_vao, plane_vbo

    glClearColor(0.8, 0.8, 0.8, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Camera e arcball
    camera = Camera3D(viewer_pos.x, viewer_pos.y, viewer_pos.z)
    arcball = camera.CreateArcball()
    arcball.Attach(win)

    # Luz
    light = Light(light_pos.x, light_pos.y, light_pos.z, 1.0, "world")

    # Material do cubo (verde esmeralda)
    emerald_green = Material(0.1, 0.8, 0.5)

    # Shader do cubo (iluminação)
    shader = Shader(light, "camera")
    shader.AttachVertexShader("shaders/vertex.glsl")
    shader.AttachFragmentShader("shaders/fragment.glsl")
    shader.Link()

    # Shader do plano
    plane_shader = Shader()
    plane_shader.AttachVertexShader("shaders/plane_vertex.glsl")
    plane_shader.AttachFragmentShader("shaders/plane_fragment.glsl")
    plane_shader.Link()

    # Shader simples para sombra (sem iluminação, cor preta/cinza escura com alfa)
    shadow_shader = Shader()
    shadow_shader.AttachVertexShader("shaders/simple_vertex.glsl")
    shadow_shader.AttachFragmentShader("shaders/simple_fragment.glsl")
    shadow_shader.Link()

    # Cena: Node com transform e cubo
    transform = Transform()
    transform.Scale(0.5, 0.5, 0.5)
    transform.Translate(-1.0, 0.5, 0.0)  # Base do cubo em Y = 0.5 - 0.25 = 0.25
    cube = Cube()

    root = Node(shader, nodes=[
        Node(None, transform, [emerald_green], [cube])
    ])
    scene = Scene(root)

    # Plano Y=0 (grande)
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

    # position attribute at location 0 (consoante plane_vertex.glsl)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

def display_shadows(win):
    global scene, camera

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 1. Renderizar o plano (chão) com Depth Offset
    render_plane()

    # 2. Renderizar a sombra (com blending)
    render_shadow()

    # 3. Renderizar a cena original (cubo iluminado)
    render_scene()

def create_shadow_projection_matrix(plane_normal, plane_point, light_pos_vec3, light_w=1.0):
    """
    Retorna a matriz 4x4 que projeta pontos sobre o plano definido por (plane_normal, plane_point).
    """
    # coeficientes do plano ax + by + cz + d = 0
    A = plane_normal.x
    B = plane_normal.y
    C = plane_normal.z
    D = - (A * plane_point.x + B * plane_point.y + C * plane_point.z)

    # vetor plano (A,B,C,D)
    plane = glm.vec4(A, B, C, D)

    # luz em homogêneo (x,y,z,w)
    L = glm.vec4(light_pos_vec3.x, light_pos_vec3.y, light_pos_vec3.z, light_w)

    # dot = plane . L
    dot = glm.dot(plane, L)

    # Constroi S pelo formula: S = dot * I - L * plane^T
    S = glm.mat4(0.0)

    for col in range(4):
        for row in range(4):
            I_cr = 1.0 if col == row else 0.0
            S[col][row] = dot * I_cr - L[col] * plane[row]

    return S

def render_shadow():
    global scene, shadow_shader, light_pos, camera

    st = State(camera)

    # Preparar GL para desenhar sombra sobre o plano:
    glDepthMask(GL_FALSE) # Não escrever no depth buffer
    glDisable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    shadow_shader.Load(st)

    # --- MATRIZ DE PROJEÇÃO DE SOMBRA ---
    plane_normal = glm.vec3(0.0, 1.0, 0.0)
    plane_point = glm.vec3(0.0, 0.0, 0.0) 
    
    # Vetor de luz direcional para projeção ortogonal (sombra exatamente abaixo)
    shadow_light_dir = glm.vec3(0.0, 1.0, 0.0)
    
    # S = Matriz de Projeção Ortogonal (light_w=0.0)
    S = create_shadow_projection_matrix(plane_normal, plane_point, shadow_light_dir, light_w=0.0) 
    
    trf = scene.root.nodes[0].trf
    cube_mesh = scene.root.nodes[0].shps[0]
    M = trf.GetMatrix() 
    
    V = camera.GetViewMatrix()
    P = camera.GetProjMatrix()

    # ✅ CORREÇÃO: Removemos o T_epsilon (epsilon push) para evitar o Z-fighting via GL_POLYGON_OFFSET
    M_final = M
    
    # Mvp_sombra = P * V * S * M_final
    shadow_model_matrix = S * M_final
    shadow_mvp_matrix = P * V * shadow_model_matrix
    
    current_shader = st.GetShader()
    current_shader.SetUniform("Mvp", shadow_mvp_matrix)

    # Desenhar o mesh (cubo)
    cube_mesh.Draw(st)

    # Restaurar GL state
    shadow_shader.Unload(st)
    glDisable(GL_BLEND)
    glDepthMask(GL_TRUE)
    glEnable(GL_CULL_FACE)

def render_plane():
    global plane_shader, plane_vao, camera
    plane_shader.UseProgram()
    model_matrix = glm.mat4(1.0)
    vp_matrix = camera.GetProjMatrix() * camera.GetViewMatrix()
    mvp_matrix = vp_matrix * model_matrix
    plane_shader.SetUniform("Mvp", mvp_matrix)

    # 🎯 CORREÇÃO: Habilitar o Polygon Offset para empurrar o plano para trás no depth buffer
    # Isto garante que a sombra (em Y=0) seja renderizada *na frente* do plano (também em Y=0)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(1.0, 1.0)
    
    glDisable(GL_CULL_FACE)
    glBindVertexArray(plane_vao)
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
    glBindVertexArray(0)
    glEnable(GL_CULL_FACE)
    
    # Desabilitar o Polygon Offset
    glDisable(GL_POLYGON_OFFSET_FILL)

def render_scene():
    # Renderiza cubo com iluminação normal
    scene.Render(camera)

def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)

if __name__ == "__main__":
    main_shadows()