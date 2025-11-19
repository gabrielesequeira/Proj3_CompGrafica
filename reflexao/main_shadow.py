import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import numpy as np
import glm # Necessário para glm.mat4 e glm.vec4
from camera3d import *
from light import *
from shader import *
from material import *
from transform import *
from node import *
from scene import *
from cube import * # Posição da câmera (ligeiramente ajustada para um novo ângulo)
viewer_pos = glm.vec3(3.0, 4.0, 5.0) 

# --- Variáveis Globais Adicionadas para Sombras ---

# Posição da luz (Fonte de luz pontual)
# Vamos usar uma posição acima e ligeiramente deslocada do objeto
light_pos = glm.vec4(5.0, 10.0, 5.0, 1.0) # Luz direcional se w=0, pontual se w=1

# Coeficientes do plano (ax + by + cz + d = 0). O plano y=0 é (0, 1, 0, 0)
# A = 0, B = 1, C = 0, D = 0
plane_coeffs = glm.vec4(0.0, 1.0, 0.0, 0.0) 

# --- Fim das Variáveis Globais Adicionadas ---


def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    win = glfw.create_window(800, 600, "Sombras Planares por Matriz de Projeção", None, None)
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
    global camera, scene, shader, plane_shader, plane_vao, plane_vbo, light

    # Nova cor de fundo: Cinza claro (0.8, 0.8, 0.8, 1.0)
    glClearColor(0.8, 0.8, 0.8, 1.0) 
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    # glDisable(GL_STENCIL_TEST) # Desabilitamos Stencil Buffer para Sombras

    camera = Camera3D(viewer_pos[0], viewer_pos[1], viewer_pos[2])
    arcball = camera.CreateArcball()
    arcball.Attach(win)

    # A luz agora é a fonte da sombra
    light = Light(light_pos[0], light_pos[1], light_pos[2], 1.0, "world") 
    
    # Novo material: Verde Esmeralda (0.1, 0.8, 0.5)
    emerald_green = Material(0.1, 0.8, 0.5) 

    # Shader principal para o objeto iluminado
    shader = Shader(light, "world")
    shader.AttachVertexShader("shaders/vertex.glsl")
    shader.AttachFragmentShader("shaders/fragment.glsl")
    shader.Link()

    # Shader para o plano e para a sombra (sem iluminação, cor simples)
    plane_shader = Shader()
    plane_shader.AttachVertexShader("shaders/plane_vertex.glsl")
    plane_shader.AttachFragmentShader("shaders/plane_fragment.glsl")
    plane_shader.Link()

    transform = Transform()
    transform.Scale(0.5, 0.5, 0.5) 
    transform.Translate(-1.0, 0.5, 0.0) 
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

# --- Funções Adicionais para Sombra ---

def computeShadowMatrix(plane_coeffs, light_pos):
    """
    Calcula a matriz de projeção de sombra.
    Baseada em: M = L' * P - D * I
    Onde: L = Posição da Luz (light_pos)
          P = Coeficientes do Plano (plane_coeffs)
          D = Produto escalar P . L
          I = Matriz Identidade
    """
    L = light_pos
    P = plane_coeffs
    
    # D = P . L (Produto escalar)
    D = P.x * L.x + P.y * L.y + P.z * L.z + P.w * L.w
    
    # Inicializa a matriz de identidade I
    I = glm.mat4(1.0)
    
    # Inicializa a matriz L_P (L' * P)
    L_P = glm.mat4(1.0)

    # Coluna 0 da matriz L_P:
    L_P[0][0] = L.x * P.x
    L_P[0][1] = L.x * P.y
    L_P[0][2] = L.x * P.z
    L_P[0][3] = L.x * P.w

    # Coluna 1 da matriz L_P:
    L_P[1][0] = L.y * P.x
    L_P[1][1] = L.y * P.y
    L_P[1][2] = L.y * P.z
    L_P[1][3] = L.y * P.w

    # Coluna 2 da matriz L_P:
    L_P[2][0] = L.z * P.x
    L_P[2][1] = L.z * P.y
    L_P[2][2] = L.z * P.z
    L_P[2][3] = L.z * P.w

    # Coluna 3 da matriz L_P:
    L_P[3][0] = L.w * P.x
    L_P[3][1] = L.w * P.y
    L_P[3][2] = L.w * P.z
    L_P[3][3] = L.w * P.w

    # Matriz final: M = L_P - D * I
    # A biblioteca glm facilita:
    shadow_matrix = L_P - I * D 

    return shadow_matrix


def renderPlane():
    """Desenha o plano receptor de sombra (chão)."""
    plane_shader.UseProgram()

    # Model Matrix do plano é identidade (já está na origem)
    model_matrix = glm.mat4(1.0) 
    vp_matrix = camera.GetProjMatrix() * camera.GetViewMatrix()
    mvp_matrix = vp_matrix * model_matrix
    
    # Passamos a MVP (Model-View-Projection) para o shader do plano
    plane_shader.SetUniform("Mvp", mvp_matrix) 

    glDisable(GL_CULL_FACE)
    glBindVertexArray(plane_vao)
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
    glBindVertexArray(0)
    glEnable(GL_CULL_FACE)


def renderObject(is_lit=True):
    """
    Desenha o objeto (Cubo).
    is_lit=True: Objeto real com iluminação
    is_lit=False: Sombra (usando cor escura)
    """
    global scene
    scene.Render(camera) # Renderiza o objeto (cubo) com o shader e materiais definidos


def renderShadow(shadow_matrix):
    """
    Renderiza o objeto projetado como sombra.
    Usa a matriz de sombra e uma cor escura, desabilitando a iluminação.
    """
    global scene, shader, camera
    
    # 1. Habilitar Blend (para suavização/transparência da sombra)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # 2. Desabilitar Iluminação para a Sombra
    # Assumindo que seu 'fragment.glsl' usa uma uniform para ligar/desligar iluminação ou cor
    shader.UseProgram()
    # Se você não tem um uniform 'is_shadow', a alternativa é usar um shader simples de cor sólida
    # Caso não seja possível, vamos usar a cena padrão, mas forçar uma cor preta (ou escura) e blending
    
    # 3. Z-Fighting: Habilitar o deslocamento de polígonos
    # Garante que a sombra fique LIGEIRAMENTE abaixo do plano, evitando z-fighting
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(-1.0, -1.0) # Valores negativos para mover na direção da câmera

    # 4. Renderizar a cena aplicando a matriz de sombra na Model Matrix
    scene.Render(camera, override_model_matrix=shadow_matrix, is_shadow=True) 
    # **Nota:** O 'scene.Render' deve ser adaptado para aceitar e aplicar a 'shadow_matrix'
    # no Model-View-Projection (MVP) dentro do shader, e para usar a flag 'is_shadow'
    # para forçar a cor (ex: preto) e desabilitar iluminação.
    
    # 5. Restaurar estados
    glDisable(GL_POLYGON_OFFSET_FILL)
    glDisable(GL_BLEND)


def display(win):
    global scene, camera

    # Limpa os buffers de cor e profundidade
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Calcula a matriz de sombra
    shadow_matrix = computeShadowMatrix(plane_coeffs, light_pos)

    # --- Sequência de Renderização ---

    # 1. Desenhar o plano receptor (chão)
    # A cor e textura do plano são definidas em 'plane_fragment.glsl'
    renderPlane()
    
    # 2. Desenhar a sombra projetada
    # Deve ser desenhada APÓS o plano para que o Z-Buffer a mantenha no plano
    renderShadow(shadow_matrix)

    # 3. Desenhar o objeto real com iluminação
    # Deve ser desenhado POR ÚLTIMO para garantir que esteja acima da sombra e do plano
    # Desabilitamos o culling reverso da sombra para evitar problemas
    glDisable(GL_CULL_FACE)
    renderObject(is_lit=True)
    glEnable(GL_CULL_FACE)
    

def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)

if __name__ == "__main__":
    main()